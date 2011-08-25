from lexor import *
from constants import *
from errors import LexicalError

if __name__ == "__main__":
    lex = Lexor("test.java")
    while True:
        try:
            tok = lex.get_token()
            if tok.get_type() == EOF:
                break
        except LexicalError as e:
            print "\n", e
            quit()

        print tok
