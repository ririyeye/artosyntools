import asyncssh
from .execline import *
from .scpul import *
from .httpul import *

remotePath = '/tmp/artoupdate'


async def rebootcmd_ssh(conn):
    await execlines(
        conn,
        "#!/bin/sh \n "
        "export LD_LIBRARY_PATH=/lib:/usr/lib:/local/lib:/local/usr/lib:$LD_LIBRARY_PATH \n"
        "export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/local/bin/:/local/usr/bin/:/local/usr/sbin:$PATH \n"
        "mount /dev/mtdblock14 /local"
        "cp /local/usr/bin/ar_wdt_service /tmp \n "
        "/tmp/ar_wdt_service -t 1 & \n "
        # "sleep 1  \n "
        "devmem 0x606330b4 32 0x04912028 \n"
        "echo 15 > /sys/class/gpio/export \n"
        "echo \"out\" > /sys/class/gpio/gpio15/direction \n "
        "echo 0 > /sys/class/gpio/gpio15/value \n"
        "ps \n "
        "killall ar_wdt_service \n ")


async def set_updateflg_and_reboot(conn: asyncssh.SSHClientConnection):
    print(conn._host + "normal mode , need reboot")
    await execlines(conn, "touch /local/sirius-clean-system-flag")
    await execlines(conn, "sync")

    print("reboot " + conn._host)
    await rebootcmd_ssh(conn)


async def if_scp_ok(conn: asyncssh.SSHClientConnection):
    ret = await execlines(conn, "scp", usestderr=True)
    try:
        ret.index("not found\n")
        return False
    except ValueError as e:
        pass

    return True

    # return await execlines(conn, "echo $PATH")


async def upload_file(conn: asyncssh.SSHClientConnection, localfile: str, remotefile: str):
    # 首选scp
    # ifscp = await if_scp_ok(conn)
    # if ifscp:
    #     return await scpulfile(conn, localfile, remotefile)

    return await httpulfile(conn, localfile, remotefile)

async def updatecmd(conn: asyncssh.SSHClientConnection,file:str):
    print(conn._host + " try update")

    await execlines(conn, "artosyn_upgrade " + file, showlines=True)

    print(conn._host + " update ok")

async def _update_firm(ip, port, config, updatefile: str, callback=None):
    async with asyncssh.connect(host=ip,
                                port=port,
                                username=config['username'],
                                password=config['password'],
                                known_hosts=None,
                                config=None,
                                server_host_key_algs=['ssh-rsa']) as conn:
        sn = await getsn(conn)
        normalsta = await is_normal_sta(conn)

        if normalsta:
            try:
                await set_updateflg_and_reboot(conn)
            except ConnectionAbortedError as e:
                pass
            return sn, False
        else:
            ret = await upload_file(conn, updatefile, remotePath)
            if not ret:
                return sn, False

        await updatecmd(conn, remotePath)

        return sn, True





async def update_firm(ip, port, config, updatefile: str, callback=None):
    sn, sta = await _update_firm(ip, port, config, updatefile)
    if not sta:
        if callback:
            callback(ip, port, config, sn, sta)
        return
