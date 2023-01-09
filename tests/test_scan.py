import asyncio,os
import artosyntools

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    configs = [{'username': 'root', 'password': 'artosyn'}]

    ips = ["192.168.10.{}".format(i) for i in range(1, 255)]
    ports = [22, 80, 443, 8080]
    timeout = 20
    s = artosyntools.ssh_scanner(ips, ports, configs)
    results = loop.run_until_complete(s.sshscan(timeout))
    for res in results:
        print("{}:{} [{}:{}] is ok!".format(res[0], res[1], res[2]['username'], res[2]['password']))
    os.system("pause")