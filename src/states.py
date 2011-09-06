import string

from constants import *
from errors import *

class State(object):
    def __init__(self, next_chk_list, acc, tok_type):
        self._next_state = next_chk_list # [ ( sig_estado, loop, lambda_checkeo ) , ... ]
        self.accepts = acc
        self._token_type = tok_type

    def check(self, ch):
        for (next, loop, chk) in self._next_state:
            if chk != None:
                if chk(ch) and next != None:
                    return next
                elif chk(ch) and loop:
                    return self
                elif chk(ch):
                    raise Exception("Estado mal definido.")

        return None

    def proc(self, ch, line = 0, col = 0):
        if len(ch) == 0 and not self.accepts:
            raise LexicalError(line,col)

        if len(ch) == 0:
            return None

        nst = self.check(ch)
        # si es aceptador y se termino lo buscado ent retorna todo bien
        if self.accepts and nst == None:
            return None
        # si hay una transicion siguiente
        # ya sea porque no acepta o porque todavia queda algo del token por leer
        # retorna el estado por el que hay que seguir
        elif nst != None:
            return nst
        # sino algo malo paso
        else:
            raise LexicalError(line, col)

    def get_token_type(self):
        return self._token_type

_check_IDENTIFIER           = lambda c: c in string.ascii_letters+"_$"
_check_rest_IDENTIFIER      = lambda c: c in string.ascii_letters+string.digits+"_$"
ST_IDENTIFIER               = State([(None, True, _check_rest_IDENTIFIER)], True, IDENTIFIER)

_check_ZERO                 = lambda c: c == "0"
ST_ZERO_LITERAL             = State([], True, INT_LITERAL)

_check_INT                  = lambda c: c in string.digits[1:]
_check_rest_INT             = lambda c: c in string.digits
ST_INT_LITERAL              = State([(None, True, _check_rest_INT)], True, INT_LITERAL)

_check_COMMA                = lambda c: c in [","]
ST_COMMA                    = State([], True, COMMA)

_check_CHAR_QUOTE           = lambda c: c == "\'"
_check_CHAR                 = lambda c: (c in string.printable and c != "\\" and c != "\'")
_check_ESCAPED_CHAR_START   = lambda c: c == "\\"
_check_ESCAPED_CHAR_END     = lambda c: c in "\\\'\"n"
ST_CHAR_QUOTE_END           = State([], True, CHAR_LITERAL)
ST_CHAR_END                 = State([(ST_CHAR_QUOTE_END, False, _check_CHAR_QUOTE)], False, None)
ST_ESCAPED_CHAR             = State([(ST_CHAR_END,      False, _check_ESCAPED_CHAR_END)], False, None)
ST_CHAR_QUOTE               = State([ (ST_CHAR_END,     False, _check_CHAR)
                                    , (ST_ESCAPED_CHAR, False, _check_ESCAPED_CHAR_START)
                                    ], False, None)

_check_STRING_QUOTE         = lambda c: c == "\""
_check_STRING_CHAR          = lambda c: (c in string.printable and c != "\\" and c != "\"" and c != "\n")
ST_STRING_END               = State([], True, STRING_LITERAL)
ST_STRING_START             = State([], False, None) # Hack
ST_ESCAPED_CHAR             = State([(ST_STRING_START, False, _check_ESCAPED_CHAR_END)], False, None)
ST_STRING_START._next_state = [ (None, True, _check_STRING_CHAR)
                              , (ST_ESCAPED_CHAR, False, _check_ESCAPED_CHAR_START)
                              , (ST_STRING_END, False, _check_STRING_QUOTE)
                              ]

_check_EQUALS               = lambda c: c == "="
ST_EQUALS                   = State([], True, EQUALS)
ST_ASSIGNMENT               = State([(ST_EQUALS, False, _check_EQUALS)], True, ASSIGNMENT)

_check_SCOLON               = lambda c: c == ";"
ST_SCOLON                   = State([], True, SCOLON)

_check_BRACE_OPEN           = lambda c: c == "{"
ST_BRACE_OPEN               = State([], True, BRACE_OPEN)

