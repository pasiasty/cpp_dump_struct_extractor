# cpp_dump_struct_extractor

The demo can be verified in following way:

1. Compile code in file main.cpp (with debug symbols included):

command: gcc main.cpp -o main -g

2. Run application in order to obtain out.bin file.

command: ./main

3. Run pahole using following arguments:

command: pahole --hex -c 100000 main -y B -E

4. Run demo.py in order to obtain parsed.txt file.

command: python demo.py
