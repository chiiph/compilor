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

%%

{WHITESPACE}    { }
{COMMENT}       { }
{INT_LITERAL}   { return new Symbol(sym.INT_LITERAL, new Integer(yytext())); }
{ID}            { return new Symbol(sym.ID, yytext());                       }
{EXIT}          { return new Symbol(sym.EXIT);                               }
{CLEAR}         { return new Symbol(sym.CLEAR);                              }
{SETCOLOR}      { return new Symbol(sym.SETCOLOR);                           }
{IF}            { return new Symbol(sym.IF);                                 }
{ELSE}          { return new Symbol(sym.ELSE);                               }
{REPEAT}        { return new Symbol(sym.REPEAT);                             }
{TIMES}         { return new Symbol(sym.TIMES);                              }
{DRAW}          { return new Symbol(sym.DRAW);                               }
{MOVE}          { return new Symbol(sym.MOVE);                               }
{DEF}           { return new Symbol(sym.DEF);                                }
"<-"            { return new Symbol(sym.ASSIGNMENT);                         }
"||"            { return new Symbol(sym.CONDITIONAL_OR);                     }
"&&"            { return new Symbol(sym.CONDITIONAL_AND);                    }
"=="            { return new Symbol(sym.EQUALS);                             }
"!="            { return new Symbol(sym.NOT_EQUALS);                         }
"<="            { return new Symbol(sym.LT_EQ);                              }
">="            { return new Symbol(sym.GT_EQ);                              }
";"             { return new Symbol(sym.SCOLON);                             }
","             { return new Symbol(sym.COMMA);                              }
"("             { return new Symbol(sym.PAREN_OPEN);                         }
")"             { return new Symbol(sym.PAREN_CLOSE);                        }
"<"             { return new Symbol(sym.LT);                                 }
">"             { return new Symbol(sym.GT);                                 }
"+"             { return new Symbol(sym.ADD);                                }
"-"             { return new Symbol(sym.SUB);                                }
"*"             { return new Symbol(sym.MUL);                                }
"/"             { return new Symbol(sym.DIV);                                }
"!"             { return new Symbol(sym.NOT);                                }
"_"             { return new Symbol(sym.ANGLE);                              }
.               { throw new Exception("Error léxico: " + yytext() + " en línea: " + (yyline + 1)); }
