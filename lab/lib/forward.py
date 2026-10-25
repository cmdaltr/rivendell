#!/usr/bin/env python3
"""Tiny TCP forwarder: 127.0.0.1:<listen> -> <host>:<port>.

Used on Apple silicon to put Tart VMs' SSH on a fixed loopback port (2230 Linux,
2231 macOS), matching the ports Vagrant forwards on Intel, so the collector
container reaches every VM the same way (host.docker.internal:<port>).

    forward.py 2231 192.168.64.5 22
"""

import asyncio
import sys


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except ConnectionError:
        pass
    finally:
        writer.close()


async def main(listen: int, host: str, port: int) -> None:
    async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        try:
            ur, uw = await asyncio.open_connection(host, port)
        except OSError:
            w.close()
            return
        await asyncio.gather(pipe(r, uw), pipe(ur, w))

    server = await asyncio.start_server(handle, "127.0.0.1", listen)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]), sys.argv[2], int(sys.argv[3])))
