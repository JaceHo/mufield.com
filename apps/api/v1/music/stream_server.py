# Copyright (C) 1994-2010 by David Massey (davidm@msynet.com)
# See LICENSE for licensing information

import os
import socket
import select
import re
import signal
import threading

from apps.api.v1.music.mp3chunker import MP3Client, MP3Chunker
from musicfield.settings import MP3_STREAM

g_mp3chunker = None


class ServerListener:
    def __init__(self):
        self.port = 8989
        self._maxusers = 5

    def _write_header(self, sock, str):
        sock.send(str + '\r\n')

    def _write_endheaders(self, sock):
        sock.send('\r\n')

    def _send_icy_header(self, client):
        global g_mp3chunker

        self._write_header(client.sock, 'ICY 200 OK')
        self._write_header(client.sock, 'icy-name:OCXRadio. OverClocked ReMix Radio.')
        self._write_header(client.sock, 'icy-genre:Video Game.')
        self._write_header(client.sock, 'icy-url:http://www.mufield.com/mufieldradio/')
        self._write_header(client.sock, 'content-type:audio/mpeg')
        self._write_header(client.sock, 'icy-pub:0')

        if client.supportsmetadata:
            self._write_header(client.sock, 'icy-metaint:%d' % (MP3Chunker.ChunkSize))

        self._write_header(client.sock, 'icy-br:%d' % (g_mp3chunker.bitrate))
        self._write_endheaders(client.sock);

    def load(self):
        self.port = MP3_STREAM['port']
        self._maxusers = MP3_STREAM['maxusers']

    def close(self):
        pass

    def _supports_metadata(self, clienthdr):
        try:
            m = re.search('icy-metadata\:\s*(?P<enabled>\d+)', clienthdr, re.IGNORECASE)
            return m.groups('enabled')[0] == '1'
        except:
            pass
        return False

    # return a string value
    def _get_value(self, header, key):
        try:
            lines = header.splitlines()
            for l in lines:
                r = l.split(":")
                if r[0] == 'icy-' + key:
                    return r[1]
        except:
            pass
        return None

    def _get_header(self, sock, max_bytes):
        hdr = ''
        while True:
            rls, wls, xls = select.select([sock], [], [], 0.50)
            if sock not in rls:
                break

            buff = sock.recv(1024)
            if len(buff) == 0 or len(buff) >= max_bytes:
                break

            hdr += buff
            if len(hdr) >= 4 and hdr[-4:] == '\r\n\r\n':
                break

        return hdr

    def serve(self):
        global g_mp3chunker

        print('Starting MfRadio Server on port %d' % self.port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', self.port))
        s.listen(5)

        running = True
        while running:
            try:
                # TODO optimize select.epool()?
                rls, wls, xls = select.select([s], [], [], 0.50)
                if len(rls) > 0:

                    conn, addr = s.accept()

                    print("Accepted a connection from ", addr)

                    if g_mp3chunker.numusers >= self._maxusers:
                        self._write_header(conn, 'ICY 400 SERVER FULL')
                        self._write_endheaders(conn)
                        conn.close()
                    else:
                        clienthdr = self._get_header(conn, 8192)
                        if clienthdr:

                            path = self._get_value(clienthdr, 'streaming-suffix')
                            offset = int(self._get_value(clienthdr, 'streaming-offset-time'))
                            meta = self._supports_metadata(clienthdr)

                            client = MP3Client(conn, path, offset, meta)
                            self._send_icy_header(client)
                            g_mp3chunker.add_client(client)

                            print(str(g_mp3chunker.numusers) + "/" + str(self._maxusers))
                        else:
                            continue

            except KeyboardInterrupt:
                running = False

        s.close()


def start_stream():
    global g_mp3chunker
    g_mp3chunker = MP3Chunker()
    g_mp3chunker.load()
    g_mp3chunker.start()

    server = ServerListener()
    server.load()

    threading.Thread(daemon=True, target=server.serve).start()

    server.close()
    g_mp3chunker.stop()


def killpid(pidfile):
    if os.path.exists(pidfile):
        pid = open(pidfile).readline()
        print("Sending SIGTERM to pid %d" % (int(pid)))
        os.kill(int(pid), signal.SIGTERM)
        os.unlink(pidfile)
        return 0
    return 1
