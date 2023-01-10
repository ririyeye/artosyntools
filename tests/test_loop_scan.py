import asyncio,os
import artosyntools

class close_cb(object):
    def __init__(self):
        self.completed_num = 0

    def set_scan_obj(self, scan: artosyntools.ssh_scanner):
        self.scan = scan

    def scan_cb(self, ip, port, config):
        print("get once = {0},{1},{2}-{3}".format(ip, port, config['username'], config['password']))
        self.completed_num += 1
        if self.completed_num == 4:
            if self.scan:
                asyncio.create_task(self.scan.stop_scan(True))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ret = None

    configs = [{'username': 'root', 'password': 'artosyn'}]

    ips = ["192.168.10.{}".format(i) for i in range(1, 255)]
    ips += ["192.168.1.{}".format(i) for i in range(1, 255)]
    ports = [22, 80, 443, 8080]

    ports = [22]

    timeout = 20
    c = close_cb()
    ret = loop.run_until_complete(artosyntools.start_loop_scan(ips, ports, configs, timeout, callback=c.scan_cb))
    c.set_scan_obj(ret)
    # ret.debugflg = True
    loop.run_forever()

    os.system("pause")