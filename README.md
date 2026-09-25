# bucketsum

纯 Python 标准库的 bucketsum。

## 用法

    from bucketsum import Digest

    left, right = Digest(bucket=4), Digest(bucket=4)
    left.put("k1", "a")          # 写入键值
    left.buckets()               # {"bucket": 4, "sums": {桶号: 摘要和}}
    left.digest()                # 整份摘要（桶摘要的集合）
    left.diff(right)             # {"changed": [...], "compared": n, "differing_buckets": [...]}
    blob = left.persist()        # 快照落盘（bytes）
    Digest().restore(blob)       # 重启恢复，数据与桶摘要一致

分桶按键内容的稳定散列（与插入顺序、进程无关），同一键在两个副本必落同一桶；
diff 先比桶摘要，只对摘要不同的桶逐键比较，比较次数与差异所在桶的键数成正比。

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py
