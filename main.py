from typing import *
from dataclasses import dataclass
import unittest
import sys

sys.setrecursionlimit(10**6)


# data definitions
@dataclass
class HNode:
    occurrence_count: int
    character: str
    left: "HTree"
    right: "HTree"


@dataclass
class HLeaf:
    occurrence_countc: int
    character: str


HTList: TypeAlias = Union["HTLNode", None]
HTree: TypeAlias = Union[HNode, HLeaf]


@dataclass
class HTLNode:
    tree: HTree
    rest: HTList


# returns an array where each index corresponds to an ascii number and holds the number of times such ascii
# value appears in the given string
def cnt_freq(text: str) -> list[int]:
    freq = [0 for _ in range(256)]

    for i in text:
        ascii_num = ord(i)
        if ascii_num <= 255:
            freq[ascii_num] += 1

    return freq


# checks if the occurrence count of the first tree is less than that of the second tree or
# if the occurrence counts are the same and the character contained at the root of the first tree is less than
# that of the character ontained at the root of the second tree; either of these will have the function
# return true
def tree_lt(HTree_1: HTree, HTree_2: HTree) -> bool:
    # Check condition (a): Primary sort by occurrence count
    if HTree_1.occurrence_count < HTree_2.occurrence_count:
        return True

    # Check condition (b): Secondary sort by character tie-breaker
    if HTree_1.occurrence_count == HTree_2.occurrence_count:
        return HTree_1.character < HTree_2.character

    return False


# finds the length of a given HTList
def list_len(HTlist: HTList) -> int:
    match HTlist:
        case None:
            return 0
        case HTLNode(_, r):
            return 1 + list_len(r)


# finds the HTree at a given index
def list_ref(HTlist: HTList, idx: int) -> HTree:
    match HTlist:
        case None:
            raise ValueError("index out of bounds")
        case HTLNode(ht, r):
            if idx == 0:
                return ht
            else:
                return list_ref(r, idx - 1)

    return htree


# takes an array of ascii numbers and frequencies from cnt_freq and rturns a HTList of the same values
def base_tree_list(list: list[int]) -> HTList:
    output: HTList = None

    for i in range(255, -1, -1):
        # Create a leaf for the current ASCII character
        # chr(i) converts the integer index to its ASCII character string
        leaf = HLeaf(list[i], chr(i))

        # Prepend the new leaf to the linked list
        output = HTLNode(leaf, output)

    return output


# given a sorted HTree according to tree_lt and inserts another HTree in the correct position
# returns a new tree not a mutated version of the first
def tree_list_insert(HTree_sorted: HTList, Htree_add: HTree) -> HTList:
    if HTree_sorted is None:
        return HTLNode(Htree_add, None)
    elif tree_lt(Htree_add, HTree_sorted.tree):
        return HTLNode(Htree_add, HTree_sorted)
    else:
        return HTLNode(
            HTree_sorted.tree, tree_list_insert(HTree_sorted.rest, Htree_add)
        )


# sorts the given HTList into ascending order
def initial_tree_sort(htlist: HTList) -> HTList:
    if htlist is None:
        return None
    else:
        sorted = initial_tree_sort(htlist.rest)
        return tree_list_insert(sorted, htlist.tree)


# merge two Htrees to be used in coalesce to combine first two nodes
def coalesce_helper(Htree1: HTree, Htree2: HTree) -> HTree:
    sum = Htree1.occurrence_count + Htree2.occurrence_count
    if ord(Htree1.character) < ord(Htree2.character):
        char = Htree1.character
    else:
        char = Htree2.character
    return HNode(sum, char, Htree1, Htree2)


# given a sorted HTList with len over 2 it returns a new HTList that combines the first two nodes of the given HTList
# to make a new single node where the occurence count is the sum of the two nodes occurence counts
# and holds the lesser char
def coalesce_once(htl_sorted: HTList) -> HTList:
    if list_len(htl_sorted) < 2:
        raise ValueError("List of given HTList must be greater than 2")

    match htl_sorted:
        case None:
            return None
        case HTLNode(tree, rest):
            r = rest
            merged = coalesce_helper(tree, r.tree)
            newTree = tree_list_insert(r, merged)
            return newTree


def coalesce_all(htl_sorted: HTList) -> HTree:
    if list_len(htl_sorted) == 1:
        return htl_sorted.tree
    else:
        return coalesce_all(coalesce_once(htl_sorted))


# Construct a Huffman tree from 's'.
def string_to_HTree(s: str) -> HTree:
    # chain together the functions required for the task:
    freqs = cnt_freq(s)
    treelist = base_tree_list(freqs)
    sorted_treelist = initial_tree_sort(treelist)
    return coalesce_all(sorted_treelist)


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

    def test_len(self):
        pass

    def test_ref(self):
        pass

    def test_base_tree_list(self):
        pass

    def test_tree_list_insert(self):
        pass

    def test_initial_tree_sort(self):
        pass

    def test_coalesce_once(self):
        pass

    def test_coalesce_all(self):
        pass

    def test_tree_lt(self):
        # Tree 1 has a smaller count than Tree 2
        t1 = HLeaf(5, "a")
        t2 = HLeaf(10, "b")
        self.assertTrue(tree_lt(t1, t2))
        self.assertFalse(tree_lt(t2, t1))

        # Counts are equal; tie-break by character ('a' < 'b')
        t1 = HLeaf(10, "a")
        t2 = HLeaf(10, "b")
        self.assertTrue(tree_lt(t1, t2))
        self.assertFalse(tree_lt(t2, t1))

        # Function should work regardless of HNode or Hleaf (Duck Typing)
        t1 = HLeaf(5, "z")
        # Assuming HNode sum is 10
        t2 = HNode(10, "a", HLeaf(5, "a"), HLeaf(5, "b"))
        self.assertTrue(tree_lt(t1, t2))

        # Identical trees should return False (it is not strictly "less than")
        t1 = HLeaf(10, "a")
        t2 = HLeaf(10, "a")
        self.assertFalse(tree_lt(t1, t2))


if __name__ == "__main__":
    unittest.main()
