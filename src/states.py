import string

from constants import *

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

    def proc(self, ch):
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
            print nst, self.accepts, self._token_type, repr(ch)
            raise LexicalError(0,0)

    def get_token_type(self):
        return self._token_type

_check_IDENTIFIER = lambda c: c in string.ascii_letters+"_$"
_check_rest_IDENTIFIER = lambda c: c in string.ascii_letters+string.digits+"_$"
ST_IDENTIFIER = State([(None, True, _check_rest_IDENTIFIER)],
                       True, IDENTIFIER)

_check_ZERO = lambda c: c == "0"
ST_ZERO_LITERAL = State([], True, INT_LITERAL)

_check_INT = lambda c: c in str(range(1,10))
_check_rest_INT = lambda c: c in str(range(0,10))
ST_INT_LITERAL = State([(None, True, _check_rest_INT)],
                       True, INT_LITERAL)

_check_SEPARATOR = lambda c: c in [" ","."]
ST_SEPARATOR = State([], True, SEPARATOR)

_check_EQUALS = lambda c: c == "="
ST_EQUALS = State([], True, EQUALS)
ST_ASSIGNMENT = State([(ST_EQUALS, False, _check_EQUALS)], True, ASSIGNMENT)

ST_INITIAL = State([(ST_IDENTIFIER, False, _check_IDENTIFIER),
                    (ST_ZERO_LITERAL, False, _check_ZERO),
                    (ST_SEPARATOR, False, _check_SEPARATOR),
                    (ST_INT_LITERAL, False, _check_INT),
                    (ST_ASSIGNMENT, False, _check_EQUALS)],
                   False, None)
