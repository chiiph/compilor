class TokenType(object):
    def __init__(self, id, name):
        self._id = id
        self._name = name

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return self._name

    def __repr__(self):
        return "TokenType(%d,%s)" % (self._id, self._name)

TT = TokenType

IDENTIFIER = TT(0, "<IDENTIFIER>")
SEPARATOR = TT(1, "<SEPARATOR>")
INT_LITERAL = TT(2, "<INT_LITERAL>")
CHAR_LITERAL = TT(0, "<CHAR_LITERAL>")
STRING_LITERAL = TT(4, "<STRING_LITERAL>")
SCOLON = TT(5, "<SCOLON>")
BRACE_OPEN = TT(6, "<BRACE_OPEN>")
BRACE_CLOSE = TT(7, "<BRACE_CLOSE>")
PAREN_OPEN = TT(8, "<PAREN_OPEN>")
PAREN_CLOSE = TT(9, "<PAREN_CLOSE>")
CLASS = TT(10, "<CLASS>")
EXTENDS = TT(11, "<EXTENDS>")
PUBLIC = TT(12, "<PUBLIC>")
PROTECTED = TT(13, "<PROTECTED>")
STATIC = TT(14, "<STATIC>")
THIS = TT(15, "<THIS>")
SUPER = TT(16, "<SUPER>")
VOID_TYPE = TT(17, "<VOID_TYPE>")
BOOLEAN_TYPE = TT(18, "<BOOLEAN_TYPE>")
INT_TYPE = TT(19, "<INT_TYPE>")
CHAR_TYPE = TT(20, "<CHAR_TYPE>")
IF = TT(21, "<IF>")
THEN = TT(22, "<THEN>")
ELSE = TT(23, "<ELSE>")
WHILE = TT(24, "<WHILE>")
RETURN = TT(25, "<RETURN>")
TRUE = TT(26, "<TRUE>")
FALSE = TT(27, "<FALSE>")
NULL = TT(28, "<NULL>")
NEW = TT(29, "<NEW>")
ASSIGNMENT = TT(30, "<ASSIGNMENT>")
CONDITIONAL_AND = TT(31, "<CONDITIONAL_AND>")
EQUALS = TT(32, "<EQUALS>")
NOT_EQUALS = TT(33, "<NOT_EQUALS>")
LT = TT(34, "<LT>")
GT = TT(35, "<GT>")
LT_EQ = TT(36, "<LT_EQ>")
GT_EQ = TT(37, "<GT_EQ>")
ADD = TT(38, "<ADD>")
SUB = TT(39, "<SUB>")
MUL = TT(40, "<MUL>")
DIV = TT(41, "<DIV>")
MOD = TT(42, "<MOD>")
NOT = TT(43, "<NOT>")
ACCESSOR = TT(44, "<ACCESSOR>")
EOF = TT(45, "<EOF>")
