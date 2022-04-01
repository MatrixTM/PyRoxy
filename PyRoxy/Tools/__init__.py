from re import compile, IGNORECASE, MULTILINE
from contextlib import suppress
from os import urandom
from socket import inet_ntop, inet_ntoa, AF_INET6
from string import ascii_letters
from struct import pack
from struct import pack as data_pack
from sys import maxsize
from typing import Callable, Any, List

__all__ = ["Patterns", "Random"]


class Random:
    latters: List[str] = list(ascii_letters)
    rand_str: Callable[[int], str] = lambda length=16: ''.join(
        Random.rand_choice(*Random.latters) for _ in range(length))
    rand_char: Callable[[int], chr] = lambda length=16: "".join(
        [chr(Random.rand_int(0, 1000)) for _ in range(length)])
    rand_ipv4: Callable[[], str] = lambda: inet_ntoa(
        data_pack('>I', Random.rand_int(1, 0xffffffff)))
    rand_ipv6: Callable[[], str] = lambda: inet_ntop(
        AF_INET6, pack('>QQ', Random.rand_bits(64), Random.rand_bits(64)))
    rand_int: Callable[[int, int],
                       int] = lambda minimum=0, maximum=maxsize: int(
                           Random.rand_float(minimum, maximum))
    rand_choice: Callable[[List[Any]], Any] = lambda *data: data[
        (Random.rand_int(maximum=len(data) - 2) or 0)]
    rand: Callable[
        [], int] = lambda: (int.from_bytes(urandom(7), 'big') >> 3) * (2**-53)

    @staticmethod
    def rand_bits(maximum: int = 255) -> int:
        numbytes = (maximum + 7) // 8
        return int.from_bytes(urandom(numbytes),
                              'big') >> (numbytes * 8 - maximum)

    @staticmethod
    def rand_float(minimum: float = 0.0,
                   maximum: float = (maxsize * 1.0)) -> float:
        with suppress(ZeroDivisionError):
            return abs((Random.rand() * maximum) % (minimum -
                                                    (maximum + 1))) + minimum
        return 0.0


class Patterns:
    Port = compile(
        "^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]"
        "{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$")
    IP = compile("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
    IPPort = compile("^((?:\d{1,3}\.){3}\d{1,3}):(\d{1,5})$")
    Proxy = compile(
        r"^(?:\[|)(?:\s+|)((?:socks[45]|http(?:s|)))(?:[]|]|)(?:\s+|)(?:](?:\s+|)|\|(?:\s+|)|://(?:\s+|)|)"
        r"((?:(?:\d+.){3}\d+|\S+[.]\w{2,3}))"
        r"(?:[:]|)((?:\d+|))"
        r"(?::(.+):(.+)|)$", IGNORECASE | MULTILINE)
    URL = compile("\S+[.]\w{2,3}")
