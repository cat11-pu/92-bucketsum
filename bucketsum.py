"""bucketsum.py：分桶摘要（增量校验内核）。"""
from __future__ import annotations

import json


def _stable_hash(key: str) -> int:
    """按键内容的稳定散列：与插入顺序、进程无关，两个副本必落同一桶。"""
    return sum((index + 1) * byte for index, byte in enumerate(key.encode("utf-8")))


def _item_sum(key: str, value: str) -> int:
    return sum(map(ord, key)) + sum(map(ord, value))


class Digest:
    def __init__(self, bucket: int = 4):
        self.bucket = bucket
        self.items = {}
        self.compares = 0

    def _bucket_of(self, key: str) -> int:
        return _stable_hash(key) % self.bucket

    def _sums(self) -> dict:
        sums = {}
        for key, value in self.items.items():
            bucket_id = self._bucket_of(key)
            sums[bucket_id] = sums.get(bucket_id, 0) + _item_sum(key, value)
        return sums

    def put(self, key: str, value: str) -> dict:
        self.items[key] = value
        return {"size": len(self.items)}

    def digest(self) -> dict:
        """整份摘要：桶摘要的集合，两份相等即认为无差异。"""
        return self.buckets()

    def diff(self, other) -> dict:
        """先比桶摘要，只对摘要不同的桶逐键比较。"""
        mine, theirs = self._sums(), other._sums()
        differing = sorted(
            bucket_id
            for bucket_id in set(mine) | set(theirs)
            if mine.get(bucket_id, 0) != theirs.get(bucket_id, 0)
        )
        differing_set = set(differing)
        keys = sorted(
            {key for key in self.items if self._bucket_of(key) in differing_set}
            | {key for key in other.items if other._bucket_of(key) in differing_set}
        )
        changed = [key for key in keys if self.items.get(key) != other.items.get(key)]
        self.compares = len(keys)
        return {
            "changed": changed,
            "compared": self.compares,
            "differing_buckets": differing,
        }

    def buckets(self) -> dict:
        return {"bucket": self.bucket, "sums": self._sums()}

    def persist(self) -> bytes:
        return json.dumps(
            {"bucket": self.bucket, "items": self.items}, sort_keys=True
        ).encode("utf-8")

    def restore(self, blob: bytes = None) -> dict:
        if blob is not None:
            state = json.loads(blob.decode("utf-8"))
            self.bucket = state["bucket"]
            self.items = dict(state["items"])
        return self.buckets()

    def stats(self) -> dict:
        return {"bucket": self.bucket, "size": len(self.items), "compares": self.compares}
