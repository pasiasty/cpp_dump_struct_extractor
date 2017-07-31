from pahole_output_parser import PaholeOutputParser
from cpp_struct import CppStruct

import argparse
import os
import subprocess


parser = argparse.ArgumentParser()
parser.set_defaults(which='none')

subparsers = parser.add_subparsers()

pahole_mode_parser = subparsers.add_parser('pahole_mode',
                                           help='only Pahole will be invoked on selected elf file')
pahole_mode_parser.set_defaults(which='pahole_mode')
pahole_mode_parser.add_argument('-p', '--elf_file_path',
                                dest='elf_file_path',
                                help='Path to elf file that should be processed with pahole',
                                required=True)
pahole_mode_parser.add_argument('-s', '--struct_name',
                                dest='struct_name',
                                help='Name of structure to be analyzed',
                                required=True)
pahole_mode_parser.add_argument('-o', '--out_file',
                                dest='out_file',
                                help='Output file for command results',
                                required=True)
pahole_mode_parser.add_argument('-v', '--verbose',
                                dest='verbose',
                                help='Run in verbose mode',
                                action='store_true')

extractor_mode_parser = subparsers.add_parser('extractor_mode',
                                              help='only extractor will be used (raw pahole output file required)')
extractor_mode_parser.set_defaults(which='extractor_mode')
extractor_mode_parser.add_argument('-d', '--dump_path',
                                   dest='dump_path',
                                   help='Path to collected dump',
                                   required=True)
extractor_mode_parser.add_argument('-p', '--pahole_path',
                                   dest='pahole_path',
                                   help='Path to file generated with pahole',
                                   required=True)
extractor_mode_parser.add_argument('-f', '--offset',
                                   dest='offset',
                                   help='Offset of target structure in collected dump',
                                   type=int,
                                   required=True)
extractor_mode_parser.add_argument('-e', '--endiannes',
                                   dest='endiannes',
                                   help='Endiannes of the elf architecture',
                                   choices=['<', '>'],
                                   default='<')
extractor_mode_parser.add_argument('-o', '--out_file',
                                   dest='out_file',
                                   help='Output file for command results',
                                   required=True)
extractor_mode_parser.add_argument('-v', '--verbose',
                                   dest='verbose',
                                   help='Run in verbose mode',
                                   action='store_true')

full_mode_parser = subparsers.add_parser('full_mode',
                                         help='script will invoke Pahole and extractor')
full_mode_parser.set_defaults(which='full_mode')
full_mode_parser.add_argument('-p', '--elf_file_path',
                              dest='elf_file_path',
                              help='Path to elf file that should be processed with pahole',
                              required=True)
full_mode_parser.add_argument('-s', '--struct_name',
                              dest='struct_name',
                              help='Name of structure to be analyzed',
                              required=True)
full_mode_parser.add_argument('-d', '--dump_path',
                              dest='dump_path',
                              help='Path to collected dump',
                              required=True)
full_mode_parser.add_argument('-f', '--offset',
                              dest='offset',
                              help='Offset of target structure in collected dump',
                              type=int,
                              required=True)
full_mode_parser.add_argument('-e', '--endiannes',
                              dest='endiannes',
                              help='Endiannes of the elf architecture',
                              choices=['<', '>'],
                              default='<')
full_mode_parser.add_argument('-o', '--out_file',
                              dest='out_file',
                              help='Output file for command results',
                              required=True)
full_mode_parser.add_argument('-v', '--verbose',
                              dest='verbose',
                              help='Run in verbose mode',
                              action='store_true')

args = parser.parse_args()

if args.which == 'pahole_mode':

    cmd = 'pahole --hex -c 10000000 {} -y {} -E > {}'.format(args.elf_file_path,
                                                             args.struct_name,
                                                             args.out_file)
    if args.verbose:
        print(cmd)

    os.system(cmd)

if args.which == 'extractor_mode':

    dump = open(args.dump_path, 'rb').read()
    raw_pahole_output = open(args.pahole_path, 'r').read()
    struct_layout = PaholeOutputParser.parse_raw_pahole_output(raw_pahole_output)

    with open(args.out_file, 'w') as out_file:

        def my_print(*args):
            out_file.write(*args)
            out_file.write('\n')

        cpp_struct = CppStruct(my_print, struct_layout, dump, args.offset, args.endiannes)
        cpp_struct.print_struct()

if args.which == 'full_mode':

    cmd = 'pahole --hex -c 10000000 {} -y {} -E'.format(args.elf_file_path,
                                                        args.struct_name)

    if args.verbose:
        print(cmd)

    raw_pahole_output = subprocess.check_output(cmd,
                                                shell=True)

    dump = open(args.dump_path, 'rb').read()
    struct_layout = PaholeOutputParser.parse_raw_pahole_output(raw_pahole_output)

    cpp_struct = CppStruct(my_print, struct_layout, dump, args.offset, args.endiannes)


    def my_print(*print_args):
        out_file.write(*print_args)
        out_file.write('\n')

    with open('{}.txt'.format(args.out_file), 'w') as out_file:
        cpp_struct.print_struct(out_file)

    import jsonpickle
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options(indent=4)

    with open('{}.jsonpickle'.format(args.out_file), 'w') as out_file:
        out_file.write(jsonpickle.encode(cpp_struct))
