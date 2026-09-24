"""bucketsum.py：分桶摘要（基线：全量比）。"""
from __future__ import annotations


class Digest:
    def __init__(self, bucket: int = 4):
        self.bucket = bucket
        self.items = {}
        self.compares = 0

    def put(self, key: str, value: str) -> dict:
        self.items[key] = value
        return {"size": len(self.items)}

    def digest(self) -> dict:
        raise NotImplementedError("分桶摘要还没实现")

    def diff(self, other) -> dict:
        """基线：逐键全量比。"""
        self.compares = len(set(self.items) | set(other.items))
        keys = sorted(set(self.items) | set(other.items))
        changed = [key for key in keys if self.items.get(key) != other.items.get(key)]
        return {"changed": changed, "compared": self.compares}

    def buckets(self) -> dict:
        raise NotImplementedError("桶映射还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"bucket": self.bucket, "size": len(self.items), "compares": self.compares}
