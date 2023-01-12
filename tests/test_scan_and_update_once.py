import asyncio, os
import artosyntools
import json
import logging
import asyncssh

use_rtos = True

frim_file = "tests/artosyn-upgrade-sirius-0.0.0.1.img"
rtos_file = "tests/a7_rtos.nonsec.img"

if use_rtos:
    testfile = rtos_file
else:
    testfile = frim_file


class update_exec(object):

    def __init__(self):
        self.succ_sn_list = []
        self.lock_sn_list = []

    def set_scan_obj(self, scan: artosyntools.ssh_scanner):
        self.scan = scan

    def update_cb(self, ip, port, config, sn, sta):
        print("update cb {},{},{}-{},sn={},sta = {}".format(ip, port, config['username'], config['password'], sn, sta))

        self.lock_sn_list.remove(sn)
        if sta:
            # update succ add sn in succ
            if not sn in self.succ_sn_list:
                self.succ_sn_list.append(sn)

    def scan_cb(self, ip, port, config, sn, normalsta):
        # print("get once = {},{},{}-{},sn={}".format(ip, port, config['username'], config['password'], sn))

        if sn in self.succ_sn_list:
            print("sn={} has updated".format(sn))
            return

        if sn in self.lock_sn_list:
            print("sn={} has locked".format(sn))
            return

        self.lock_sn_list.append(sn)
        if use_rtos:
            asyncio.create_task(artosyntools.update_rtos(ip, port, config, testfile, self.update_cb))
        else:
            asyncio.create_task(artosyntools.update_firm(ip, port, config, testfile, self.update_cb))


def getjson(file):
    with open(file) as f:
        return json.load(f)


if __name__ == "__main__":
    asyncssh.set_debug_level(3)
    logging.basicConfig(level=logging.INFO,
                        filename='./log.txt',
                        filemode='w',
                        datefmt='%a %d %b %Y %H:%M:%S',
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ret = None

    js = getjson('tests/cfg.json')

    loop.run_until_complete(
        artosyntools.ftp_dl_file(host=js['ftp']['ip'],
                                 cwd=js['ftp']['workpath'],
                                 usr=js['ftp']['usr'],
                                 password=js['ftp']['pw'],
                                 filename=os.path.basename(testfile),
                                 localfile=testfile))

    configs = artosyntools.get_user_pass(js)

    ips = ["192.168.10.{}".format(i) for i in range(1, 255)]
    ips += ["192.168.1.{}".format(i) for i in range(1, 255)]
    ports = [22, 80, 443, 8080]

    ports = [22]

    timeout = 20
    c = update_exec()
    ret = loop.run_until_complete(artosyntools.start_loop_scan(ips, ports, configs, timeout, callback=c.scan_cb))
    c.set_scan_obj(ret)
    # ret.debugflg = True
    loop.run_forever()

    os.system("pause")