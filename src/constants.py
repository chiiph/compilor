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

IDENTIFIER      = TT( 0, "<IDENTIFIER>")
COMMA           = TT( 1, "<COMMA>")
INT_LITERAL     = TT( 2, "<INT_LITERAL>")
CHAR_LITERAL    = TT( 3, "<CHAR_LITERAL>")
STRING_LITERAL  = TT( 4, "<STRING_LITERAL>")
SCOLON          = TT( 5, "<SCOLON>")
BRACE_OPEN      = TT( 6, "<BRACE_OPEN>")
BRACE_CLOSE     = TT( 7, "<BRACE_CLOSE>")
PAREN_OPEN      = TT( 8, "<PAREN_OPEN>")
PAREN_CLOSE     = TT( 9, "<PAREN_CLOSE>")
CLASS           = TT(10, "<CLASS>")
EXTENDS         = TT(11, "<EXTENDS>")
PUBLIC          = TT(12, "<PUBLIC>")
PROTECTED       = TT(13, "<PROTECTED>")
STATIC          = TT(14, "<STATIC>")
THIS            = TT(15, "<THIS>")
SUPER           = TT(16, "<SUPER>")
VOID_TYPE       = TT(17, "<VOID_TYPE>")
BOOLEAN_TYPE    = TT(18, "<BOOLEAN_TYPE>")
INT_TYPE        = TT(19, "<INT_TYPE>")
CHAR_TYPE       = TT(20, "<CHAR_TYPE>")
IF              = TT(21, "<IF>")
ELSE            = TT(22, "<ELSE>")
WHILE           = TT(23, "<WHILE>")
RETURN          = TT(24, "<RETURN>")
TRUE            = TT(25, "<TRUE>")
FALSE           = TT(26, "<FALSE>")
NULL            = TT(27, "<NULL>")
NEW             = TT(28, "<NEW>")
ASSIGNMENT      = TT(29, "<ASSIGNMENT>")
CONDITIONAL_AND = TT(30, "<CONDITIONAL_AND>")
CONDITIONAL_OR  = TT(31, "<CONDITIONAL_OR>")
EQUALS          = TT(31, "<EQUALS>")
NOT_EQUALS      = TT(32, "<NOT_EQUALS>")
LT              = TT(33, "<LT>")
GT              = TT(34, "<GT>")
LT_EQ           = TT(35, "<LT_EQ>")
GT_EQ           = TT(36, "<GT_EQ>")
ADD             = TT(37, "<ADD>")
SUB             = TT(38, "<SUB>")
MUL             = TT(39, "<MUL>")
DIV             = TT(40, "<DIV>")
MOD             = TT(41, "<MOD>")
NOT             = TT(42, "<NOT>")
ACCESSOR        = TT(43, "<ACCESSOR>")
EOF             = TT(44, "<EOF>")
REF_TYPE        = TT(45, "<REF_TYPE>")

reserved_words = { "class"      : CLASS
                 , "extends"    : EXTENDS
                 , "public"     : PUBLIC
                 , "protected"  : PROTECTED
                 , "static"     : STATIC
                 , "this"       : THIS
                 , "super"      : SUPER
                 , "void"       : VOID_TYPE
                 , "boolean"    : BOOLEAN_TYPE
                 , "int"        : INT_TYPE
                 , "char"       : CHAR_TYPE
                 , "if"         : IF
                 , "else"       : ELSE
                 , "while"      : WHILE
                 , "return"     : RETURN
                 , "true"       : TRUE
                 , "false"      : FALSE
                 , "null"       : NULL
                 , "new"        : NEW
                 }
