from contextlib import suppress
from enum import IntEnum, auto
from functools import partial
from ipaddress import ip_address
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from pathlib import Path
from socket import socket, SOCK_STREAM, AF_INET, gethostbyname
from threading import Lock
from typing import Match, AnyStr, Set, Collection

from maxminddb.types import RecordDict
from requests import Session
from socks import socksocket, SOCKS4, SOCKS5, HTTP
from yarl import URL

from PyRoxy import GeoIP, Tools
from PyRoxy.Exceptions import ProxyInvalidHost, ProxyInvalidPort, ProxyParseError
from PyRoxy.Tools import Patterns


class ProxyType(IntEnum):
    HTTP = auto()
    HTTPS = auto()
    SOCKS4 = auto()
    SOCKS5 = auto()

    def asPySocksType(self):
        return SOCKS5 if self == ProxyType.SOCKS5 else \
            SOCKS4 if self == ProxyType.SOCKS4 else \
                HTTP

    @staticmethod
    def stringToProxyType(n: str):
        return ProxyType.HTTP if not (n.isdigit() and not (int(n) == 1)) else \
            int(n) if int(n) in PRINTABLE_PROXY_TYPES else \
                ProxyType.SOCKS5 if int(n) == 5 else \
                    ProxyType.SOCKS4 if int(n) == 4 else \
                        ProxyType.HTTP


PROXY_TYPES = {"SOCKS4": ProxyType.SOCKS4, "SOCKS5": ProxyType.SOCKS5, "HTTP": ProxyType.HTTP, "HTTPS": ProxyType.HTTPS}
PRINTABLE_PROXY_TYPES = dict(zip(PROXY_TYPES.values(), PROXY_TYPES.keys()))


class Proxy(object):
    user: AnyStr | None
    password: AnyStr | None
    country: AnyStr | RecordDict | None
    port: int
    type: ProxyType
    host: AnyStr

    def __init__(self, host: str, port: int = 0, proxy_type: ProxyType = ProxyType.HTTP, user=None, password=None):
        if Patterns.URL.match(host): host = gethostbyname(host)
        assert self.validate(host, port)
        self.host = host
        self.type = proxy_type
        self.port = port
        self.country = GeoIP.get(host)
        if self.country: self.country = self.country["registered_country"]["iso_code"]
        self.user = user or None
        self.password = password or None

    def __str__(self):
        return "%s://%s:%d%s" % (self.type.name.lower(), self.host, self.port, ("%s:%s" % (self.user, self.password)
                                                                                if self.password and self.user else ""))

    def __repr__(self):
        return "<Proxy %s:%d>" % (self.host, self.port)

    @staticmethod
    def fromString(string: str):
        with suppress(KeyboardInterrupt):
            proxy: Match[str] | None = Patterns.Proxy.search(string)
            return Proxy(proxy.group(1),
                         int(proxy.group(2)) if proxy.group(3) and proxy.group(2).isdigit() else 80,
                         ProxyType.stringToProxyType(proxy.group(1)),
                         proxy.group(3),
                         proxy.group(4))
        raise ProxyParseError("'%s' is an Invalid Proxy URL" % string)

    def ip_port(self):
        return "%s:%d" % (self.host, self.port)

    @staticmethod
    def validate(host: str, port: int):
        with suppress(ValueError):
            if not ip_address(host):
                raise ProxyInvalidHost(host)
            if not Tools.Patterns.Port.match(str(port)):
                raise ProxyInvalidPort(port)
            return True
        raise ProxyInvalidHost(host)

    # noinspection PyShadowingBuiltins
    def open_socket(self, family=AF_INET, type=SOCK_STREAM, proto=-1, fileno=None):
        return ProxySocket(self, family, type, proto, fileno)

    def wrap(self, sock: socket | Session):
        if isinstance(sock, socket):
            return self.open_socket(sock.family, sock.type, sock.proto, sock.fileno())
        sock.proxies = self.asRequest()
        return sock

    def asRequest(self):
        return {"http": self.__str__()}

    # noinspection PyUnreachableCode
    def check(self, url: str | URL = "https://httpbin.org/get", timeout=5):
        if not isinstance(url, URL): url = URL(url)
        with suppress(KeyboardInterrupt):
            with self.open_socket() as sock:
                sock.settimeout(timeout)
                return sock.connect((url.host, url.port or 80))
        return False


# noinspection PyShadowingBuiltins
class ProxySocket(socksocket):
    def __init__(self, proxy: Proxy, family=-1, type=-1, proto=-1, fileno=None):
        super().__init__(family, type, proto, fileno)
        if proxy.port:
            if proxy.user and proxy.password:
                self.setproxy(proxy.type.asPySocksType(), proxy.host, proxy.port, username=proxy.user,
                              password=proxy.password)
                return
            self.setproxy(proxy.type.asPySocksType(), proxy.host, proxy.port)
            return
        if proxy.user and proxy.password:
            self.setproxy(proxy.type.asPySocksType(), proxy.host, username=proxy.user,
                          password=proxy.password)
            return
        self.setproxy(proxy.type.asPySocksType(), proxy.host)


class ProxyChecker:
    result: Set[Proxy]
    out_lock: Lock

    def __init__(self):
        self.out_lock = Lock()
        self.result = set()

    def check(self, proxy: Proxy, url: str | URL = "https://httpbin.org/get", timeout=5):
        with suppress(Exception), self.out_lock:
            if proxy.check(url, timeout):
                self.result.add(proxy)

    def checkAll(self, proxies: Collection[Proxy], url: str | URL = "https://httpbin.org/get", timeout=5, threads=1000):
        with Pool(max(round(len(proxies) / cpu_count()), threads)) as pool:
            pool.map(partial(self.check, url=url, timeout=timeout), proxies)


class ProxyUtiles:
    @staticmethod
    def parseAll(proxies: Collection[str]) -> Set[Proxy]:
        return set(map(Proxy.fromString, proxies))

    @staticmethod
    def parseAllIPPort(proxies: Collection[str], ptype: ProxyType=ProxyType.HTTP) -> Set[Proxy]:
        resu = set()
        for pr in proxies:
            pr = Patterns.IPPort.search(pr)
            if not pr: continue
            resu.add(Proxy(pr.group(1), int(pr.group(2)), ptype))
        return resu

    @staticmethod
    def readFromFile(path: Path | str) -> Set[Proxy]:
        if isinstance(path, Path):
            with path.open("r+") as read:
                lines = read.readlines()
        else:
            with open(path, "r+") as read:
                lines = read.readlines()

        return ProxyUtiles.parseAll([prox.strip() for prox in lines])
    @staticmethod
    def readIPPortFromFile(path: Path | str) -> Set[Proxy]:
        if isinstance(path, Path):
            with path.open("r+") as read:
                lines = read.readlines()
        else:
            with open(path, "r+") as read:
                lines = read.readlines()

        return ProxyUtiles.parseAllIPPort([prox.strip() for prox in lines])
