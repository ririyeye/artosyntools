import asyncio, os
import artosyntools
import json


class close_cb(object):

    def __init__(self):
        self.completed_num = 0

    def set_scan_obj(self, scan: artosyntools.ssh_scanner):
        self.scan = scan

    def scan_cb(self, ip, port, config, sn, normalsta):
        print("get once = {},{},{}-{},sn={}".format(ip, port, config['username'], config['password'], sn))
        self.completed_num += 1
        if self.completed_num == 4:
            if self.scan:
                asyncio.create_task(self.scan.stop_scan(True))


def getjson(file):
    with open(file) as f:
        return json.load(f)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ret = None

    js = getjson('tests/cfg.json')

    configs = artosyntools.get_user_pass(js)

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