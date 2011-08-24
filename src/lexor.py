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

class Lexor:
    # States
    self.ST_INITIAL        = 0
    self.ST_IDENTIFIER     = 1
    self.ST_ESCAPE_CHAR    = 2
    self.ST_ZERO_LITERAL   = 3
    self.ST_INT_LITERAL    = 4
    self.ST_CHAR_LITERAL   = 5
    self.ST_CHAR_1         = 6
    self.ST_CHAR_2         = 7
    self.ST_CHAR_3         = 8
    self.ST_STRING_LITERAL = 9
    self.ST_STRING_1       = 10
    self.ST_STRING_2       = 11
    self.ST_EOF            = 12

    self._acceptors = [ self.ST_IDENTIFIER
                      , self.ST_ESCAPE_CHAR 
                      , self.ST_ZERO_LITERAL
                      , self.ST_INT_LITERAL 
                      , self.ST_CHAR_LITERAL  
                      , self.ST_STRING_LITERAL
                      , self.ST_EOF           
                      ]

    self._whitespace = frozenset([ " ", "\n", "\r", "\t" ])

    def __init__(self):
        self._cursor = 0
        self._line   = 1
        self._col    = 0
        self._state  = self.INITIAL
        self._current_token = Token()
        self._current_char  = ""

    def get_token(self):
        self._state = self.INITIAL
        while (True):
            self._current_char = self._next_char()
            if   ((self._state == self.INITIAL) and (self._current_char in string.letters + "_$"))):
                print "state:", self._state, " current_char:", self._current_char
                self._state = self.ST_IDENTIFIER
                self._current_token.append(self._current_char)
            #elif ((self._state == self.INITIAL) and (self._current_char in ". \t\n\r")):
            #    self._state = self.ST_ESCAPE_CHAR
            #    self._current_token.append(self._current_char)
            elif ((self._state == self.INITIAL) and (self._current_char in "0")):
                self._state = self.ST_ZERO_LITERAL
                self._current_token.append(self._current_char)
            elif ((self._state == self.INITIAL) and (self._current_char in "123456789")):
                self._state = self.ST_INT_LITERAL
                self._current_token.append(self._current_char)
            elif ((self._state == self.INITIAL) and (self._current_char in "\'")):
                self._state = self.ST_CHAR_1
                self._current_token.append(self._current_char)
            elif ((self._state == self.INITIAL) and (self._current_char in "\"")):
                self._state = self.ST_STRING_1
                self._current_token.append(self._current_char)
            elif ((self._state == self.INITIAL) and (self._current_char in "")):
                self._state = self.ST_EOF
                self._current_token.append(self._current_char)
            elif ((self._state == self.ST_IDENTIFIER) and (self._current_char not in self._whitespace) and (self._current_char in string.letters + "_$")):
                self._current_token.append(self._current_char)
            elif ((self._state == self.ST_IDENTIFIER) and (self._current_char in self._whitespace)):
                return self._current_token
            #elif (self._state == self.ST_ESCAPE_CHAR):
            #    return self._current_token
            elif ((self._state == self.ST_) and (self._current_char in )):
                self._current_token.append(self._current_char)
            elif ((self._state == self.) and (self._current_char in )):
                self._current_token.append(self._current_char)
            elif ((self._state == self.) and (self._current_char in )):
                self._current_token.append(self._current_char)
                return self._current_token
            else:
                raise LexicalException(self._current_token)

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
