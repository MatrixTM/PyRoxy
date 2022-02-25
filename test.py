from PyRoxy import ProxyUtiles, ProxyChecker

if __name__ == '__main__':
    ps = ProxyUtiles.readFromFile("test.txt")
    pc = ProxyChecker.checkAll(ps)
    print(pc)
