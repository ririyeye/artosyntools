import asyncssh
import aiohttp
import random
from aiohttp import web

class httpuls(object):

    def __init__(self, conn: asyncssh.SSHClientConnection, fname: str, remotename: str = '/tmp/update'):
        self.fname = fname
        self.conn = conn
        self.remotename = remotename

    async def handle(self, request):
        name = request.match_info.get('name', "Anonymous")
        wf = web.FileResponse(path=self.fname)
        return wf

    async def runweb(self) -> int:
        app = web.Application()
        app.add_routes([web.get('/', self.handle), web.get('/{name}', self.handle)])

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        for i in range(10):
            port = random.randint(10000, 20000)
            try:
                self.site = web.TCPSite(self.runner, "0.0.0.0", port=port)
                await self.site.start()
                print("start ok!! , port = {0}".format(port))
                return port
            except OSError as e:
                print("bind error , port = {0}".format(port))
                if i == 9:
                    raise

    async def tryupload(self):
        port = await self.runweb()
        await self.conn.run("cd /tmp;ls /tmp")
        localaddr = self.conn._local_addr
        cmd = "wget http://{0}:{1}/123 -O {2}".format(localaddr, port, self.remotename)
        result = await self.conn.run(cmd)
        await self.site.stop()
        await self.runner.shutdown()