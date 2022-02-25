from PyRoxy import Proxy, ProxyType, ProxyUtiles, ProxyChecker

if __name__ == '__main__':
    ps= ProxyUtiles.readFromFile("test.txt")
    for p in ps:
        print(str(p))
    # pc = ProxyChecker()
    # pc.checkAll(ps)
    # ps = pc.result
    # print(ps)