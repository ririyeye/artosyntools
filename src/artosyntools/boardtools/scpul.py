import asyncssh


class scpdls(object):

    def __init__(self, conn: asyncssh.SSHClientConnection, fname: str, remotename: str = '/tmp/update'):
        self.fname = fname
        self.conn = conn
        self.remotename = remotename

    async def tryupload(self):

        def cb(local_file, remote_file, sent, total):
            percent = format(sent / total * 100, '.2f') + '%'
            print("\rcopy ", local_file, percent, end="")

        await asyncssh.scp(self.fname, (self.conn, self.remotename), progress_handler=cb)
        print('\n')
