from pahole_output_parser import PaholeOutputParser
from cpp_struct import CppStruct

import os

dump = open(os.path.join('demo', 'out.bin'), 'rb').read()
raw_pahole_output = open(os.path.join('demo', 'raw_pahole_output.txt'), 'r').read()
struct_layout = PaholeOutputParser.parse_raw_pahole_output(raw_pahole_output)

cpp_struct = CppStruct(struct_layout, dump, 0, '<')

with open('parsed.txt', 'w') as out_file:
    def my_print(*args):
        out_file.write(*args)
        out_file.write('\n')

    cpp_struct.print_struct(my_print)