import unittest

from bucketsum import Digest
from digestapi import Replica


class TestDigest(unittest.TestCase):
    def test_put_counts(self):
        self.assertEqual(Digest().put("a", "1")["size"], 1)

    def test_diff_identical(self):
        left, right = Digest(), Digest()
        left.put("a", "1")
        right.put("a", "1")
        self.assertEqual(left.diff(right)["changed"], [])

    def test_diff_changed(self):
        left, right = Digest(), Digest()
        left.put("a", "1")
        right.put("a", "2")
        self.assertEqual(left.diff(right)["changed"], ["a"])

    def test_stats_shape(self):
        self.assertIn("bucket", Digest().stats())

    def test_replica_wraps(self):
        replica = Replica()
        replica.put("a", "1")
        self.assertEqual(replica.digest.stats()["size"], 1)


if __name__ == "__main__":
    unittest.main()
