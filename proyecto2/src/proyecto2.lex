pacakge Proyecto2;
import java_cup.runtime.Symbol;

%%

%debug
%line
%column
%char
%ignorecase
%cup

WHITESPACE  = [ \t\r\n\f ]+
INT_LITERAL = [0-9]+
ID          = [a-zA-Z][a-zA-Z0-9]*

%%

{WHITESPACE}    = { }
{INT_LITERAL}   = { return new Symbol(sym.INT_LITERAL, new Integer(yytext())) }
{ID}            = { return new Symbol(sym.ID, yytext()) }
"exit"          = { return new Symbol(sym.EXIT) }
"clear"         = { return new Symbol(sym.CLEAR) }
"setcolor"      = { return new Symbol(sym.SETCOLOR) } 
"if"            = { return new Symbol(sym.IF) } 
"else"          = { return new Symbol(sym.ELSE) } 
"repeat"        = { return new Symbol(sym.REPEAT) } 
"times"         = { return new Symbol(sym.TIMES) } 
"draw"          = { return new Symbol(sym.DRAW) } 
"move"          = { return new Symbol(sym.MOVE) }  
"def"           = { return new Symbol(sym.DEF) }
";"             = { return new Symbol(sym.SCOLON) }
","             = { return new Symbol(sym.COMMA) }
"<-"            = { return new Symbol(sym.ASSIGNMENT) }
"("             = { return new Symbol(sym.PAREN_OPEN) }
")"             = { return new Symbol(sym.PAREN_CLOSE) }
"||"            = { return new Symbol(sym.CONDITIONAL_OR) }
"&&"            = { return new Symbol(sym.CONDITIONAL_AND) }
"=="            = { return new Symbol(sym.EQUALS) }
"!="            = { return new Symbol(sym.NOT_EQUALS) }
"<"             = { return new Symbol(sym.LT) }
">"             = { return new Symbol(sym.GT) }
"<="            = { return new Symbol(sym.LT_EQ) } 
">="            = { return new Symbol(sym.GT_EQ) } 
"+"             = { return new Symbol(sym.ADD) } 
"-"             = { return new Symbol(sym.SUB) }  
"*"             = { return new Symbol(sym.MUL) } 
"/"             = { return new Symbol(sym.DIV) } 
"!"             = { return new Symbol(sym.NOT) } 
"°"             = { return new Symbol(sym.ANGLE) }  
.               = { throw new Exception("Error léxico: " + yytext() + " en línea: " + (yyline + 1)) }
