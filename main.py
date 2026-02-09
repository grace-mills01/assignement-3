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


class Tests(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
