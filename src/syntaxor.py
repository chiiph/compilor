from lexor import Lexor
from constants import *
from firsts import *
from errors import SyntaxError

from mj.mjprimary import *
from mj.mjclass import *

class Syntaxor(object):
    def __init__(self, path):
        self._lexor = Lexor(path)
        self._current_token = None

    def check_syntax(self, ts):
        self.update_token()
        return self.compilation_unit(ts)

    def update_token(self):
        self._current_token = self._lexor.get_token()
        #print self._current_token

    def tok(self, tokentype):
        return self._current_token.get_type() == tokentype

    def compilation_unit(self, ts):
        return self.type_declarations(ts)

    def type_declarations(self, ts):
        if self.tok(PUBLIC):
            class_decl = self.class_declaration(ts)
            rest = self.type_declarations(ts)
            return [class_decl] + rest
        elif self.tok(EOF):
            return [] # LAMBDA
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Las declaraciones de clases deben comenzar con el keyword public.")

    def class_declaration(self, ts):
        # si entre aca es porque el current es PUBLIC
        # asi que busco CLASS ahora
        self.update_token()
        if self.tok(CLASS):
            # y despues IDENTIFIER
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                clts = mjTS(ts)
                (ext_id, decls) = self.rest_class_declaration(clts)
                return mjClass(t, ext_id, decls, ts, clts)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe especificar un nombre para la clase, %s no es valido." %
                                  self._current_token.get_lexeme())
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "La palabra clave class debe ser especificada luego de public.")

    def rest_class_declaration(self, ts):
        if self.tok(BRACE_OPEN):
            return (None, self.class_body(ts))
        elif self.tok(EXTENDS):
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                return (t, self.class_body(ts))
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe especificar un identificador de la clase de la cual se hereda.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba una { o la palabra clave extends.")

    def class_body(self, ts):
        if self.tok(BRACE_OPEN):
            self.update_token()
            return self.rest_class_body(ts)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba una {.")

    def rest_class_body(self, ts):
        if self.tok(BRACE_CLOSE):
            self.update_token()
            return []
        else:
            decls = self.class_body_declarations(ts)
            if self.tok(BRACE_CLOSE):
                self.update_token()
                return decls
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba una } como cierre de la clase.")

    def class_body_declarations(self, ts):
        decl = self.class_body_declaration(ts)
        rest = self.rest_class_body_declarations(ts)
        return [decl] + rest

    def rest_class_body_declarations(self, ts):
        # si hay mas class body declaration
        if self._current_token.get_type() in FIRST_class_body_declaration:
            return self.class_body_declarations(ts)
        # sino, vamos por lambda
        return []

    def class_body_declaration(self, ts):
        modifs = self.field_modifiers()
        (method_decl, name, init, list_ids, method_body) = self.rest_class_body_declaration()
        if method_decl:
            if init == None: # constructor
                return mjMethod(modifs = modifs, ret_type = None, name = name, params = list_ids, body = method_body, ts=ts)
            else:
                return mjMethod(modifs = modifs, ret_type = name, name = init, params = list_ids, body = method_body, ts=ts)
        else:
            return mjClassVariableDecl(modifs, name, list_ids, ts)

    def rest_class_body_declaration(self):
        if self._current_token.get_type() in FIRST_primitive_type:
            _type = self.primitive_type()
            (method_decl, init, list_ids, method_body) = self.declarators()
            return (method_decl, _type, init, list_ids, method_body)
        elif self.tok(VOID_TYPE):
            _type = self._current_token
            self.update_token()
            (method_decl, init, list_ids, method_body) = self.declarators()
            return (method_decl, _type, init, list_ids, method_body)
        elif self.tok(IDENTIFIER):
            t = self._current_token
            self.update_token()
            (method_decl, init, list_ids, method_body) = self.rest2_class_body_declaration()
            if method_decl:
                return (method_decl, t, init, list_ids, method_body)
            else:
                return (method_decl, t, None, list_ids, None)

    def rest2_class_body_declaration(self):
        if self._current_token.get_type() in FIRST_constructor_declarator:
            params = self.constructor_declarator()
            body = self.constructor_body()
            return (True, None, params, body)
        elif self.tok(IDENTIFIER):
            (method_decl, init, list_ids, method_body) = self.declarators()
            return (method_decl, init, list_ids, method_body)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un identificador o un (.")

    def constructor_declarator(self):
        if self.tok(PAREN_OPEN):
            self.update_token()
            return self.rest_constructor_declarator()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Luego del nombre del constructor se deben especificar los parametros. Se esperaba leer un (.")

    def rest_constructor_declarator(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            return []
        else:
            params = self.formal_parameter_list()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                return params
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ) como cierre de los parametros del constructor.")

    def formal_parameter_list(self):
        param = self.formal_parameter()
        rest = self.rest_formal_parameter_list()
        return [param] + rest

    def rest_formal_parameter_list(self):
        if self.tok(COMMA):
            self.update_token()
            return self.formal_parameter_list()
        # sino vamos por lambda
        return []

    def formal_parameter(self):
        _type = self.type()
        if self.tok(IDENTIFIER):
            t = self._current_token
            self.update_token()
            return (_type, t)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba encontrar un nombre para el parametro, %s no es valido." %
                              self._current_token.get_lexeme())

    def constructor_body(self):
        if self.tok(BRACE_OPEN):
            self.update_token()
            return self.rest_constructor_body()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Debe existir un cuerpo del constructor encerrado entre llaves. Se esperaba una {.")

    def rest_constructor_body(self):
        if self.tok(BRACE_CLOSE):
            self.update_token()
            return mjBlock()
        elif self._current_token.get_type() in FIRST_block_statements:
            bstats = self.block_statements()
            if self.tok(BRACE_CLOSE):
                self.update_token()
                return mjBlock(bstats)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Debe cerrar el cuerpo del constructor. Se esperaba una }.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba el cierre del cuerpo del constructor, o una sucesion de sentencias.")

    def field_modifiers(self):
        modif = self.field_modifier()
        rest = self.rest_field_modifiers()
        return [modif] + rest

    def rest_field_modifiers(self):
        if self._current_token.get_type() in FIRST_field_modifiers:
            return self.field_modifiers()
        # sino lambda
        return []

    def field_modifier(self):
        if self._current_token.get_type() in FIRST_field_modifier:
            t = self._current_token
            self.update_token()
            return t
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Solo los siguientes keywords son validos: public, protected, static.")

    def declarators(self):
        if self.tok(IDENTIFIER):
            t = self._current_token
            self.update_token()
            (method_decl, init, list_ids, method_body) = self.rest_declarators()
            if method_decl:
                return (method_decl, t, list_ids, method_body)
            else:
                print type(list_ids)
                return (method_decl, None, [(t, init)] + list_ids, method_body)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un nombre de un identificador, %s no es valido." %
                              self._current_token.get_lexeme())

    def rest_declarators(self):
        if self.tok(COMMA):
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                (method_decl, initializer, list_ids, method_body) = self.rest2_declarators()
                return (False, None, [(t, initializer)] + list_ids, None)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." %
                                  self._current_token)
        elif self.tok(ASSIGNMENT):
            self.update_token()
            expr = self.expression()
            (method_decl, init, list_ids, method_body) = self.rest2_declarators()
            return (False, expr, list_ids, None)
        elif self.tok(PAREN_OPEN):
            self.update_token()
            params = self.rest_method_declarator()
            bl = self.method_body()
            return (True, None, params, bl)
        elif self.tok(SCOLON):
            self.update_token()
            return (False, None, [], None)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ; al final de la declaracion.")

    def rest2_declarators(self):
        if self.tok(COMMA):
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                (method_decl, init, list_ids, method_body) = self.rest2_declarators()
                return (False, None, [(t, init)] + list_ids, None)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." %
                                  self._current_token)
        elif self.tok(ASSIGNMENT):
            self.update_token()
            expr = self.expression()
            (method_decl, init, list_ids, method_body) = self.rest2_declarators()
            return (False, expr, list_ids, method_body)
        elif self.tok(SCOLON):
            self.update_token()
            return (False, None, [], None)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ; al final de la declaracion.")

    def rest_method_declarator(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            return []
        elif self._current_token.get_type() in FIRST_formal_parameter_list:
            params = self.formal_parameter_list()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                return params
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ) que cierre la lista de parametros.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un parametro valido." % self._current_token.get_lexeme())

    def method_body(self):
        return self.block()

    def type(self):
        if self.tok(IDENTIFIER) or self.tok(VOID_TYPE):
            t = self._current_token
            self.update_token()
            return t
        else:
            return self.primitive_type()

    def primitive_type(self):
        if self._current_token.get_type() in FIRST_numeric_type:
            return self.numeric_type()
        elif self._current_token.get_type() in FIRST_boolean_type:
            return self.boolean_type()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def numeric_type(self):
        if self._current_token.get_type() in FIRST_integral_type:
            return self.integral_type()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def integral_type(self):
        if self.tok(INT_TYPE) or self.tok(CHAR_TYPE):
            t = self._current_token
            self.update_token()
            return t
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def boolean_type(self):
        if self.tok(BOOLEAN_TYPE):
            t = self._current_token
            self.update_token()
            return t
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un tipo valido." % self._current_token.get_lexeme())

    def block(self):
        if self.tok(BRACE_OPEN):
            self.update_token()
            blstats = self.rest_block()
            return mjBlock(blstats)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un bloque de codigo encerrado entre llaves.")

    def rest_block(self):
        if self.tok(BRACE_CLOSE):
            self.update_token()
            return []
        else:
            blstats = self.block_statements()
            if self.tok(BRACE_CLOSE):
                self.update_token()
                return blstats
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba una } para cerrar el bloque de codigo.")

    def block_statements(self):
        blstat = self.block_statement()
        rest = self.rest_block_statements()
        return [blstat] + rest

    def rest_block_statements(self):
        if self._current_token.get_type() in FIRST_block_statements:
            return self.block_statements()
        # sino lambda
        return []

    def block_statement(self):
        if self._current_token.get_type() in FIRST_primitive_type:
            prim_type = self.primitive_type()
            vardecl = self.local_variable_declaration_statement()
            return mjVariableDecl(prim_type, vardecl)
        elif self.tok(IF):
            return self.if_start_statement()
        elif self.tok(WHILE):
            return self.while_statement()
        elif self.tok(BRACE_OPEN):
            return self.block()
        elif self.tok(SCOLON):
            return self.empty_statement()
        elif self.tok(RETURN):
            return self.return_statement()
        elif self._current_token.get_type() in FIRST_primary:
            (prim_first, prim_last) = self.primary()
            # aca siempre se devuelve where == 4, o sea lambda, ver de sacar
            (where, _type, expr, first, last) = self.rest_method_invocation()
            return prim_last
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def local_variable_declaration_statement(self):
        localdecl = self.local_variable_declaration()
        if self.tok(SCOLON):
            self.update_token()
            return localdecl
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def local_variable_declaration(self):
        if self.tok(IDENTIFIER):
            t = self._current_token
            self.update_token()
            (vardecls, rest) = self.variable_declarators()
            return [(t, vardecls)] + rest
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un identificador valido." % self._current_token.get_lexeme())

    def variable_declarators(self):
        vardecl = self.variable_declarator()
        rest = self.rest_variable_declarators()
        return (vardecl, rest)

    def rest_variable_declarators(self):
        if self.tok(COMMA):
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                (vardecls, rest) = self.variable_declarators()
                return [(t, vardecls)] + rest
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un identificador valido.")
        # sino lambda
        return []

    def variable_declarator(self):
        # VER
        #if self._current_token.get_type() in FIRST_rest_variable_declarator:
        return self.rest_variable_declarator()

    def rest_variable_declarator(self):
        if self.tok(ASSIGNMENT):
            self.update_token()
            return self.expression()
        # sino lambda
        return None

    def statement(self):
        if self._current_token.get_type() in FIRST_statement_without_trailing_substatements:
            return self.statement_without_trailing_substatement()
        elif self._current_token.get_type() in FIRST_if_start_statement:
            return self.if_start_statement()
        elif self._current_token.get_type() in FIRST_while_statement:
            return self.while_statement()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def statement_without_trailing_substatement(self):
        if self._current_token.get_type() in FIRST_block:
            return self.block()
        elif self._current_token.get_type() in FIRST_empty_statement:
            return self.empty_statement()
        elif self._current_token.get_type() in FIRST_expression_statement:
            return self.expression_statement()
        elif self._current_token.get_type() in FIRST_return_statement:
            return self.return_statement()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Comienzo de sentencia no valido.")

    def empty_statement(self):
        if self.tok(SCOLON):
            self.update_token()
            return None
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def expression_statement(self):
        expr = self.statement_expression()
        if self.tok(SCOLON):
            self.update_token()
            return expr
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ;.")

    def statement_expression(self):
        return self.method_invocation()

    def if_start_statement(self):
        if self.tok(IF):
            self.update_token()
            if self.tok(PAREN_OPEN):
                self.update_token()
                expr = self.expression()
                if self.tok(PAREN_CLOSE):
                    self.update_token()
                    stat = self.statement()
                    elsestat = self.rest_if_start_statement()
                    return mjIf(expr, stat, elsestat)
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
            return self.statement()
        # sino lambda
        return None

    def while_statement(self):
        if self.tok(WHILE):
            self.update_token()
            if self.tok(PAREN_OPEN):
                self.update_token()
                expr = self.expression()
                if self.tok(PAREN_CLOSE):
                    self.update_token()
                    stat = self.statement()
                    return mjWhile(expr, stat)
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
            expr = self.rest_return_statement()
            return mjReturn(expr)
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un return.")

    def rest_return_statement(self):
        if self.tok(SCOLON):
            self.update_token()
            return None
        elif self._current_token.get_type() in FIRST_expression:
            expr = self.expression()
            if self.tok(SCOLON):
                self.update_token()
                return expr
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ;.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Sentencia de return no valida.")

    def expression(self):
        return self.assignment_expression()

    def assignment_expression(self):
        return self.conditional_expression()

    def conditional_expression(self):
        coe = self.conditional_or_expression()
        (op, rce) = self.rest_conditional_expression()
        if op is None:
            return coe
        return op([coe, rce])

    def rest_conditional_expression(self):
        if self.tok(ASSIGNMENT):
            op = ops[self._current_token.get_type()]
            self.update_token()
            ce = self.conditional_expression()
            return (op, ce)
        # sino lambda
        return (None, None)

    def conditional_or_expression(self):
        cae = self.conditional_and_expression()
        (op, rcoe) = self.rest_conditional_or_expression()
        if op is None:
            return cae
        return op([cae, rcoe])

    def rest_conditional_or_expression(self):
        if self.tok(CONDITIONAL_OR):
            op = ops[self._current_token.get_type()]
            self.update_token()
            coe = self.conditional_or_expression()
            return (op, coe)
        # sino lambda
        return (None, None)

    def conditional_and_expression(self):
        ee = self.equality_expression()
        (op, rcae) = self.rest_conditional_and_expression()
        if op is None:
            return ee
        return op([ee, rcae])

    def rest_conditional_and_expression(self):
        if self.tok(CONDITIONAL_AND):
            op = ops[self._current_token.get_type()]
            self.update_token()
            cae = self.conditional_and_expression()
            return (op, cae)
        # sino lambda
        return (None, None)

    def equality_expression(self):
        re = self.relational_expression()
        (op, ree) = self.rest_equality_expression()
        if op is None:
            return re
        return op([re, ree])

    def rest_equality_expression(self):
        if self.tok(EQUALS) or self.tok(NOT_EQUALS):
            op = ops[self._current_token.get_type()]
            self.update_token()
            ee = self.equality_expression()
            return (op, ee)
        # sino lambda
        return (None, None)

    def relational_expression(self):
        ae = self.additive_expression()
        (op, re) = self.rest_relational_expression()
        if op is None:
            return ae
        return op([ae, re])

    def rest_relational_expression(self):
        if self._current_token.get_type() in FIRST_rest_relational_expression:
            op = ops[self._current_token.get_type()]
            self.update_token()
            re = self.relational_expression()
            return (op, re)
        # sino lambda
        return (None, None)

    def additive_expression(self):
        me = self.multiplicative_expression()
        (op, ae) = self.rest_additive_expression()
        if op is None:
            return me
        return op([me, ae])

    def rest_additive_expression(self):
        if self._current_token.get_type() in FIRST_rest_additive_expression:
            op = ops[self._current_token.get_type()]
            self.update_token()
            ae = self.additive_expression()
            return (op, ae)
        # sino lambda
        return (None, None)

    def multiplicative_expression(self):
        u = self.unary_expression()
        (op, me) = self.rest_multiplicative_expression()
        if op is None:
            return u
        return op([u, me])

    def rest_multiplicative_expression(self):
        if self._current_token.get_type() in FIRST_rest_multiplicative_expression:
            op = ops[self._current_token.get_type()]
            self.update_token()
            me = self.multiplicative_expression()
            return (op, me)
        # sino lambda
        return (None, None)

    def unary_expression(self):
        if self.tok(ADD) or self.tok(SUB):
            op = ops[self._current_token.get_type()]
            self.update_token()
            ex = self.unary_expression()
            return op([ex])
        elif self._current_token.get_type() in FIRST_unary_expression_not_plus_minus:
            ex = self.unary_expression_not_plus_minus()
            return ex
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba uno de los siguiente operadores: + o -, o una expresion unaria valida.")

    def unary_expression_not_plus_minus(self):
        if self._current_token.get_type() in FIRST_postfix_expression:
            ex = self.postfix_expression()
            return ex
        elif self.tok(NOT):
            self.update_token()
            ex = self.unary_expression()
            return mjNot([ex])

    def postfix_expression(self):
        if self._current_token.get_type() in FIRST_primary:
            (prim_first, prim_last) = self.primary()
            return prim_last
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un identificador valido." % self._current_token.get_lexeme())

    def primary(self):
        prim = None
        first = None
        last = None
        # aca va a haber que diferenciar entre todos y NULL y THIS
        if self._current_token.get_type() in [INT_LITERAL, TRUE, FALSE, CHAR_LITERAL, STRING_LITERAL, NULL, THIS]:
            prim = mjPrimary(ref=self._current_token, type=self._current_token.get_type()._id)
            self.update_token()
            (first, last) = self.rest_primary()
        elif self.tok(PAREN_OPEN):
            self.update_token()
            prim = self.expression()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                (first, last) = self.rest_primary()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        elif self.tok(NEW):
            prim = self.class_instance_creation_expression()
            (first, last) = self.rest_primary()
        elif self.tok(SUPER):
            prim = mjPrimary(self._current_token, self._current_token.get_type()._id)
            self.update_token()
            (first, last) = self.rest_primary()
        elif self.tok(IDENTIFIER):
            print "UUUUUOOOOOOOOOOO", self._current_token
            prim = self.method_invocation()
            (first, last) = self.rest_primary()
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "%s no es un primary valido." % self._current_token.get_lexeme())
        if first is None:
            return (prim, prim)
        first.goesto = prim
        return (prim, last)

    def rest_primary(self):
        if self.tok(ACCESSOR):
            self.update_token()
            if self.tok(IDENTIFIER):
                prim = mjPrimary(ref=self._current_token, type=self._current_token.get_type()._id)
                self.update_token()
                (where, argList, first, last) = self.rest2_primary()
                if where == 1:
                    method = mjMethodInvocation(prim, argList)
                    if not first is None:
                        first.goesto = method
                        return (method, last)
                    return (method, method)
                elif where == 2:
                    if not first is None:
                        first.goesto = prim
                        return (prim, last)
                    return (prim, prim)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "%s no es un identificador valido." % self._current_token.get_lexeme())
        # sino lambda
        return (None, None)

    def rest2_primary(self):
        argList = []
        first = None
        last = None
        where = 2
        if self.tok(PAREN_OPEN):
            self.update_token()
            argList = self.rest2_method_invocation()
            where = 1
        (first, last) = self.rest_primary()
        return (where, argList, first, last)

    def class_instance_creation_expression(self):
        if self.tok(NEW):
            self.update_token()
            if self.tok(IDENTIFIER):
                t = self._current_token
                self.update_token()
                if self.tok(PAREN_OPEN):
                    self.update_token()
                    argList = self.rest_class_instance_creation_expression()
                    prim_id = mjPrimary(ref=t, type=IDENTIFIER)
                    return mjClassInstanceCreation(prim_id, argList)
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un (.")
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
            self.update_token()
            return []
        elif self._current_token.get_type() in FIRST_argument_list:
            argList = self.argument_list()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                return argList
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un ) o un argumento valido.")

    def argument_list(self):
        expr = self.expression()
        rest = self.rest_argument_list()
        return [expr] + rest

    def rest_argument_list(self):
        if self.tok(COMMA):
            self.update_token()
            rest = self.argument_list()
            return rest
        # sino lambda
        return []

    def method_invocation(self):
        prim_ref = None
        prim_first = None
        prim_last = None
        argList = []
        where = 0
        _type = 0
        expr = None
        first = None
        last = None
        prim_id = None

        if self.tok(IDENTIFIER):
            print "POR ACA", self._current_token
            prim_ref = mjPrimary(ref=self._current_token, type=IDENTIFIER)
            self.update_token()
            (prim_first, prim_last) = self.rest_primary()
            # if self.tok(PAREN_OPEN):
            #     self.update_token()
            #     argList = self.rest2_method_invocation()
            (where, _type, expr, first, last) = self.rest_method_invocation()
        elif (self._current_token.type() in FIRST_literal) or self.tok(THIS):
            prim_ref = mjPrimary(ref=self._current_token, type=self._current_token.get_type()._id)
            self.update_token()
            (prim_first, prim_last) = self.rest_primary()
            if self.tok(ACCESSOR):
                self.update_token()
                if self.tok(IDENTIFIER):
                    prim_id = mjPrimary(ref=self._current_token, type=IDENTIFIER)
                    self.update_token()
                    if self.tok(PAREN_OPEN):
                        argList = self.rest2_method_invocation()
                        (where, _type, expr, first, last) = self.rest_method_invocation()
                        prim_id = mjMethodInvocation(prim_id, argList)
                    else:
                        raise SyntaxError(self._current_token.get_line(),
                                          self._current_token.get_col(),
                                          "Se esperaba un (.")
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un identificador valido.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un . .")
        elif self.tok(PAREN_OPEN):
            self.update_token()
            prim_ref = self.expression()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                (prim_first, prim_last) = self.rest_primary()
                if self.tok(ACCESSOR):
                    self.update_token()
                    if self.tok(IDENTIFIER):
                        prim_id = mjPrimary(ref=self._current_token, type=IDENTIFIER)
                        self.update_token()
                        if self.tok(PAREN_OPEN):
                            argList = self.rest2_method_invocation()
                            (where, _type, expr, first, last) = self.rest_method_invocation()
                            prim_id = mjMethodInvocation(prim_id, argList)
                        else:
                            raise SyntaxError(self._current_token.get_line(),
                                              self._current_token.get_col(),
                                              "Se esperaba un (.")
                    else:
                        raise SyntaxError(self._current_token.get_line(),
                                          self._current_token.get_col(),
                                          "Se esperaba un identificador valido.")
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un . .")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ).")
        elif self.tok(NEW):
            prim_ref = self.class_instance_creation_expression()
            (prim_first, prim_last) = self.rest_primary()
            if self.tok(ACCESSOR):
                self.update_token()
                if self.tok(IDENTIFIER):
                    prim_id = mjPrimary(ref=self._current_token, type=IDENTIFIER)
                    self.update_token()
                    if self.tok(PAREN_OPEN):
                        argList = self.rest2_method_invocation()
                        (where, _type, expr, first, last) = self.rest_method_invocation()
                        prim_id = mjMethodInvocation(prim_id, argList)
                    else:
                        raise SyntaxError(self._current_token.get_line(),
                                          self._current_token.get_col(),
                                          "Se esperaba un (.")
                else:
                    raise SyntaxError(self._current_token.get_line(),
                                      self._current_token.get_col(),
                                      "Se esperaba un identificador valido.")
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un . .")
        elif self.tok(SUPER):
            sup = mjPrimary(ref=self._current_token, type=SUPER)
            self.update_token()
            (prim_first, prim_last) = self.rest_primary()
            (where, _type, expr, first, last) = self.rest_super()
            if where == 1:
                method = mjMethodInvocation(sup, expr)
                first.goesto = method
            elif where == 2:
                first.goesto = sup
            return last

        if not prim_first is None:
            prim_first.goesto = prim_ref

        if not first is None:
            if not prim_id is None:
                first.goesto = prim_id
                prim_id.goesto = prim_last
            else:
                if not prim_first is None:
                    first.goesto = prim_last
                else:
                    first.goesto = prim_ref

        the_last = None
        if not last is None:
            the_last = last
        elif not prim_id is None:
            the_last = prim_id
        elif not prim_last is None:
            the_last = prim_last
        else:
            the_last = prim_ref

        if where == 4:
            return the_last

        if _type == 1:
            if where == 3:
                method = None
                if not prim_last is None:
                    method = mjMethodInvocation(prim_last, expr)
                    method.goesto = prim_last.goesto
                else:
                    method = mjMethodInvocation(prim_ref, expr)

                if not first is None:
                    first.goesto = method
                else:
                    if the_last == prim_ref or the_last == prim_last:
                        the_last = method

            print "YYYYYYYYYYYY", expr
            return mjAssignment(the_last, expr)
        elif _type == 2:
            if where == 1:
                return the_last
            elif where == 3:
                method = None
                if not prim_last is None:
                    method = mjMethodInvocation(prim_last, expr)
                    method.goesto = prim_last.goesto
                else:
                    method = mjMethodInvocation(prim_ref, expr)

                if not first is None:
                    first.goesto = method
                else:
                    if the_last == prim_ref or the_last == prim_last:
                        the_last = method

                return the_last
        elif _type == 3:
            return the_last
        elif _type == 4:
            prim_ref.pprint()
            if not isId(prim_ref):
                raise Exception("AA")
            print "TYPE ES 4444444444444444", expr
            return mjVariableDecl(prim_ref.ref, expr)

    def rest_method_invocation(self):
        if self.tok(ACCESSOR):
            self.update_token()
            if self.tok(IDENTIFIER):
                prim_id = mjPrimary(ref=self._current_token, type=self._current_token.get_type()._id)

                self.update_token()
                (prim_first, prim_last) = self.rest_primary()
                (where, _type, expr, first, last) = self.rest_method_invocation()

                if where == 4:
                    if not prim_first is None:
                        prim_first.goesto = prim_id
                        return (1, _type, expr, prim_id, prim_last)
                    else:
                        return (1, _type, expr, prim_id, prim_id)
                elif where == 1:
                    if not prim_first is None:
                        first.goesto = prim_last
                        prim_first.goesto = prim_id
                    else:
                        first.goesto = prim_id
                    return (1, _type, expr, prim_id, last)
                elif where == 2:
                    prim_first.goesto = prim_id
                    return (1, _type, expr, prim_id, prim_last)
                elif where == 3:
                    prim_ref = prim_id
                    if not prim_first is None:
                        prim_ref = prim_last

                    method = mjMethodInvocation(prim_ref.ref, expr)
                    method.goesto = prim_ref.goesto
                    if not prim_first is None: # caso "especial"
                        prim_first.goesto = prim_id
                    if not first is None:
                        first.goesto = method
                        return (1, _type, expr, prim_id, last)
                    else:
                        return (1, _type, expr, prim_id, prim_ref)
                elif where == 5:
                    raise Exception()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un identificador valido.")
        elif self.tok(ASSIGNMENT):
            self.update_token()
            expr = self.expression()
            if self.tok(SCOLON):
                return (2, 1, expr, None, None)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ;.")
        elif self.tok(IDENTIFIER):
            print "AAAAAAAAAAA"
            expr = self.local_variable_declaration()
            if self.tok(SCOLON):
                return (5, 4, expr, None, None)
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un ;.")
        elif self.tok(PAREN_OPEN):
            self.update_token()
            argList = self.rest2_method_invocation()
            (where, _type, expr, first, last) = self.rest_method_invocation()
            if where == 4:
                return (3, 2, argList, first, last)
            elif where == 2:
                raise Exception()
            elif where == 1:
                return (3, _type, argList, first, last)
            elif where == 3:
                raise Exception()

        return (4, None, None, None, None)

    def rest_super(self):
        if self.tok(PAREN_OPEN):
            argList = self.rest2_method_invocation()
            (where, _type, expr, first, last) = self.rest_method_invocation()
            if where == 4:
                return (1, 2, argList, first, last)
            elif where == 2:
                raise Exception()
            elif where == 1:
                return (1, _type, argList, first, last)
            elif where == 3:
                raise Exception()
        elif self.tok(IDENTIFIER):
            prim_id = mjPrimary(ref=self._current_token, type=self._current_token.get_type()._id)
            self.update_token()
            if self.tok(PAREN_OPEN):
                argList = self.rest2_method_invocation()
                (where, _type, expr, first, last) = self.rest_method_invocation()
                method = mjMethodInvocation(prim_id, expr)
                if not first is None:
                    first.goesto = method
                if where == 4:
                    return (2, 2, argList, method, last)
                elif where == 2:
                    raise Exception()
                elif where == 1:
                    return (2, _type, argList, method, last)
                elif where == 3:
                    raise Exception()
            else:
                raise SyntaxError(self._current_token.get_line(),
                                  self._current_token.get_col(),
                                  "Se esperaba un (.")
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un identificador valido o un (.")

    def rest2_method_invocation(self):
        if self.tok(PAREN_CLOSE):
            self.update_token()
            return []
        elif self._current_token.get_type() in FIRST_argument_list:
            argList = self.argument_list()
            if self.tok(PAREN_CLOSE):
                self.update_token()
                return argList
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
            self.update_token()
            return
        else:
            raise SyntaxError(self._current_token.get_line(),
                              self._current_token.get_col(),
                              "Se esperaba un literal valido.")
