from constants import *

class LexicalError(Exception):
    def __init__(self, tok):
        self.message = "ERROR: Line: %d, Col: %d :: Unrecognize expression: %s" % (tok.get_line(), 
                                                                                   tok.get_col(),
                                                                                   tok.get_lexeme())

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

class State:
    def __init__(self, next_chk_list, acc):
        self._next_state = next_chk_list # [ ( sig_estado, loop, lambda_checkeo ) , ... ] <-- se asume que check da True para un solo posible char de entrada en toda la lista
        self.accepts = acc

    def check(self, ch):
        for (next, loop, chk) in self._next_state:
            if chk() and next != None:
                return next
            elif chk():
                return self

        return None

    def proc(self, ch):
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
            raise Exception("error")

class Lexor:
    # States
    # se definen los estados al reves, primero vamos por los terminales hacia el inicial
    # proque ahora necesitamos el estado siguiente para definir el actual, salvo qeu sea terminal
    self._check_IDENTIFIER = lambda c: return c in string.letters+"_$"
    self.ST_IDENTIFIER = State([(None, True, self._check_IDENTIFIER), # el siguiente estado es un loop que va a si mismo (por eso el None) si se da check
                                 (None, False, lambda c: not self._checl_IDENTIFIER(c))], # o finaliza si se da lo contrario de check
                                True) # si esto estuviera en False, el caso de arriba daria un error

    self._check_ZERO = lambda c: return c == "0"
    self.ST_ZERO_LITERAL = State([(None, True, self._check_IDENTIFIER),
                                  (None, False, lambda c: not self._check_ZERO(c))],
                                 True)

    self._check_INT = lambda c: return c in range(1,10)
    self.ST_INT_LITERAL = State([(None, True, self._check_INT),
                                 (None, False, lambda c: not self._check_INT(c))],
                                True)

    self.ST_INITIAL = State([(self.ST_IDENTIFIER, False, self._check_IDENTIFIER),
                          (self.ST_ZERO_LITERAL, False, self._check_ZERO)],
                          False)

    self._whitespace = frozenset([ " ", "\n", "\r", "\t" ])

    def __init__(self):
        self._cursor = 0
        self._line   = 1
        self._col    = 0
        self._state  = self.ST_INITIAL
        self._current_token = Token()
        self._current_char  = ""

    def get_token(self):
        # todas las vueltas, se empieza desde el estado inicial
        self._state = self.ST_INITIAL
        # se limpia el token
        self._current_token = Token()
        # si es el primer token, levanta un char
        if self._current_char == "":
            self._current_char = self._next_char()
        # dado este caracter, decime si hay una transicion posible
        # y devolveme el estado al que saltar
        self._state = self._state.proc(self._current_char)
        # mientras exista un estado al cual saltar
        while self._state != None:
            # entonces el char leido es valido, appendealo al token actual
            self._current_token.append(self._current_char)
            # agarra un char nuevo
            self._current_char = self._next_char()
            # y fijate si hay un siguiente estado
            self._state = self._state.proc(self._current_char)
        # si es none, y todavia estamos aca, es porque acepto
        if self._state == None:
            return self._current_token
   
    def _next_char(self):
        # eat self._whitespace
        # increment self._line when \n is found and set self._col = 0
        # increment self._col otherwise
        # blabla yield char
        pass
