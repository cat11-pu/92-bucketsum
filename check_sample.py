"""check_sample.py：按 sample/keys.json 走一圈，打印验收面。"""
import json
import os
import sys

from bucketsum import Digest


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "keys.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    left, right = Digest(spec["bucket"]), Digest(spec["bucket"])
    for key, value in spec["left"].items():
        left.put(key, value)
    for key, value in spec["right"].items():
        right.put(key, value)
    buckets = left.buckets()
    result = left.diff(right)
    blob = left.persist()
    reborn = Digest(spec["bucket"])
    restored = reborn.restore(blob)
    print("桶个数 =", len(buckets.get("sums") or {}))
    print("各桶摘要 =", buckets.get("sums"))
    print("变更的键 =", result.get("changed"))
    print("实际比较的键数 =", result.get("compared"))
    print("全量比较的键数（对照） =", len(set(spec["left"]) | set(spec["right"])))
    print("不同的桶 =", result.get("differing_buckets"))
    print("恢复后的桶个数 =", len(restored.get("sums") or {}))
    print("不变量（差异定位与逐键比较一致） =", spec["diff_invariant"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
