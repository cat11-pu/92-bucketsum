"""bucketsum.py：分桶摘要（增量校验内核）。"""
from __future__ import annotations

import hashlib
import json


def _stable_hash(key: str) -> int:
    """按键内容的稳定散列：与插入顺序、进程无关，两个副本必落同一桶。"""
    return sum((index + 1) * byte for index, byte in enumerate(key.encode("utf-8")))


def _item_sum(key: str, value: str) -> int:
    return sum(map(ord, key)) + sum(map(ord, value))


def _item_stamp(key: str, value: str) -> int:
    """键值对的强指纹：避免摘要和抵消时漏掉差异。"""
    digest = hashlib.sha256(key.encode("utf-8") + b"=" + value.encode("utf-8")).digest()
    return int.from_bytes(digest[:16], "big")


class Digest:
    def __init__(self, bucket: int = 4):
        self.bucket = bucket
        self.items = {}
        self.compares = 0
        self._sums = {}
        self._stamps = {}

    def _bucket_of(self, key: str) -> int:
        return _stable_hash(key) % self.bucket

    def _track(self, key: str, value: str, sign: int) -> None:
        bucket_id = self._bucket_of(key)
        sums = self._sums.setdefault(bucket_id, [0, 0])
        sums[0] += sign * _item_sum(key, value)
        sums[1] += sign
        self._stamps[bucket_id] = self._stamps.get(bucket_id, 0) ^ _item_stamp(key, value)
        if sums[1] == 0:
            del self._sums[bucket_id]
            del self._stamps[bucket_id]

    def put(self, key: str, value: str) -> dict:
        if key in self.items:
            self._track(key, self.items[key], -1)
        self.items[key] = value
        self._track(key, value, 1)
        return {"size": len(self.items)}

    def digest(self) -> dict:
        """整份摘要：桶摘要的集合，两份相等即认为无差异。"""
        return {
            "bucket": self.bucket,
            "sums": self._bucket_sums(),
            "stamps": {bucket_id: stamp for bucket_id, stamp in sorted(self._stamps.items())},
        }

    def _bucket_sums(self) -> dict:
        return {bucket_id: total for bucket_id, (total, _count) in sorted(self._sums.items())}

    def _bucket_marks(self) -> dict:
        """每桶的完整摘要：摘要和 + 键数 + 强指纹。"""
        return {
            bucket_id: (total, count, self._stamps[bucket_id])
            for bucket_id, (total, count) in self._sums.items()
        }

    def diff(self, other) -> dict:
        """先比桶摘要，只对摘要不同的桶逐键比较。"""
        mine, theirs = self._bucket_marks(), other._bucket_marks()
        differing = sorted(
            bucket_id
            for bucket_id in set(mine) | set(theirs)
            if mine.get(bucket_id) != theirs.get(bucket_id)
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
        return {"bucket": self.bucket, "sums": self._bucket_sums()}

    def persist(self) -> bytes:
        return json.dumps(
            {"bucket": self.bucket, "items": self.items}, sort_keys=True
        ).encode("utf-8")

    def restore(self, blob: bytes = None) -> dict:
        if blob is not None:
            state = json.loads(blob.decode("utf-8"))
            self.bucket = state["bucket"]
            self.items = {}
            self._sums = {}
            self._stamps = {}
            for key, value in state["items"].items():
                self.put(key, value)
        return self.buckets()

    def stats(self) -> dict:
        return {"bucket": self.bucket, "size": len(self.items), "compares": self.compares}
