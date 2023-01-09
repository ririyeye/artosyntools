import asyncssh, io


async def execlines(conn: asyncssh.SSHClientConnection, lines: str, showlines=False) -> str:
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

            return outline.getvalue()