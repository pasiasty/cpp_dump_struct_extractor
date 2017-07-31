from pahole_output_parser import StructureFieldEntry, SimpleFieldEntry
from collections import namedtuple
import functools


class MultidimensionalIterator:

    def __init__(self, arr):
        self.sizes = arr
        self.idx = [0] * len(arr)
        self.gave_last_element = False

    def increment(self):

        if self.gave_last_element:
            raise StopIteration

        result = list(self.idx)
        self.idx[0] += 1
        check_it = 0

        while self.idx[check_it] >= self.sizes[check_it]:

            if check_it == (len(self.sizes) - 1):
                self.gave_last_element = True
                break
            else:
                self.idx[check_it] = 0
                self.idx[check_it + 1] += 1
                check_it += 1

        return result

ArrayElementEntry = namedtuple('ArrayElementEntry', ['value', 'offset', 'size'])
StructFieldEntry = namedtuple('StructFieldEntry', ['type', 'value', 'offset', 'size'])


class ArrayEntry:
    def __init__(self, type, offset, content):
        self.type = type
        self.offset = offset
        self.content = content

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]

    def __iter__(self):
        return iter(self.content)

    def get_first_line_of_print(self, name):
        dimmensions = []
        arr_ref = self.content

        while isinstance(arr_ref, list):
            dimmensions.append(len(arr_ref))
            arr_ref = arr_ref[0]

        dim_desc = ''.join(['[' + str(el) + ']' for el in dimmensions])

        return '{} {}{}'.format(self.type, name, dim_desc)

    @staticmethod
    def print_arrays_body(print_func, array, indent_offset, with_comma=False):
        print_func(' ' * indent_offset.value + '[')
        indent_offset.increase()

        max_dig_for_idx = str(len(str(len(array))))

        def idx_string(el_idx, el_type=''):
            return ' ' * indent_offset.value + ('[{:0' + max_dig_for_idx + '}] {} = ').format(el_idx, el_type)

        for idx, entry in enumerate(array):
            if isinstance(entry, CppStruct):
                print_func(idx_string(idx, entry.type))
                entry.print_structs_body(indent_offset, True)
            elif isinstance(entry, list):
                print_func(idx_string(idx))
                ArrayEntry.print_arrays_body(print_func, entry, indent_offset, True)
            elif isinstance(entry, ArrayElementEntry):
                print_func(idx_string(idx) + '{:<15} (addr {:08X} size {:08X}),'.format(
                    entry.value,
                    entry.offset,
                    entry.size
                ))
            else:
                raise NotImplementedError('for type: {}'.format(type(entry)))

        indent_offset.decrease()
        if with_comma:
            print_func(' ' * indent_offset.value + '],')
        else:
            print_func(' ' * indent_offset.value + ']')


class CurrentIndentIndicator:
    def __init__(self, value=0, increase_step=4):
        self.step = increase_step
        self.value = value

    def increase(self):
        self.value += self.step

    def decrease(self):
        self.value -= self.step


class CppStruct:

    @staticmethod
    def create_empty_multidimensional_array(array_desc):
        res = []

        for idx in range(len(array_desc) - 1):
            iterator = MultidimensionalIterator(array_desc[len(array_desc) - 1 - idx:])

            try:
                while True:
                    array_ref = res
                    current_multidim_idx = iterator.increment()[::-1]

                    for depth_idx in range(idx):
                        array_ref = array_ref[current_multidim_idx[depth_idx]]

                    array_ref.append([])
            except StopIteration:
                pass
        return res

    def merge_bytes(self, bytes_arr):
        res = 0
        if self.endiannes == '>':
            for byte in bytes_arr:
                res <<= 8
                if isinstance(byte, int):
                    res += byte
                else:
                    res += ord(byte)
            return res
        elif self.endiannes == '<':
            for byte in bytes_arr[::-1]:
                res <<= 8
                if isinstance(byte, int):
                    res += byte
                else:
                    res += ord(byte)
            return res
        else:
            raise NotImplementedError('endiannes {}'.format(self.endiannes))

    def __init__(self, print_func, struct_layout, dump, curr_offset=0, endiannes='>'):
        self.endiannes = endiannes
        self.type = struct_layout.type
        self.fields = []
        self.print_func = print_func

        for field in struct_layout.content:
            if len(field.array_desc) > 0:
                setattr(self,
                        field.name,
                        ArrayEntry(type=field.type,
                                   offset=curr_offset,
                                   content=CppStruct.create_empty_multidimensional_array(field.array_desc)))

                self.fields.append(field.name)
                single_entry_size = field.size // functools.reduce(lambda x, y: x * y, field.array_desc)

                iterator = MultidimensionalIterator(field.array_desc)
                try:
                    while True:
                        array_ref = getattr(self, field.name).content

                        current_multidim_idx = iterator.increment()[::-1]

                        for depth_idx in range(len(current_multidim_idx) - 1):
                            array_ref = array_ref[current_multidim_idx[depth_idx]]

                        if isinstance(field, StructureFieldEntry):
                            array_ref.append(CppStruct(self.print_func, field, dump, curr_offset, self.endiannes))
                        elif isinstance(field, SimpleFieldEntry):
                            array_ref.append(ArrayElementEntry(value=self.merge_bytes(dump[curr_offset:curr_offset + single_entry_size]),
                                                               offset=curr_offset,
                                                               size=single_entry_size))
                        curr_offset += single_entry_size

                except StopIteration:
                    pass
            else:
                if isinstance(field, StructureFieldEntry):
                    setattr(self, field.name, CppStruct(self.print_func, field, dump, curr_offset, self.endiannes))
                elif isinstance(field, SimpleFieldEntry):
                    setattr(self, field.name, StructFieldEntry(value=self.merge_bytes(dump[curr_offset:curr_offset + field.size]),
                                                               offset=curr_offset,
                                                               size=field.size,
                                                               type=field.type))
                curr_offset += field.size
                self.fields.append(field.name)

    def print_structs_body(self, indent_offset, with_comma=False):

        self.print_func(' ' * indent_offset.value + '{')
        indent_offset.increase()

        for field_name in self.fields:
            field = getattr(self, field_name)
            if isinstance(field, CppStruct):
                self.print_func(' ' * indent_offset.value + '{} {}'.format(field.type, field_name))
                field.print_structs_body(indent_offset)
            elif isinstance(field, ArrayEntry):
                self.print_func(' ' * indent_offset.value + field.get_first_line_of_print(field_name))
                ArrayEntry.print_arrays_body(self.print_func, field.content, indent_offset)
            elif isinstance(field, StructFieldEntry):
                self.print_func(' ' * indent_offset.value + '{:<20} {:<35} = {:<15} (addr {:08X} size {:08X})'.format(
                    field.type,
                    field_name,
                    field.value,
                    field.offset,
                    field.size
                ))
            else:
                raise NotImplementedError('for type: {}'.format(type(field)))

        indent_offset.decrease()
        if with_comma:
            self.print_func(' ' * indent_offset.value + '},')
        else:
            self.print_func(' ' * indent_offset.value + '}')

    def print_struct(self):

        self.print_func('{}'.format(self.type))
        self.print_structs_body(CurrentIndentIndicator())
