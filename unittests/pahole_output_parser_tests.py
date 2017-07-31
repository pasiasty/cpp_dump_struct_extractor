from pahole_output_parser import *

import os
import jsonpickle
import unittest


class PaholeOutputParserTests(unittest.TestCase):

    def test_extract_only_relevant_lines(self):
        with open(os.path.join('..', 'resources', '001_raw_pahole_output.txt'), 'r') as input_file:
            input_file_content = input_file.read()

        with open(os.path.join('..', 'resources', '002_only_relevant_lines.txt'), 'r') as input_file:
            expected_res = jsonpickle.decode(input_file.read())

        self.assertEqual(expected_res, PaholeOutputParser._extract_only_relevant_lines(input_file_content))

    def test_get_info_of_main_structure(self):
        with open(os.path.join('..', 'resources', '002_only_relevant_lines.txt'), 'r') as input_file:
            input_file_content = jsonpickle.decode(input_file.read())
        with open(os.path.join('..', 'resources', '003_extracted_info_of_main_structure.txt'), 'r') as input_file:
            expected_res = jsonpickle.decode(input_file.read())

        res = PaholeOutputParser._get_info_of_main_structure(input_file_content)
        self.assertEqual(expected_res, res)

    def test_sort_raw_struct_content_by_fields(self):
        with open(os.path.join('..', 'resources', '003_extracted_info_of_main_structure.txt'), 'r') as input_file:
            input_file_content = jsonpickle.decode(input_file.read())
        with open(os.path.join('..', 'resources', '004_sorted_struct_fields.txt'), 'r') as input_file:
            expected_res = jsonpickle.decode(input_file.read())

        res = MainStructureSorted(input_file_content.type,
                                  PaholeOutputParser._sort_raw_struct_content_by_fields(input_file_content))

        self.assertEqual(expected_res, res)

    def test_get_array_description(self):
        input_line = 'unsigned int a;'
        exp_res = []
        self.assertEqual(exp_res, PaholeOutputParser._get_array_description(input_line))

        input_line = 'unsigned int a[1];'
        exp_res = [1]
        self.assertEqual(exp_res, PaholeOutputParser._get_array_description(input_line))

        input_line = 'unsigned int a[2][3][5];'
        exp_res = [2, 3, 5]
        self.assertEqual(exp_res, PaholeOutputParser._get_array_description(input_line))

    def test_parse_raw_struct_field(self):
        with open(os.path.join('..', 'resources', 'raw_struct_field.txt'), 'r') as input_file:
            input_file_content = jsonpickle.decode(input_file.read())
        with open(os.path.join('..', 'resources', 'parsed_struct_field.txt'), 'r') as input_file:
            expected_res = jsonpickle.decode(input_file.read())

        self.assertEqual(expected_res, PaholeOutputParser._parse_raw_struct_field(input_file_content))

    def test_parse_single_simple_field(self):
        input_field = '                unsigned long      uliCtrl4;                            /*   0x8   0x4 */'
        exp_res = SimpleFieldEntry(type='unsigned long', name='uliCtrl4', array_desc=[], mem_offset=0x8, size=0x4)

        self.assertEqual(exp_res, PaholeOutputParser._parse_single_simple_field(input_field))

        input_field = 'unsigned long              auliCRETempNonUE[1][2][6][2];                     /* 0x4d0  0x60 */'

        exp_res = SimpleFieldEntry(type='unsigned long',
                                   name='auliCRETempNonUE',
                                   array_desc=[1, 2, 6, 2],
                                   mem_offset=0x4d0,
                                   size=0x60)

        self.assertEqual(exp_res, PaholeOutputParser._parse_single_simple_field(input_field))

    def test_parse_all_sorted_fields_recursively(self):
        with open(os.path.join('..', 'resources', '004_sorted_struct_fields.txt'), 'r') as input_file:
            input_file_content = jsonpickle.decode(input_file.read())
        with open(os.path.join('..', 'resources', '005_fully_parsed_struct.txt'), 'r') as input_file:
            expected_res = jsonpickle.decode(input_file.read())

        res = PaholeOutputParser._parse_all_fields_of_main_struct(input_file_content)
        self.assertEqual(expected_res, res)

