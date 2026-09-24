"""digestapi.py：对外门面（老接口 put/diff 不能改）。"""
from __future__ import annotations

from bucketsum import Digest


class Replica:
    def __init__(self, bucket: int = 4):
        self.digest = Digest(bucket)

    def put(self, key: str, value: str) -> dict:
        return self.digest.put(key, value)

    def digest_of(self) -> dict:
        return self.digest.digest()

    def diff(self, other) -> dict:
        return self.digest.diff(other.digest if hasattr(other, "digest") else other)

    def buckets(self) -> dict:
        return self.digest.buckets()

    def snapshot(self) -> bytes:
        return self.digest.persist()

    def rebuild(self, blob: bytes = None) -> dict:
        return self.digest.restore(blob)
