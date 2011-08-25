from lexor import *
from constants import *

if __name__ == "__main__":
    lex = Lexor("test.java")
    while True:
        tok = lex.get_token()
        if tok.get_type() == EOF:
            break

        print tok
