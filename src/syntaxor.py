from lexor import Lexor
from constants import *
from firsts import *
from errors import SyntaxError

from traceback import *

class Syntaxor(object):
    def __init__(self, path):
        self._lexor = Lexor(path)
        self._current_token = None

    def check_syntax(self):
        self.compilation_unit()

    def update_token(self):
        self._current_token = self._lexor.get_token()

    def tok(self, tokentype):
        return self._current_token.get_type() == tokentype

    def compilation_unit(self):
        self.type_declarations()

    def type_declarations(self):
        self.update_token()
        if self.tok(PUBLIC):
            self.class_declaration()
            self.type_declarations()
        elif self.tok(EOF):
            return # LAMBDA
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Las declaraciones de clases deben comenzar con el keyword public.")

    def class_declaration(self):
        # si entre aca es porque el current es PUBLIC
        # asi que busco CLASS ahora
        self.update_token()
        if self.tok(CLASS):
            # y despues IDENTIFIER
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                self.rest_class_declaration()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe especificar un nombre para la clase, %s no es valido." %
                                  self._current_token.get_lexeme())
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "La palabra clave class debe ser especificada luego de public.")

    def rest_class_declaration(self):
        if self.tok(BRACE_OPEN):
            self.class_body()
        elif self.tok(EXTENDS):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                self.class_body()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe especificar un identificador de la clase de la cual se hereda.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba una { o la palabra clave extends.")

    def class_body(self):
        if self.tok(BRACE_OPEN):
            self.update_token()
            self.rest_class_body()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba una {.")

    def rest_class_body(self):
        if self.tok(BRACE_CLOSE):
            return
        else:
            self.class_body_declarations()
            #self.update_token() # buscamos el BRACE_CLOSE
            if self.tok(BRACE_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba una } como cierre de la clase.")

    def class_body_declarations(self):
        self.class_body_declaration()
        #self.update_token()
        self.rest_class_body_declarations()

    def rest_class_body_declarations(self):
        # si hay mas class body declaration
        if self._current_token.get_type() in FIRST_class_body_declaration:
            self.class_body_declarations()
        # sino, vamos por lambda

    def class_body_declaration(self):
        self.field_modifiers()
        #self.update_token()
        self.rest_class_body_declaration()

    def rest_class_body_declaration(self):
        if self._current_token.get_type() in FIRST_primitive_type:
            self.primitive_type()
            self.update_token()
            self.declarators()
        elif self.tok(VOID_TYPE):
            self.update_token()
            self.declarators()
        elif self.tok(IDENTIFIER):
            self.update_token()
            self.rest2_class_body_declaration()

    def rest2_class_body_declaration(self):
        if self._current_token.get_type() in FIRST_constructor_declarator:
            self.constructor_declarator()
            self.update_token()
            self.constructor_body()
        elif self.tok(IDENTIFIER):
            self.declarators()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un identificador o un (.")

    def constructor_declarator(self):
        if self.tok(PAREN_OPEN):
            self.update_token()
            self.rest_constructor_declarator()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Luego del nombre del constructor se deben especificar los parametros. Se esperaba leer un (.")

    def rest_constructor_declarator(self):
        if self.tok(PAREN_CLOSE):
            return
        else:
            self.formal_parameter_list()
            #self.update_token()
            if self.tok(PAREN_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ) como cierre de los parametros del constructor.")

    def formal_parameter_list(self):
        self.formal_parameter()
        self.update_token()
        self.rest_formal_parameter_list()

    def rest_formal_parameter_list(self):
        if self.tok(COMMA):
            self.update_token()
            self.formal_parameter_list()
        # sino vamos por lambda

    def formal_parameter(self):
        self.type()
        self.update_token()
        if self.tok(IDENTIFIER):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba encontrar un nombre para el parametro, %s no es valido." %
                              self._current_token.get_lexeme())

    def constructor_body(self):
        if self.tok(BRACE_OPEN):
            self.update_token()
            self.rest_constructor_body()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Debe existir un cuerpo del constructor encerrado entre llaves. Se esperaba una {.")

    def rest_constructor_body(self):
        if self.tok(BRACE_CLOSE):
            return
        elif self._current_token.get_type() in FIRST_block_statements:
            self.block_statements()
            #self.update_token()
            if self.tok(BRACE_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe cerrar el cuerpo del constructor. Se esperaba una }.")

        elif self._current_token.get_type() in FIRST_explicit_constructor_invocation:
            self.explicit_constructor_invocation()
            self.update_token()
            self.rest2_constructor_body()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba el cierre del cuerpo del constructor, o una sucesion de sentencias.")

    def rest2_constructor_body(self):
        if self.tok(BRACE_CLOSE):
            return
        else:
            self.block_statements()
            #self.update_token()
            if self.tok(BRACE_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe cerrar del cuerpo del construcor. Se esperaba {")

    def explicit_constructor_invocation(self):
        if self._current_token.get_type() in FIRST_explicit_constructor_invocation:
            self.update_token()
            if self.tok(PAREN_OPEN):
                self.update_token()
                self.rest_explicit_constructor_invocation()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ( que comenzara la definicion de parametros usados para la llamada.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba this o super.")

    def rest_explicit_constructor_invocation(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            if self.tok(SCOLON):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe cerrar la lista de parametros con un ).")
        else:
            self.argument_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                if self.tok(SCOLON):
                    return
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un ;.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe cerrar la lista de parametros con un ).")

    def field_modifiers(self):
        self.field_modifier()
        self.update_token()
        self.rest_field_modifiers()

    def rest_field_modifiers(self):
        if self._current_token.get_type() in FIRST_field_modifiers:
            self.field_modifiers()
        # sino lambda

    def field_modifier(self):
        if self._current_token.get_type() in FIRST_field_modifier:
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Solo los siguientes keywords son validos: public, protected, static.")

    def declarators(self):
        if self.tok(IDENTIFIER):
            self.update_token()
            self.rest_declarators()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un nombre de un identificador, %s no es valido." %
                              self._current_token.get_lexeme())

    def rest_declarators(self):
        if self.tok(COMMA):
            self.update_token()
            self.rest_declarators()
        elif self.tok(ASSIGNMENT):
            self.update_token()
            self.variable_initializer()
            self.update_token()
            if self.tok(SCOLON):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ; al final de la declaracion.")
        elif self.tok(PAREN_OPEN):
            self.update_token()
            self.rest_method_declarator()
            self.update_token()
            self.method_body()
        elif self.tok(SCOLON):
            #self.update_token()
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ; al final de la declaracion.")

    def rest_method_declarator(self):
        if self.tok(PAREN_CLOSE):
            return
        elif self._current_token.get_type() in FIRST_formal_parameter_list:
            self.formal_parameter_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ) que cierre la lista de parametros.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un parametro valido." % self._current_token.get_lexeme())

    def method_body(self):
        self.block()

    def type(self):
        if self.tok(IDENTIFIER) or self.tok(VOID_TYPE):
            return
        else:
            self.primitive_type()

    def primitive_type(self):
        if self._current_token.get_type() in FIRST_numeric_type:
            self.numeric_type()
        elif self._current_token.get_type() in FIRST_boolean_type:
            self.boolean_type()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def type_noident_void(self):
        if self._current_token.get_type() in FIRST_primitive_type:
            self.primitive_type()
        elif self.tok(VOID_TYPE):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def numeric_type(self):
        if self._current_token.get_type() in FIRST_integral_type:
            self.integral_type()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def integral_type(self):
        if self.tok(INT_TYPE) or self.tok(CHAR_TYPE):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def boolean_type(self):
        if self.tok(BOOLEAN_TYPE):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def block(self):
        if self.tok(BRACE_OPEN):
            self.update_token()
            self.rest_block()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un bloque de codigo encerrado entre llaves.")

    def rest_block(self):
        if self.tok(BRACE_CLOSE):
            return
        else:
            self.block_statements()
            #self.update_token()
            if self.tok(BRACE_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba una } para cerrar el bloque de codigo.")

    def block_statements(self):
        self.block_statement()
        self.update_token()
        self.rest_block_statements()

    def rest_block_statements(self):
        if self._current_token.get_type() in FIRST_block_statements:
            self.block_statements()
        # sino lambda

    def block_statement(self):
        if self._current_token.get_type() in FIRST_primitive_type:
            self.update_token()
            self.local_variable_declaration_statement()
        elif self.tok(IDENTIFIER):
            self.update_token()
            self.rest_block_statement()
        elif self.tok(IF):
            self.if_start_statement()
        elif self.tok(WHILE):
            self.while_statement()
        elif self.tok(BRACE_OPEN):
            self.block()
        elif self.tok(SCOLON):
            self.empty_statement()
        elif self.tok(RETURN):
            self.return_statement()
        elif self._current_token.get_type() in FIRST_primary:
            self.primary()
            self.update_token()
            self.rest_method_invocation()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def rest_block_statement(self):
        if self._current_token.get_type() in FIRST_variable_declarator:
            self.variable_declarators()
        elif self.tok(PAREN_OPEN):
            self.update_token()
            self.rest2_method_invocation()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Sentencia no valida.")

    def local_variable_declaration_statement(self):
        self.local_variable_declaration()
        #self.update_token()
        if self.tok(SCOLON):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def local_variable_declaration(self):
        if self.tok(IDENTIFIER):
            self.update_token()
            self.variable_declarators()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un identificador valido." % self._current_token.get_lexeme())

    def variable_declarators(self):
        self.variable_declarator()
        #self.update_token()
        self.rest_variable_declarators()

    def rest_variable_declarators(self):
        if self.tok(COMMA):
            self.update_token()
            self.variable_declarators()
        # sino lambda

    def variable_declarator(self):
        if self._current_token.get_type() in FIRST_rest_variable_declarator:
            self.rest_variable_declarator()

    def rest_variable_declarator(self):
        if self.tok(ASSIGNMENT):
            self.update_token()
            self.expression()
        # sino lambda

    def statement(self):
        if self._current_token.get_type() in FIRST_statement_without_trailing_substatements:
            self.statement_without_trailing_substatement()
        elif self._current_token.get_type() in FIRST_if_start_statement:
            self.if_start_statement()
        elif self._current_token.get_type() in FIRST_while_statement:
            self.while_statement()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def statement_without_trailing_substatement(self):
        if self._current_token.get_type() in FIRST_block:
            self.block()
        elif self._current_token.get_type() in FIRST_empty_statement:
            self.empty_statement()
        elif self._current_token.get_type() in FIRST_expression_statement:
            self.expression_statement()
        elif self._current_token.get_type() in FIRST_return_statement:
            self.return_statement()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def empty_statement(self):
        if self.tok(SCOLON):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def expression_statement(self):
        self.statement_expression()
        self.update_token()
        if self.tok(SCOLON):
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def statement_expression(self):
        self.method_invocation()

    def if_start_statement(self):
        if self.tok(IF):
            self.update_token()
            if self.tok(PAREN_OPEN):
                self.update_token()
                self.expression()
                #self.update_token()
                if self.tok(PAREN_CLOSE):
                    self.update_token()
                    self.statement()
                    self.update_token()
                    self.rest_if_start_statement()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Debe cerrar la expresion con un ).")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe comenzar la expresion luego del if con un (.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba el comienzo de un if.")

    def rest_if_start_statement(self):
        if self.tok(ELSE):
            self.update_token()
            self.statement()
        # sino lambda

    def while_statement(self):
        if self.tok(WHILE):
            self.update_token()
            if self.tok(PAREN_OPEN):
                self.update_token()
                self.expression()
                self.update_token()
                if self.tok(PAREN_CLOSE):
                    self.update_token()
                    self.statement()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Debe cerrar la expresion con un ).")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe comenzar la expresion del while con un (.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un while.")

    def return_statement(self):
        if self.tok(RETURN):
            self.update_token()
            self.rest_return_statement()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un return.")

    def rest_return_statement(self):
        if self.tok(SCOLON):
            return
        elif self._current_token.get_type() in FIRST_expression:
            self.expression()
            self.update_token()
            if self.tok(SCOLON):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ;.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Sentencia de return no valida.")

    def expression(self):
        self.assignment_expression()

    def assignment_expression(self):
        self.conditional_expression()

    def conditional_expression(self):
        self.conditional_or_expression()
        #self.update_token()
        self.rest_conditional_expression()

    def rest_conditional_expression(self):
        if self.tok(ASSIGNMENT):
            self.update_token()
            self.conditional_expression()
        # sino lambda

    def conditional_or_expression(self):
        self.conditional_and_expression()
        #self.update_token()
        self.rest_conditional_or_expression()

    def rest_conditional_or_expression(self):
        if self.tok(CONDITIONAL_OR):
            self.update_token()
            self.conditional_or_expression()
        # sino lambda

    def conditional_and_expression(self):
        self.equality_expression()
        #self.update_token()
        self.rest_conditional_and_expression()

    def rest_conditional_and_expression(self):
        if self.tok(CONDITIONAL_AND):
            self.update_token()
            self.conditional_and_expression()
        # sino lambda

    def equality_expression(self):
        self.relational_expression()
        #self.update_token()
        self.rest_equality_expression()

    def rest_equality_expression(self):
        if self.tok(EQUALS) or self.tok(NOT_EQUALS):
            self.update_token()
            self.equality_expression()
        # sino lambda

    def relational_expression(self):
        self.additive_expression()
        #self.update_token()
        self.rest_relational_expression()

    def rest_relational_expression(self):
        if self._current_token.get_type() in FIRST_rest_relational_expression:
            self.update_token()
            self.relational_expression()
        # sino lambda

    def additive_expression(self):
        self.multiplicative_expression()
        #self.update_token()
        self.rest_additive_expression()

    def rest_additive_expression(self):
        if self._current_token.get_type() in FIRST_rest_additive_expression:
            self.update_token()
            self.additive_expression()
        # sino lambda

    def multiplicative_expression(self):
        self.unary_expression()
        #self.update_token()
        self.rest_multiplicative_expression()

    def rest_multiplicative_expression(self):
        if self._current_token.get_type() in FIRST_rest_multiplicative_expression:
            self.update_token()
            self.multiplicative_expression()
        # sino lambda

    def unary_expression(self):
        if self.tok(ADD) or self.tok(SUB):
            self.update_token()
            self.unary_expression()
        elif self._current_token.get_type() in FIRST_unary_expression_not_plus_minus:
            self.unary_expression_not_plus_minus()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba uno de los siguiente operadores: + o -, o una expresion unaria valida.")

    def unary_expression_not_plus_minus(self):
        if self._current_token.get_type() in FIRST_postfix_expression:
            self.postfix_expression()
        elif self.tok(NOT):
            self.update_token()
            self.unary_expression()

    def postfix_expression(self):
        if self._current_token.get_type() in FIRST_primary:
            self.primary()
        elif self.tok(IDENTIFIER):
            self.update_token()
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un identificador valido." % self._current_token.get_lexeme())

    def primary(self):
        if self._current_token.get_type() in [INT_LITERAL, TRUE, FALSE, CHAR_LITERAL, STRING_LITERAL, NULL, THIS]:
            self.update_token()
            self.rest_primary()
        elif self.tok(PAREN_OPEN):
            self.update_token()
            self.expression()
            #self.update_token()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                self.rest_primary()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        elif self.tok(NEW):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                if self.tok(PAREN_OPEN):
                    self.update_token()
                    self.rest2_primary()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un (.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        elif self.tok(SUPER):
            self.update_token()
            if self.tok(ACCESSOR):
                self.update_token()
                if self.tok(IDENTIFIER):
                    return
                else:
                    raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un identificador valido." % self._current_token.get_lexeme())
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un . .")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un primary valido." % self._current_token.get_lexeme())

    def rest_primary(self):
        if self.tok(ACCESSOR):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                self.rest_primary()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        # sino lambda

    def rest2_primary(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            self.rest_primary()
        elif self._current_token.get_type() in FIRST_argument_list:
            self.argument_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                self.rest_primary()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ( o un tipo valido.")

    def class_instance_creation_expression(self):
        if self.tok(NEW):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                if self.tok(PAREN_OPEN):
                    self.update_token()
                    self.rest_class_instance_creation_expression()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un ).")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba el operador new.")

    def rest_class_instance_creation_expression(self):
        if self.tok(PAREN_CLOSE):
            return
        elif self._current_token.get_type() in FIRST_argument_list:
            self.argument_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ) o un argumento valido.")

    def argument_list(self):
        self.expression()
        self.update_token()
        self.rest_argument_list()

    def rest_argument_list(self):
        if self.tok(COMMA):
            self.update_token()
            self.rest_argument_list()
        # sino lambda

    def field_access(self):
        if self._current_token in [INT_LITERAL, TRUE, FALSE, CHAR_LITERAL, STRING_LITERAL, NULL, THIS]:
            self.update_token()
            self.rest_field_access()
        elif self.tok(PAREN_OPEN):
            self.update_token()
            self.expression()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                self.rest_field_access()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        elif self.tok(NEW):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                if self.tok(PAREN_OPEN):
                    self.update_token()
                    self.rest2_field_access()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un (.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        elif self.tok(SUPER):
            self.update_token()
            if self.tok(ACCESSOR):
                self.update_token()
                if self.tok(IDENTIFIER):
                    return
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "%s no es un identificador valido." % self._current_token.get_lexeme())
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un . .")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un primary valido." % self._current_token.get_lexeme())

    def rest_field_access(self):
        if self.tok(ACCESSOR):
            self.update_token()
            if self.tok(IDENTIFIER):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un . .")

    def rest2_field_access(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            self.rest_field_access()
        elif self._current_token.get_type() in FIRST_argument_list:
            self.argument_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                self.rest_field_access()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ) o un argumento valido.")

    def method_invocation(self):
        if self.tok(IDENTIFIER):
            self.update_token()
            self.rest_method_invocation()
        elif self._current_token.get_type() in FIRST_primary:
            self.primary()
            self.update_token()
            self.rest_method_invocation()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un primary ni un identificador valido." % self._current_token.get_lexeme())

    def rest_method_invocation(self):
        if self.tok(ACCESSOR):
            self.update_token()
            if self.tok(IDENTIFIER):
                self.update_token()
                if self.tok(PAREN_OPEN):
                    self.update_token()
                    self.rest2_method_invocation()
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un (.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        elif self.tok(ASSIGNMENT):
            self.update_token()
            self.expression()
        # sino lambda

    def rest2_method_invocation(self):
        if self.tok(PAREN_CLOSE):
            return
        elif self._current_token.get_type() in FIRST_argument_list:
            self.argument_list()
            self.update_token()
            if self.tok(PAREN_CLOSE):
                return
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ) o un argumento valido.")

    def literal(self):
        if self._current_token in [INT_LITERAL, TRUE, FALSE, CHAR_LITERAL, STRING_LITERAL, NULL]:
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un literal valido.")
