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
    occurrence_count: int
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
    sum_count = Htree1.occurrence_count + Htree2.occurrence_count
    char = min(Htree1.character, Htree2.character)
    return HNode(sum_count, char, Htree1, Htree2)


# given a sorted HTList with len over 2 it returns a new HTList that combines the first two nodes of the given HTList
# to make a new single node where the occurence count is the sum of the two nodes occurence counts
# and holds the lesser char
def coalesce_once(htl_sorted: HTList) -> HTList:
    if htl_sorted is None or htl_sorted.rest is None:
        raise ValueError("List must have at least 2 elements")

    # Merge first two, skip them in the rest of the list
    merged = coalesce_helper(htl_sorted.tree, htl_sorted.rest.tree)
    return tree_list_insert(htl_sorted.rest.rest, merged)


# merges every two nodes in a HTList untill the function reaches the end of the list
def coalesce_all(htl_sorted: HTList) -> HTree:
    if htl_sorted is None:
        return None
    if htl_sorted.rest is None:
        return htl_sorted.tree
    return coalesce_all(coalesce_once(htl_sorted))


# Construct a Huffman tree from 's'.
def string_to_HTree(s: str) -> HTree:
    # chain together the functions required for the task:
    freqs = cnt_freq(s)
    treelist = base_tree_list(freqs)
    sorted_treelist = initial_tree_sort(treelist)
    return coalesce_all(sorted_treelist)

# Creates an encoder array from 'tree'
def build_encoder_array(tree: HTree) -> list[str]:
    # Initialize the array with empty strings for all 256 ASCII values
    encoder_array = [""] * 256
    
    # Helper function to perform the recursive traversal
    def traverse(node: HTree, code: str):
        match node:
            case HLeaf(_, char):
                # When we reach a leaf, store the accumulated code at the character's index
                encoder_array[ord(char)] = code
            case HNode(_, _, left, right):
                # Traverse left (add '0') and right (add '1')
                traverse(left, code + "0")
                traverse(right, code + "1")
    
    # Start traversal from the root with an empty path string
    if tree is not None:
        traverse(tree, "")
        
    return encoder_array

# Takes a string and an encoder array, returning a single string of '0's and '1's 
# representing the Huffman encoding of 'text'.
def encode_string_one(text: str, encoder_array: list[str]) -> str:

    encoded_chars = []

    for char in text:
        encoded_chars.append(encoder_array[ord(char)])

    return "".join(encoded_chars)

# Converts 'bits' of '1's and '0's into a bytearray.
# Pads 'bits' with trailing '0's if the length is not a multiple of 8.
def bits_to_bytes(bits: str) -> bytearray:
    remainder = len(bits) % 8
    if remainder != 0:
        padding_needed = 8 - remainder
        bits += '0' * padding_needed

    num_bytes = len(bits) // 8
    
    result = bytearray(num_bytes)

    for i in range(num_bytes):
        start = i * 8
        end = start + 8
        byte_str = bits[start:end]

        result[i] = int(byte_str, 2)
        
    return result

with open("test_input.txt", "w") as f:
    f.write("hello huffman! this is a test string.")

# Create a huffman code file read from 'source_path' and wirtten to 'target_path'
def huffman_code_file(source_path: str, target_path: str) -> None:
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tree = string_to_HTree(content)

    encoder_array = build_encoder_array(tree)
    
    bit_string = encode_string_one(content, encoder_array)
    
    encoded_bytes = bits_to_bytes(bit_string)
    
    with open(target_path, 'wb') as f:
        f.write(encoded_bytes)

huffman_code_file("test_input.txt", "test_output.bin")

