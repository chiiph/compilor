import sys
from lexor     import *
from constants import *
from errors    import LexicalError

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
        input_filepath  = sys.argv[1]
        try:
            lex = Lexor(input_filepath)
        except IOError as ioe:
            print "Error: no such file."
            quit()
        
        if (argv_len == 3):
            output_filepath = sys.argv[2]
            output_file = open(output_filepath, 'w')
            sys.stdout = output_file

        while True:
            try:
                tok = lex.get_token()
                if tok.get_type() == EOF:
                    break
            except LexicalError as e:
                print "\n", e
                quit()
            print tok
        
        if (argv_len == 3):
            output_file.close()
    else:
        usage()


