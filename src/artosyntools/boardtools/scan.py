import asyncio
import asyncssh
from typing import List
from socket import error as socket_error
import errno


class ssh_scanner(object):

    def __init__(self, ips, ports, configs, timeout, callback=None, loopflg=False) -> None:
        """
        @type callback: function(string, int, dict)
        """
        self.ips = ips
        self.ports = ports
        self.configs = configs
        self.timeout = timeout
        self.callback = callback
        self.loopmode = loopflg
        self.loopflg = loopflg
        self.rescan_interval = 5
        self.debugflg = False
        self.loop = asyncio.get_event_loop()

        self.scan_tasks = []
        self.output = []

    async def trysshconnect(self, ip, port, config: dict, timeoutpoint):
        try:
            async with asyncio.timeout_at(timeoutpoint) as cm:
                async with asyncssh.connect(host=ip,
                                            port=port,
                                            username=config['username'],
                                            password=config['password'],
                                            known_hosts=None,
                                            config=None,
                                            server_host_key_algs=['ssh-rsa']) as conn:

                    if self.debugflg:
                        print("{}:{} ssh Connected".format(ip, port))
                    if self.callback:
                        self.callback(ip, port, config)
                    else:
                        self.output.append((ip, port, config))

                    return
        except asyncio.TimeoutError as e1:
            pass
        except asyncssh.ConnectionLost as e2:
            pass
        except ConnectionResetError as e3:
            print("ConnectionResetError")
        except asyncssh.PermissionDenied as e4:
            pass

    async def tcp_connect(self, ip, port):
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            writer.close()
            await writer.wait_closed()

            return True

        except socket_error as serr:
            if serr.errno != errno.EINVAL:
                print('Error {}:{} {}'.format(ip, port, serr))
            return False

    async def scanner(self, ip, port):
        leftsecond = self.timeout
        timoutpoint = self.loop.time() + self.timeout

        try:
            async with asyncio.timeout_at(timoutpoint):
                ret = await self.tcp_connect(ip, port)
                if not ret:
                    return

            if self.debugflg:
                print("{}:{} port Connected".format(ip, port))

            tasks = [asyncio.create_task(self.trysshconnect(ip, port, config, timoutpoint)) for config in self.configs]

            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in tasks:
                if not task.done():
                    task.cancel()
            if not self.loopmode:
                self.port_res.cancel()
            return

        except asyncio.TimeoutError as e:
            pass

    async def loop_scanner(self, ip, port):
        while True:
            await self.scanner(ip, port)

            if not self.loopflg:
                return

            await asyncio.sleep(self.rescan_interval)

    async def wait_scans(self):
        self.scan_tasks = [asyncio.create_task(self.scanner(ip, port)) for port in self.ports for ip in self.ips]

        self.port_res = asyncio.gather(*self.scan_tasks)
        try:
            await asyncio.wait_for(self.port_res, timeout=self.timeout)
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass

        return self.output

    def create_loop_scan(self):
        for port in self.ports:
            for ip in self.ips:
                self.scan_tasks += [asyncio.create_task(self.loop_scanner(ip, port))]

    async def stop_scan(self, forceflg=False):
        print("stop start")
        self.loopflg = False

        if forceflg:
            for task in self.scan_tasks:
                if not task.done():
                    task.cancel()
        else:
            await asyncio.gather(*self.scan_tasks)
        print("stop ok")


async def sshscan_any(ips: list[str], ports, configs: list[dict], timeout: int) -> list[(str, str, dict)]:
    s = ssh_scanner(
        ips,
        ports,
        configs,
        timeout,
    )
    return await s.wait_scans()


async def start_loop_scan(ips: list[str], ports, configs: list[dict], timeout: int, callback) -> ssh_scanner:
    s = ssh_scanner(ips, ports, configs, timeout, callback=callback, loopflg=True)
    s.create_loop_scan()
    return s
