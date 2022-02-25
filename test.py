from PyRoxy import Proxy, ProxyType, ProxyUtiles, ProxyChecker

if __name__ == '__main__':
    ps= ProxyUtiles.readIPPortFromFile("test.txt")
    print(ps)
    # pc = ProxyChecker()
    # pc.checkAll(ps)
    # ps = pc.result
    # print(ps)