__all__ = ["ProxyInvalidHost", "ProxyInvalidPort", "ProxyParseError"]


class ProxyParseError(Exception):
    pass


class ProxyInvalidPort(ProxyParseError):

    def __init__(self, port: int):
        ProxyParseError.__init__(
            self, "'%d' is too %s" % (port, "small" if port < 1 else "long"))


class ProxyInvalidHost(ProxyParseError):

    def __init__(self, host: str):
        ProxyParseError.__init__(self, "'%s' is an Invalid IP Address" % host)
