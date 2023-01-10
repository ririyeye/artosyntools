import asyncssh
from ..comms import *
from .execline import *


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


async def scpulfile(conn: asyncssh.SSHClientConnection, localfile: str, remotefile: str):
    localmd5 = get_file_md5(localfile)
    h = scpdls(conn, localfile, remotefile)
    await h.tryupload()
    ret = await execlines(conn, "md5sum " + remotefile)
    getmd5 = ret.split(' ')[0]
    if localmd5 == getmd5:
        return True
    return False
