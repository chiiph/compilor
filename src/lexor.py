from constants import *
from states import *

import os, re

class Token(object):
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
        return "%d:%d\t-\t%s\t:: %s" % (self._line, self._col, self._type, self._lexeme)

class Lexor(object):
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
        self._cursor = -1
        self._file_data = self._file.read()
        self._one_sep = False
        self._maybe_start_comment = False

        self._remove_comments()

    def __del__(self):
        self._file.close()

    def _replacer(self, match):
        st = match.group()
        retcount = st.count("\n")
        return " "*(len(st)-retcount)+"\n"*retcount

    def _remove_comments(self):
        regex = re.compile("(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?",
                        re.DOTALL | re.MULTILINE)
        tmp = regex.sub(self._replacer, self._file_data)
        self._file_data = tmp

    def get_token(self):
        self._state = ST_INITIAL
        self._current_token = Token()

        if len(self._current_char) == 0:
            self._current_char = self._next_char()

        self._current_token._line = self._line
        if self._col > 0:
            self._current_token._col = self._col-1

        # si a esta altura el current_char es "" entonces estamos
        # en EOF
        if len(self._current_char) == 0:
            # TODO: cambiar por un set_type()
            self._current_token._type = EOF
            return self._current_token

        self._state = self._state.proc(self._current_char,
                                       self._line,
                                       self._col-len(self._current_token.get_lexeme())-1)
        while self._state != None:
            self._current_token.append(self._current_char)
            self._current_token._type = self._state.get_token_type()

            self._current_char = self._next_char()
            self._state = self._state.proc(self._current_char,
                                           self._line,
                                           self._col-len(self._current_token.get_lexeme())-1)

        if self._current_token.get_lexeme() in reserved_words.keys():
            self._current_token._type = reserved_words[self._current_token.get_lexeme()]
        return self._current_token

    def _real_next_char(self):
        self._cursor += 1
        if self._cursor >= len(self._file_data):
            return ""
        return self._file_data[self._cursor]

    def _next_char(self):
        ch = self._real_next_char()
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
            ch = self._real_next_char()
            self._col += 1

        if ch == "/":
            if self._cursor+1 < len(self._file_data):
                if self._file_data[self._cursor+1] == "*":
                    raise LexicalError(self._line, self._col-1,
                                       "Comentario no cerrado.")
        if ch == "*":
            if self._cursor+1 < len(self._file_data):
                if self._file_data[self._cursor+1] == "/":
                    raise LexicalError(self._line, self._col-1,
                                       "Comentario que no ha sido abierto.")

        self._one_sep = False

        return ch
