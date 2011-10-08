package Proyecto2;
import java_cup.runtime.Symbol;

%%

%line
%ignorecase
%cup

%yylexthrow{ Exception
%yylexthrow}

WHITESPACE  = [ \t\r\n\f ]+
COMMENT     = "/*"[.]*"*/"
INT_LITERAL = [0-9]+
ID          = [a-zA-Z][a-zA-Z0-9]*
EXIT        = EXIT
CLEAR       = CLEAR
SETCOLOR    = SETCOLOR
IF          = IF
ELSE        = ELSE
REPEAT      = REPEAT
TIMES       = TIMES
DRAW        = DRAW
MOVE        = MOVE
DEF         = DEF
ANGLE_SYM   = D
%%

{WHITESPACE}    { }
{COMMENT}       { }
"<-"            { return new Symbol(sym.ASSIGNMENT, yyline, 0);                         }
"||"            { return new Symbol(sym.CONDITIONAL_OR, yyline, 0);                     }
"&&"            { return new Symbol(sym.CONDITIONAL_AND, yyline, 0);                    }
"=="            { return new Symbol(sym.EQUALS, yyline, 0);                             }
"!="            { return new Symbol(sym.NOT_EQUALS, yyline, 0);                         }
"<="            { return new Symbol(sym.LT_EQ, yyline, 0);                              }
">="            { return new Symbol(sym.GT_EQ, yyline, 0);                              }
";"             { return new Symbol(sym.SCOLON, yyline, 0);                             }
","             { return new Symbol(sym.COMMA, yyline, 0);                              }
"("             { return new Symbol(sym.PAREN_OPEN, yyline, 0);                         }
")"             { return new Symbol(sym.PAREN_CLOSE, yyline, 0);                        }
"<"             { return new Symbol(sym.LT, yyline, 0);                                 }
">"             { return new Symbol(sym.GT, yyline, 0);                                 }
"+"             { return new Symbol(sym.ADD, yyline, 0);                                }
"-"             { return new Symbol(sym.SUB, yyline, 0);                                }
"*"             { return new Symbol(sym.MUL, yyline, 0);                                }
"/"             { return new Symbol(sym.DIV, yyline, 0);                                }
"!"             { return new Symbol(sym.NOT, yyline, 0);                                }
{EXIT}          { return new Symbol(sym.EXIT, yyline, 0);                               }
{CLEAR}         { return new Symbol(sym.CLEAR, yyline, 0);                              }
{SETCOLOR}      { return new Symbol(sym.SETCOLOR, yyline, 0);                           }
{IF}            { return new Symbol(sym.IF, yyline, 0);                                 }
{ELSE}          { return new Symbol(sym.ELSE, yyline, 0);                               }
{REPEAT}        { return new Symbol(sym.REPEAT, yyline, 0);                             }
{TIMES}         { return new Symbol(sym.TIMES, yyline, 0);                              }
{DRAW}          { return new Symbol(sym.DRAW, yyline, 0);                               }
{MOVE}          { return new Symbol(sym.MOVE, yyline, 0);                               }
{DEF}           { return new Symbol(sym.DEF, yyline, 0);                                }
{INT_LITERAL}   { return new Symbol(sym.INT_LITERAL, yyline, 0, new Integer(yytext())); }
{ANGLE_SYM}     { return new Symbol(sym.ANGLE, yyline, 0);                              }
{ID}            { return new Symbol(sym.ID, yyline, 0, yytext());                       }
.               { throw new Exception("Error léxico: " + yytext() + " en línea: " + (yyline + 1)); }
