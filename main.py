from typing import *
from dataclasses import dataclass
import unittest
import sys

sys.setrecursionlimit(10**6)


# data definitions
class HNode:
    occurance_count: int
    character: str
    left: "HTree"
    right: "HTree"


class Hleaf:
    occurance_count: int
    character: str


HTree: TypeAlias = Union[HNode, Hleaf]


# returns an array where each index corresponds to an ascii number and holds the number of times such ascii
# value appears in the given string
def cnt_freq(text: str) -> list[int]:
    freq = [0 for _ in range(256)]

    for i in text:
        ascii_num = ord(i)
        if ascii_num <= 255:
            freq[ascii_num] += 1

    return freq


class Tests(unittest.TestCase):

    def test_cnt_freq(self):
        empty_str = [0 for _ in range(256)]
        test_1 = [0 for _ in range(256)]
        test_1[96:104] = [0, 2, 4, 8, 16, 0, 2, 0]
        test_2 = [0 for _ in range(256)]
        test_2[97] = 3
        test_2[65] = 3
        test_2[56] = 1
        self.assertEqual(cnt_freq("ddddddddddddddddccccccccbbbbaaff"), test_1)
        self.assertEqual(cnt_freq("aaaAAA8"), test_2)
        self.assertEqual(cnt_freq(""), empty_str)


if __name__ == "__main__":
    unittest.main()
