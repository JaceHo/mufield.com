# Copyright (C) 1994-2010 by David Massey (davidm@msynet.com)
# See LICENSE for licensing information

import os
import time
import select
import socket
import signal
import subprocess
import threading

from apps.api.v1.music.metadata import MP3Metadata
from musicfield import settings
from musicfield.settings import MP3_STREAM


class MP3Client:
    def __init__(self, sock, path, offset=0, meta=False):
        self.mp3data = MP3Metadata()
        # streaming mp3 file path
        self.streaming_suffix_path = path
        # streaming mp3 time offset seconds
        self.streaming_offset_time = offset
        self.supportsmetadata = meta
        self.sock = sock
        self.proc = None
        self.mp3data.load(self.trackname())
        self._metadata = self.mp3data.get_shoutcast_metadata()

    def trackname(self):
        return os.path.join(settings.MEDIA_ROOT, self.streaming_suffix_path)


class MP3Chunker(threading.Thread):
    ChunkSize = 4096

    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True
        self._clients = {}
        self._clientlock = threading.Lock()
        self._lame_exe = '/usr/bin/lame'
        self._metadata = None
        self.bitrate = 128
        self.numusers = 0

    def _lame_enc_stream(self, client):
        lfile = '%s -b %d --noreplaygain --quiet "%s" -' % (self._lame_exe, self.bitrate, client.trackname())
        proc = subprocess.Popen(lfile, shell=True, stdout=subprocess.PIPE)
        print("Streaming %s" % (client.trackname()))
        client.proc = proc
        client.bytestometadata = self.ChunkSize

    def load(self):

        self._lame_exe = MP3_STREAM['exe']
        if not os.path.isfile(self._lame_exe):
            raise Exception("The lame executable does not exist at %s." % self._lame_exe)

        self.bitrate = MP3_STREAM['bitrate']
        if self.bitrate < 0 or self.bitrate > 1024:
            raise Exception("Set your bitrate to between 0 and 1024 not %d." % self.bitrate)


    def add_client(self, client):
        try:
            self._clientlock.acquire()
            self._clients[client.sock] = client
            self._lame_enc_stream(client)
            self.numusers += 1
        finally:
            self._clientlock.release()

    def stop(self):
        self._running = False

    def _remove_client(self, client):
        client.sock.close()
        del self._clients[client.sock]
        self.numusers -= 1
        print("Removed client")

    def _send_bytes(self, sock, bytes):
        bytes_to_send = len(bytes)
        bytes_sent = 0
        while bytes_sent < bytes_to_send:
            bytes_sent += sock.send(bytes[bytes_sent:])

    def _send_data(self, client):
        """ This function assumes that bytes is never more than 2x ChunkSize """
        bytes = self._get_chunck_data(client)
        if not client.supportsmetadata:
            self._send_bytes(client.sock, bytes)
        else:
            if client.bytestometadata < len(bytes):
                self._send_bytes(client.sock, bytes[:client.bytestometadata])
                self._send_bytes(client.sock, self._metadata)
                self._send_bytes(client.sock, bytes[client.bytestometadata:])
                client.bytestometadata = MP3Chunker.ChunkSize - len(bytes[client.bytestometadata:])
            else:
                client.bytestometadata -= len(bytes)
                self._send_bytes(client.sock, bytes)

    def _get_chunck_data(self, client):
        proc = client.proc
        data = proc.stdout.read(MP3Chunker.ChunkSize)
        if not data:
            os.kill(proc.pid, signal.SIGKILL)  # because 2.5 doesn't have terminate()
        return data

    def run(self):

        try:
            # time to sleep inbetweeen chunk sends..
            timetosleep = float(MP3Chunker.ChunkSize) / ((self.bitrate / 8) * 1024.0)
            while self._running:
                start = time.time()

                try:
                    self._clientlock.acquire()

                    csocks = self._clients.keys()

                    r, w, e = select.select(csocks, csocks, [], 0)
                    for sock in w:
                        try:
                            self._send_data(self._clients[sock])

                        except socket.error as e:
                            self._remove_client(self._clients[sock])

                    for sock in r:
                        if sock in self._clients:
                            try:
                                bytes = sock.recv(1024)
                                if len(bytes) == 0:
                                    self._remove_client(self._clients[sock])
                            except socket.error as e:
                                self._remove_client(self._clients[sock])

                finally:
                    self._clientlock.release()

                elapsed = time.time() - start

                sleepytime = timetosleep - elapsed
                if sleepytime > 0:
                    time.sleep(sleepytime)

        finally:
            for client in self._clients.values():
                client.sock.close()
                os.kill(client.proc.pid, signal.SIGKILL)  # because 2.5 doesn't have terminate()

            self._clients = {}
            self._numusers = 0
