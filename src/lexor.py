from constants import *
from states import *
from errors import *

import os, re

def isToken(obj):
    return isinstance(obj, Token)

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

    def __init__(self, file_path, system_classes = ""):
        self._cursor = 0
        self._line   = 1
        self._col    = 0
        self._state  = ST_INITIAL
        self._current_token = Token()
        self._current_char  = ""
        self._file_path = file_path
        self._file = open(self._file_path, "r")
        self._cursor = -1
        self._file_data = system_classes + self._file.read()
        self._one_sep = False
        self._maybe_start_comment = False
        self._prev_token = None

        self._remove_comments()

        self._is_string = False

    def __del__(self):
        self._file.close()

    def _replacer(self, match):
        st = match.group()
        spl = st.split("\n")
        res = []
        for spl_st in spl:
            res.append(" "*len(spl_st))
        return "\n".join(res)

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
            self._prev_token = self._current_token
            return self._current_token

        if self._current_char == " ":
            self._current_char = self._next_char()
            if len(self._current_char) == 0:
                # TODO: cambiar por un set_type()
                self._current_token._type = EOF
                self._prev_token = self._current_token
                return self._current_token
            self._prev_token = None

        self._state = self._state.proc(self._current_char,
                                       self._line,
                                       self._col-len(self._current_token.get_lexeme())-1)
        self._is_string = False
        if self._current_char == "\"":
            self._is_string = True

        while self._state != None:

            if len(self._current_char) == 0:
                self._current_token._type = EOF
                self._prev_token = self._current_token
                return self._current_token

            self._current_token.append(self._current_char)
            self._current_token._type = self._state.get_token_type()

            self._current_char = self._next_char()

            if self._current_char == "\"" and self._is_string:
                self._is_string = False

            self._state = self._state.proc(self._current_char,
                                           self._line,
                                           self._col-len(self._current_token.get_lexeme())-1)

        if self._current_token.get_lexeme() in reserved_words.keys():
            self._current_token._type = reserved_words[self._current_token.get_lexeme()]

        if self._prev_token != None:
            prev_token_type = self._prev_token.get_type()
            error_condition = ((  prev_token_type == INT_LITERAL
                               or prev_token_type == CHAR_LITERAL
                               or prev_token_type == STRING_LITERAL
                               ) and self._current_token.get_type() == IDENTIFIER)
            if (error_condition):
                if (prev_token_type == INT_LITERAL):
                    raise LexicalError(self._current_token.get_line(), self._current_token.get_col(), "Entero mal formado.")
                elif (prev_token_type == CHAR_LITERAL):
                    raise LexicalError(self._current_token.get_line(), self._current_token.get_col(), "Literal de caracter seguido por un identificador.")
                elif (prev_token_type == STRING_LITERAL):
                    raise LexicalError(self._current_token.get_line(), self._current_token.get_col(), "Literal de string seguido por un identificador.")
                else:
                    print "prev",self._prev_token.get_type()
                    print "curr",self._current_token.get_type()
                    print prev_token_type == INT_LITERAL
                    print prev_token_type == CHAR_LITERAL
                    print prev_token_type == STRING_LITERAL
                    print self._current_token.get_type() == IDENTIFIER
                    raise LexicalError(self._current_token.get_line(), self._current_token.get_col(), "Error desconocido.")
        self._prev_token = self._current_token
        return self._current_token

    def _real_next_char(self):
        self._cursor += 1
        if self._cursor >= len(self._file_data):
            return ""
        return self._file_data[self._cursor]

    def _next_char(self):
        ch = self._real_next_char()
        if len(ch) == 0:
            return ""
        self._col += 1

        if self._is_string:
            return ch

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
            if len(ch) == 0:
                return ""
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
