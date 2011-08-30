import sys
from lexor     import *
from constants import *
from errors    import LexicalError

def pretty_print_error_message(input_filepath, exc):
    input_file = open(input_filepath, 'r')
    line = exc.line
    col  = exc.col
    print exc
    print "In line %s:%s" % (line, col)
    i = 0
    line_str = ""
    while (i < line):
        line_str = input_file.readline()
        i += 1
    if len(line_str) > 0 and line_str[-1] == "\n":
        print line_str,
    else:
        print line_str
    i = 0
    while (i < col):
        sys.stdout.write("-")
        i += 1
    print "^"
    input_file.close()

def usage():
    usage_str = """
    Error: two arguments required.
    Usage:
        lexor INPUTFILE OUTPUTFILE

    """
    print usage_str

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if ((argv_len == 3) or (argv_len == 2)):
        input_filepath = sys.argv[1]
        try:
            lex = Lexor(input_filepath)
        except IOError as ioe:
            print "Error: no such file."
            sys.exit()

        if (argv_len == 3):
            output_filepath = sys.argv[2]
            output_file = open(output_filepath, 'w')
            sys.stdout = output_file

        while True:
            try:
                tok = lex.get_token()
                if tok.get_type() == EOF:
                    break
            except LexicalError as le:
                #print "\n", e
                pretty_print_error_message(input_filepath, le)
                sys.exit()
            print tok

        if (argv_len == 3):
            output_file.close()
    else:
        usage()


