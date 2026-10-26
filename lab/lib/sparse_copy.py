#!/usr/bin/env python3
"""Copy a VM disk image without filling in its holes, then check the copy.

rsync -S and cp don't keep sparseness between APFS volumes, so a 50 GB Tart
disk with 26 GB in use lands as 50 GB. Zero blocks are skipped with a seek,
which APFS stores as holes.

Usage: sparse_copy.py SOURCE DEST
"""

import hashlib
import os
import sys

BLOCK = 1 << 20


def copy(source: str, dest: str) -> list:
    """Copy source to dest, returning the digest of each data block."""
    digests = []
    zero = bytes(BLOCK)
    size = os.path.getsize(source)
    with open(source, "rb") as src, open(dest, "wb") as dst:
        offset = 0
        while True:
            block = src.read(BLOCK)
            if not block:
                break
            if block == zero[:len(block)]:
                dst.seek(len(block), os.SEEK_CUR)
                digests.append(None)
            else:
                dst.write(block)
                digests.append(hashlib.blake2b(block, digest_size=16).digest())
            offset += len(block)
            if offset % (1 << 30) < BLOCK:
                print(f"  {offset >> 30}/{size >> 30} GB", flush=True)
        dst.truncate(size)
    return digests


def verify(dest: str, digests: list) -> bool:
    zero = bytes(BLOCK)
    with open(dest, "rb") as dst:
        for expected in digests:
            block = dst.read(BLOCK)
            if expected is None:
                if block != zero[:len(block)]:
                    return False
            elif hashlib.blake2b(block, digest_size=16).digest() != expected:
                return False
    return True


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[-1])
        return 2
    source, dest = sys.argv[1:]
    digests = copy(source, dest)
    if os.path.getsize(dest) != os.path.getsize(source) or not verify(dest, digests):
        print(f"[x] {dest} doesn't match {source}")
        return 1
    used = os.stat(dest).st_blocks * 512
    print(f"  verified: {os.path.getsize(dest) >> 20} MB, {used >> 20} MB allocated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
