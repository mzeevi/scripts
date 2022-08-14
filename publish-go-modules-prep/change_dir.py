import re
import sys
import os

def upper_repl(match):
    return match.group(1)[1].upper()

def change_dir_name(orig, new):
    os.rename(orig, new)

if __name__ == "__main__":
    # replace every instance of a word starting with '!'
    # with the upper case version of the word, for instance
    # replace !data!dog with DataDog
    dir_name = sys.argv[1]
    for x in os.walk(dir_name):
        regex = r'(![a-z])'
        orig_dir_name = x[0]
        new_dir_name = re.sub(regex, upper_repl, orig_dir_name)

        if new_dir_name != orig_dir_name:
            print("Renaming:", orig_dir_name, "To:", new_dir_name)
            change_dir_name(orig_dir_name, new_dir_name)
        else:
            print("No need to rename:", orig_dir_name)
