from constants import *

class LexicalError(Exception):
    def __init__(self, tok):
        self.message = "ERROR: Line: %d, Col: %d :: Unrecognize expression: %s" % (tok.get_line(), 
                                                                                   tok.get_col(),
                                                                                   tok.get_lexeme())

class Token:
    def __init__(self):
        self._lexeme = ""
        self._line = 1
        self._col = 0
        self._type = 0

    def append(self, ch):
        self._lexeme += ch

    def get_line(self):
        return self._line

    def get_col(self):
        return self._col

    def get_lexeme(self):
        return self._lexeme

class Lexor:
    # States
    self.INITIAL = 0
    self.START_SCOLON = 1
    self.END_SCOLON = 2

    self._states = { self.INITIAL : self._initial,
                     self.START_SCOLON : self._start_scolon }

    self._acceptors = [ self.END_SCOLON ]

    # Transitions <state> : (char to read, next state)
    self._transitions = { self.INITIAL : { "" : self.START_COLON }, # all dummy!
                          self.START_COLON : { ";", self.END_SCOLON } }

    self._whitespace = [ " ", "\n", "\r", "\t" ]

    def __init__(self):
        self._cursor = 0
        self._line = 1
        self._col = 0
        self._state = self.INITIAL
        self._current_token = Token()
        self._current_char = ""

    def get_token(self):
        if self._state in self._acceptors:
            return self._current_token
        else:
            self._current_char = self._next_char()
            try:
                new_state = self._transitions[self._state][self._current_char]
                self._current_token.append(self._current_char):
                return self._states[trans_new_state[1]]()
            except:
                raise LexicalException(self._current_token)
    
    def _next_char(self):
        # eat self._whitespace
        # increment self._line when \n is found and set self._col = 0
        # increment self._col otherwise
        # blabla yield char
        pass

    def _initial(self):
       pass 
