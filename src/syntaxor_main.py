import sys
from syntaxor  import *
from constants import *
from errors    import LexicalError

def pretty_print_error_message(input_filepath, exc):
    pass

def usage():
    usage_str = """
    Error: two arguments required.
    Usage:
        syntaxor INPUTFILE OUTPUTFILE

    """
    print usage_str

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if ((argv_len == 3) or (argv_len == 2)):
        input_filepath = sys.argv[1]
        try:
            syntaxor = Syntaxor(input_filepath)
        except IOError as ioe:
            print "Error: no such file."
            sys.exit()

        if (argv_len == 3):
            output_filepath = sys.argv[2]
            output_file = open(output_filepath, 'w')
            sys.stdout = output_file

        syntaxor.check_syntax()
        # while True:
        #     try:
        #         tok = lex.get_token()
        #         if tok.get_type() == EOF:
        #             break
        #     except LexicalError as le:
        #         #print "\n", e
        #         pretty_print_error_message(input_filepath, le)
        #         sys.exit()
        #     print tok

        if (argv_len == 3):
            output_file.close()
    else:
        usage()
