from collections import namedtuple
import re

MainStructureRawEntry = namedtuple('MainStructureRawEntry', ['type', 'content'])
MainStructureSorted = namedtuple('MainStructureSorted', ['type', 'content'])
MainStructure = namedtuple('MainStructure', ['type', 'content'])
StructureFieldEntry = namedtuple('StructureFieldEntry', ['type', 'name', 'content', 'array_desc', 'size'])
SimpleFieldEntry = namedtuple('SimpleFieldEntry', ['type', 'name', 'array_desc', 'mem_offset', 'size'])


class PaholeOutputParser:

    @staticmethod
    def _remove_not_exact_struct_definition(input_file, desired_struct):
        arr = input_file.split('\n')

        res_beg_idx = next(idx for (idx, el) in enumerate(arr) if ' {} {{'.format(desired_struct) in el)
        res_end_idx = next(idx for (idx, el) in enumerate(arr[res_beg_idx:]) if '};' in el)

        return '\n'.join(arr[res_beg_idx:res_beg_idx + res_end_idx + 1])

    @staticmethod
    def _extract_only_relevant_lines(input_file):
        arr = input_file.split('\n')
        return [el for el in arr if '{' in el or '}' in el or ';' in el]

    @staticmethod
    def _get_struct_type_from_first_line_of_definition(line):
        return line.strip().split(' ')[1]

    @staticmethod
    def _get_info_of_main_structure(input_arr):
        type = PaholeOutputParser._get_struct_type_from_first_line_of_definition(input_arr[0])
        content = input_arr[1:len(input_arr)-1]
        return MainStructureRawEntry(type=type, content=content)

    @staticmethod
    def _sort_raw_struct_content_by_fields(input_struct):
        content = input_struct.content
        in_struct_field = False

        fields = []
        current_struct_content = []

        for el in content:
            if not in_struct_field and 'struct' in el and '{' in el:
                in_struct_field = True
                current_struct_content = [el]

            elif in_struct_field:
                current_struct_content.append(el)

                if '}' in el:
                    in_struct_field = False
                    fields.append(current_struct_content)
            else:
                fields.append(el)

        return fields

    @staticmethod
    def _get_array_description(line):
        if '[' in line:
            start_idx = line.find('[')
            end_idx = line.rfind(']')

            raw_arr_desc = line[start_idx:end_idx]
            raw_arr_desc = re.sub('\[', '', raw_arr_desc)
            return [int(el) for el in raw_arr_desc.split(']')]
        else:
            return []

    @staticmethod
    def _parse_raw_struct_field(input_raw_struct_field):
        last_line = input_raw_struct_field[-1]
        type = PaholeOutputParser._get_struct_type_from_first_line_of_definition(input_raw_struct_field[0])
        content = input_raw_struct_field[1:len(input_raw_struct_field) - 1]
        field_name = re.sub('\[.*;', '', last_line.strip().split(' ')[1])
        array_desc = PaholeOutputParser._get_array_description(last_line)
        size = PaholeOutputParser._get_size_of_entry(last_line)

        return StructureFieldEntry(type=type, name=field_name, content=content, array_desc=array_desc, size=size)

    @staticmethod
    def _parse_single_simple_field(input_simple_field):
        semicolon_idx = input_simple_field.find(';')
        name_beg_idx = input_simple_field[:semicolon_idx].rfind(' ') + 1
        field_type = input_simple_field[:name_beg_idx].strip()

        if '[' in input_simple_field:
            name_end_idx = input_simple_field.find('[')
        else:
            name_end_idx = semicolon_idx

        name = input_simple_field[name_beg_idx:name_end_idx]
        arr_desc = PaholeOutputParser._get_array_description(input_simple_field)
        mem_offset = int(input_simple_field[input_simple_field.find('/*') + 2:].strip().split(' ')[0], 16)
        size = PaholeOutputParser._get_size_of_entry(input_simple_field)

        return SimpleFieldEntry(type=field_type, name=name, array_desc=arr_desc, mem_offset=mem_offset, size=size)

    @staticmethod
    def _parse_all_struct_fields(fields):

        res = []

        for raw_field_entry in fields:
            if isinstance(raw_field_entry, list):
                struct_field = PaholeOutputParser._parse_raw_struct_field(raw_field_entry)
                content = PaholeOutputParser._sort_raw_struct_content_by_fields(struct_field)
                content = PaholeOutputParser._parse_all_struct_fields(content)
                res.append(StructureFieldEntry(type=struct_field.type,
                                               name=struct_field.name,
                                               array_desc=struct_field.array_desc,
                                               content=content,
                                               size=struct_field.size))
            else:
                res.append(PaholeOutputParser._parse_single_simple_field(raw_field_entry))

        return res

    @staticmethod
    def _parse_all_fields_of_main_struct(input_sorted_struct):
        return MainStructure(type=input_sorted_struct.type,
                             content=PaholeOutputParser._parse_all_struct_fields(input_sorted_struct.content))

    @staticmethod
    def _get_size_of_entry(entry):
        return int(entry[:entry.rfind('*/')].strip().split(' ')[-1], 16)

    @staticmethod
    def parse_raw_pahole_output(raw_pahole_output, desired_struct):
        res = PaholeOutputParser._remove_not_exact_struct_definition(raw_pahole_output, desired_struct)
        res = PaholeOutputParser._extract_only_relevant_lines(res)
        res = PaholeOutputParser._get_info_of_main_structure(res)
        res = MainStructureSorted(res.type,
                                  PaholeOutputParser._sort_raw_struct_content_by_fields(res))
        res = PaholeOutputParser._parse_all_fields_of_main_struct(res)

        return res