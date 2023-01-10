import asyncssh, io


async def execlines(conn: asyncssh.SSHClientConnection, lines: str, showlines=False, usestderr=False) -> str:
    async with conn.create_process(
            "#!/bin/sh \n "
            "export LD_LIBRARY_PATH=/lib:/usr/lib:/local/lib:/local/usr/lib:$LD_LIBRARY_PATH \n"
            "export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/local/bin/:/local/usr/bin/:/local/usr/sbin:$PATH \n" + lines +
            "\n") as process:
        with io.StringIO() as outline:
            async for line in process.stdout:
                outline.write(line)
                if showlines == True:
                    print(line)

            outstr = outline.getvalue()
            async for line in process.stderr:
                if usestderr:
                    outline.write(line)
                if showlines == True:
                    print(line)

            return outline.getvalue()


async def getsn(conn: asyncssh.SSHClientConnection):
    return await execlines(conn, "cat /factory/productsn")


async def is_normal_sta(conn: asyncssh.SSHClientConnection):
    testcmd = ["ps | grep p301d | grep -v grep | wc -l", "ps | grep \"run.sh nor mtdblock15\" | grep -v grep | wc -l"]

    rets = []
    for cmd in testcmd:
        ps = await execlines(conn, cmd)
        retcode = int(ps[0].strip('\n'))
        rets.append(retcode)

    for ret in rets:
        if ret == 1:
            return True

    return False
