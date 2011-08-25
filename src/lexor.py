from constants import *
from states import *

class LexicalError(Exception):
    def __init__(self, line, col):
        self.message = "ERROR: Line: %d, Col: %d :: Unrecognize token." % (line, col)

class Token:
    def __init__(self):
        self._lexeme = ""
        self._line   = 1
        self._col    = 0
        self._type   = 0

    def append(self, ch):
        self._lexeme += ch

    def get_line(self):
        return self._line

    def get_col(self):
        return self._col

    def get_lexeme(self):
        return self._lexeme

    def get_type(self):
        return self._type

    def __str__(self):
        return "%d:%d - %d :: %s" % (self._line, self._col, self._type, self._lexeme)

class Lexor:
    _whitespace = frozenset([ " ", "\n", "\r", "\t" ])

    def __init__(self, file_path):
        self._cursor = 0
        self._line   = 1
        self._col    = 0
        self._state  = ST_INITIAL
        self._current_token = Token()
        self._current_char  = ""
        self._file_path = file_path
        self._file = open(self._file_path, "r")
        self._one_sep = False

    def get_token(self):
        self._state = ST_INITIAL
        self._current_token = Token()

        if len(self._current_char) == 0:
            self._current_char = self._next_char()

        self._current_token._line = self._line
        self._current_token._col = self._col

        # si a esta altura el current_char es "" entonces estamos
        # en EOF
        if len(self._current_char) == 0:
            # TODO: cambiar por un set_type()
            self._current_token._type = EOF
            print "EOF!"
            return self._current_token

        self._state = self._state.proc(self._current_char)
        while self._state != None:
            self._current_token.append(self._current_char)
            self._current_token._type = self._state.get_token_type()

            self._current_char = self._next_char()

            self._state = self._state.proc(self._current_char)

        if self._state == None:
            return self._current_token

    def _next_char(self):
        ch = self._file.read(1)
        self._col += 1

        if ch in self._whitespace and not self._one_sep:
            self._one_sep = True
            if ch == "\n":
                self._line += 1
                self._col = 0
            return " "

        while ch in self._whitespace:
            if ch == "\n":
                self._line += 1
                self._col = 0
            ch = self._file.read(1)
            self._col += 1

        self._one_sep = False
        return ch
