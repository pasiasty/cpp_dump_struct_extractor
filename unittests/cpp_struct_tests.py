from cpp_struct import *
from pahole_output_parser import *

import unittest


class MultidimensionalIteratorTests(unittest.TestCase):

    def test_simple_case(self):

        iterator = MultidimensionalIterator([2, 2, 3])
        print()

        self.assertEqual([0, 0, 0], iterator.increment())
        self.assertEqual([1, 0, 0], iterator.increment())
        self.assertEqual([0, 1, 0], iterator.increment())
        self.assertEqual([1, 1, 0], iterator.increment())
        self.assertEqual([0, 0, 1], iterator.increment())
        self.assertEqual([1, 0, 1], iterator.increment())
        self.assertEqual([0, 1, 1], iterator.increment())
        self.assertEqual([1, 1, 1], iterator.increment())
        self.assertEqual([0, 0, 2], iterator.increment())
        self.assertEqual([1, 0, 2], iterator.increment())
        self.assertEqual([0, 1, 2], iterator.increment())
        self.assertEqual([1, 1, 2], iterator.increment())

        self.assertRaises(StopIteration, iterator.increment)


class CppStructTests(unittest.TestCase):

    def test_create_empty_multidimensional_array(self):
        array_desc = [7, 4, 5, 2]

        res = CppStruct.create_empty_multidimensional_array(array_desc)

        self.assertEqual(2, len(res))
        self.assertEqual(5, len(res[0]))
        self.assertEqual(4, len(res[0][0]))
        self.assertEqual(0, len(res[0][0][0]))

        array_desc = [2, 2]

        res = CppStruct.create_empty_multidimensional_array(array_desc)

        self.assertEqual(2, len(res))
        self.assertEqual(0, len(res[0]))

    def test_get_cpp_struct_from_layout(self):

        struct_layout = MainStructure(type='TestType', content=[])

        substruct = StructureFieldEntry(type='SimpleType',
                                        name='substruct',
                                        content=[SimpleFieldEntry(type='int',
                                                                  name='inner',
                                                                  array_desc=[],
                                                                  mem_offset=0,
                                                                  size=4)],
                                        array_desc=[],
                                        size=4)

        struct_layout.content.append(substruct)
        struct_layout.content.append(SimpleFieldEntry(type='int', name='a', array_desc=[1, 2], mem_offset=0, size=8))
        struct_layout.content.append(SimpleFieldEntry(type='int', name='b', array_desc=[], mem_offset=0, size=4))

        dump = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]

        cpp_struct = CppStruct(print, struct_layout, dump)

        self.assertEqual('int', cpp_struct.substruct.inner.type)
        self.assertEqual(0x00010203, cpp_struct.substruct.inner.value)
        self.assertEqual(0, cpp_struct.substruct.inner.offset)
        self.assertEqual(4, cpp_struct.substruct.inner.size)

        self.assertEqual('int', cpp_struct.a.type)
        self.assertEqual(0x04050607, cpp_struct.a[0][0].value)
        self.assertEqual(4, cpp_struct.a[0][0].offset)
        self.assertEqual(4, cpp_struct.a[0][0].size)

        self.assertEqual(0x08090A0B, cpp_struct.a[1][0].value)
        self.assertEqual(8, cpp_struct.a[1][0].offset)
        self.assertEqual(4, cpp_struct.a[1][0].size)

        self.assertEqual('int', cpp_struct.b.type)
        self.assertEqual(0x0C0D0E0F, cpp_struct.b.value)
        self.assertEqual(12, cpp_struct.b.offset)
        self.assertEqual(4, cpp_struct.b.size)