class Tests(unittest.TestCase):

    testHTL1: HTList = HTLNode(
        HLeaf(3, "a"),
        HTLNode(
            HLeaf(5, "b"),
            HTLNode(
                HLeaf(14, "c"), HTLNode(HLeaf(8, "d"), HTLNode(HLeaf(4, " "), None))
            ),
        ),
    )

    testHTL2: HTList = HTLNode(
        HLeaf(10, "g"),
        HTLNode(
            HLeaf(5, "f"),
            HTLNode(
                HLeaf(8, "c"),
                HTLNode(
                    HLeaf(9, "d"), HTLNode(HLeaf(4, "e"), HTLNode(HLeaf(6, "u"), None))
                ),
            ),
        ),
    )

    sortedHTL1: HTList = HTLNode(
        HLeaf(6, " "),
        HTLNode(HLeaf(7, "a"), HTLNode(HLeaf(13, " "), None)),
    )

    sortedHTL2: HTList = HTLNode(
        HLeaf(3, "a"),
        HTLNode(
            HLeaf(4, " "),
            HTLNode(
                HLeaf(5, "b"), HTLNode(HLeaf(8, "d"), HTLNode(HLeaf(14, "c"), None))
            ),
        ),
    )

    sortedHTL3: HTList = HTLNode(
        HLeaf(4, "e"),
        HTLNode(
            HLeaf(5, "f"),
            HTLNode(
                HLeaf(6, "u"),
                HTLNode(
                    HLeaf(8, "c"), HTLNode(HLeaf(9, "d"), HTLNode(HLeaf(10, "g"), None))
                ),
            ),
        ),
    )

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
        self.assertEqual(list_len(None), 0)
        self.assertEqual(list_len(self.testHTL1), 5)

    def test_ref(self):
        self.assertEqual(list_ref(self.testHTL1, 2), HLeaf(14, "c"))
        self.assertEqual(list_ref(self.testHTL2, 4), HLeaf(4, "e"))

    def test_base_tree_list(self):
        # Test with a simple frequency list where only 'a' (97) and 'b' (98) have counts
        freqs = [0] * 256
        freqs[97] = 5  # 'a'
        freqs[98] = 10  # 'b'

        result = base_tree_list(freqs)

        # Index 98 should be 'b' with count 10
        leaf_b = list_ref(result, 98)
        self.assertEqual(leaf_b.character, "b")
        self.assertEqual(leaf_b.occurrence_count, 10)

        # Test that a zeroed-out frequency array still produces 256 nodes with 0 counts
        freqs = [0] * 256
        result = base_tree_list(freqs)

        # Check the first node (ASCII 0)
        first_node = list_ref(result, 0)
        self.assertEqual(first_node.character, chr(0))
        self.assertEqual(first_node.occurrence_count, 0)

        # Check the last node (ASCII 255)
        last_node = list_ref(result, 255)
        self.assertEqual(last_node.character, chr(255))
        self.assertEqual(last_node.occurrence_count, 0)

    def test_tree_list_insert(self):
        input1 = HTLNode(HLeaf(6, " "), HTLNode(HLeaf(7, "a"), None))
        input2 = HLeaf(13, " ")
        expected = self.sortedHTL1
        self.assertEqual(tree_list_insert(input1, input2), expected)

        input3 = HTLNode(HLeaf(7, "a"), HTLNode(HLeaf(13, " "), None))
        input4 = HLeaf(6, " ")
        expected = self.sortedHTL1
        self.assertEqual(tree_list_insert(input3, input4), expected)

    def test_initial_tree_sort(self):
        self.assertEqual(initial_tree_sort(self.testHTL1), self.sortedHTL2)
        self.assertEqual(initial_tree_sort(self.testHTL2), self.sortedHTL3)

    def test_coalesce_once(self):
        lst = HTLNode(
            HLeaf(3, "a"), HTLNode(HLeaf(4, "b"), HTLNode(HLeaf(10, "c"), None))
        )

        result = coalesce_once(lst)
        self.assertEqual(result.tree.occurrence_count, 7)
        self.assertEqual(result.rest.tree.occurrence_count, 10)

    def test_coalesce_all(self):
        leaf_a = HLeaf(3, "a")
        leaf_b = HLeaf(4, "b")
        leaf_c = HLeaf(10, "c")

        lst = HTLNode(leaf_a, HTLNode(leaf_b, HTLNode(leaf_c, None)))
        result = coalesce_all(lst)

        self.assertIsInstance(result, HNode)
        self.assertEqual(result.occurrence_count, 17)
        self.assertEqual(result.character, "a")

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

    def test_build_encoder_array(self):
        
        leaf_a = HLeaf(1, "a")
        leaf_b = HLeaf(1, "b")
        leaf_c = HLeaf(1, "c")
        inner_node = HNode(2, "b", leaf_b, leaf_c)
        root = HNode(3, "a", leaf_a, inner_node)

        encoder = build_encoder_array(root)

        self.assertEqual(encoder[ord('a')], "0")
        self.assertEqual(encoder[ord('b')], "10")
        self.assertEqual(encoder[ord('c')], "11")

        self.assertEqual(encoder[ord('d')], "")
        self.assertEqual(encoder[32], "") 
        
        self.assertEqual(len(encoder), 256)

    def test_build_encoder_array_single_leaf(self):
        leaf_z = HLeaf(5, "z")
        encoder = build_encoder_array(leaf_z)
        self.assertEqual(encoder[ord('z')], "")

    def test_encode_string_one(self):
        encoder = [""] * 256
        encoder[ord('a')] = "0"
        encoder[ord('b')] = "10"
        encoder[ord('c')] = "11"
        encoder[ord(' ')] = "111"

        self.assertEqual(encode_string_one("abc", encoder), "01011")
        self.assertEqual(encode_string_one("a ba", encoder), "0111100")
        self.assertEqual(encode_string_one("", encoder), "")
        self.assertEqual(encode_string_one("z", encoder), "")

    def test_bits_to_bytes(self):
        self.assertEqual(bits_to_bytes("01000001"), bytearray([65]))
        self.assertEqual(bits_to_bytes("1"), bytearray([128]))
        self.assertEqual(bits_to_bytes("111111111"), bytearray([255, 128]))
        self.assertEqual(bits_to_bytes("0000000000000001"), bytearray([0, 1]))
        self.assertEqual(bits_to_bytes(""), bytearray(0))
        self.assertEqual(bits_to_bytes("10101010"), bytearray([170]))


if __name__ == "__main__":
    unittest.main()