_check_BRACE_CLOSE          = lambda c: c == "}"
ST_BRACE_CLOSE              = State([], True, BRACE_CLOSE)

_check_PAREN_OPEN           = lambda c: c == "("
ST_PAREN_OPEN               = State([], True, PAREN_OPEN)

_check_PAREN_CLOSE          = lambda c: c == ")"
ST_PAREN_CLOSE              = State([], True, PAREN_CLOSE)

_check_LT                   = lambda c: c == "<"
ST_LT_EQ                    = State([], True, LT_EQ)
ST_LT                       = State([(ST_LT_EQ, False, _check_EQUALS)], True, LT)

_check_GT                   = lambda c: c == ">"
ST_GT_EQ                    = State([], True, GT_EQ)
ST_GT                       = State([(ST_GT_EQ, False, _check_EQUALS)], True, GT)

_check_ADD                  = lambda c: c == "+"
ST_ADD                      = State([], True, ADD)

_check_SUB                  = lambda c: c == "-"
ST_SUB                      = State([], True, SUB)

_check_MUL                  = lambda c: c == "*"
ST_MUL                      = State([], True, MUL)

_check_DIV                  = lambda c: c == "/"
ST_DIV                      = State([], True, DIV)

_check_MOD                  = lambda c: c == "%"
ST_MOD                      = State([], True, MOD)

_check_NOT                  = lambda c: c == "!"
ST_NOT_EQUALS               = State([], True, NOT_EQUALS)
ST_NOT                      = State([(ST_NOT_EQUALS, False, _check_EQUALS)], True, NOT)

_check_ACCESSOR             = lambda c: c == "."
ST_ACCESSOR                 = State([], True, ACCESSOR)

_check_AMP                  = lambda c: c == "&"
ST_CONDITIONAL_AND_END      = State([], True, CONDITIONAL_AND)
ST_CONDITIONAL_AND          = State([(ST_CONDITIONAL_AND_END, False, _check_AMP)], False, None)

_check_PIPE                 = lambda c: c == "|"
ST_CONDITIONAL_OR_END       = State([], True, CONDITIONAL_OR)
ST_CONDITIONAL_OR           = State([(ST_CONDITIONAL_OR_END, False, _check_PIPE)], False, None)

ST_INITIAL                  = State([ (ST_IDENTIFIER,       False, _check_IDENTIFIER)
                                    , (ST_ZERO_LITERAL,     False, _check_ZERO)
                                    , (ST_COMMA,            False, _check_COMMA)
                                    , (ST_INT_LITERAL,      False, _check_INT)
                                    , (ST_ASSIGNMENT,       False, _check_EQUALS)
                                    , (ST_CHAR_QUOTE,       False, _check_CHAR_QUOTE)
                                    , (ST_STRING_START,     False, _check_STRING_QUOTE)
                                    , (ST_SCOLON,           False, _check_SCOLON)
                                    , (ST_BRACE_OPEN,       False, _check_BRACE_OPEN)
                                    , (ST_BRACE_CLOSE,      False, _check_BRACE_CLOSE)
                                    , (ST_PAREN_OPEN,       False, _check_PAREN_OPEN)
                                    , (ST_PAREN_CLOSE,      False, _check_PAREN_CLOSE)
                                    , (ST_LT,               False, _check_LT)
                                    , (ST_GT,               False, _check_GT)
                                    , (ST_ADD,              False, _check_ADD)
                                    , (ST_SUB,              False, _check_SUB)
                                    , (ST_MUL,              False, _check_MUL)
                                    , (ST_DIV,              False, _check_DIV)
                                    , (ST_MOD,              False, _check_MOD)
                                    , (ST_NOT,              False, _check_NOT)
                                    , (ST_ACCESSOR,         False, _check_ACCESSOR)
                                    , (ST_CONDITIONAL_AND,  False, _check_AMP)
                                    , (ST_CONDITIONAL_OR,   False, _check_PIPE)
                                    ],
                                    False,
                                    None)
