from mjcheckers import mjCheckable
from constants import *
from errors import SemanticError
from mjclass import isClass, mjVariable, isVariable, isMethod
from firsts import FIRST_literal, FIRST_primitive_type
from lexor import Token, isToken

import random
import string

def typeToStr(t):
  if t == INT_TYPE:
    return "int"
  elif t == CHAR_TYPE:
    return "char"
  elif t == BOOLEAN_TYPE:
    return "boolean"
  else:
    return "<unresolved>"

def literalToType(lit):
  if lit == INT_LITERAL:
    return INT_TYPE
  elif lit == CHAR_LITERAL:
    return CHAR_TYPE
  elif lit == TRUE or lit == FALSE:
    return BOOLEAN_TYPE
  else:
    return REF_TYPE

def isMethodInv(obj):
  return isinstance(obj, mjMethodInvocation)

def isClassInstanceCreation(obj):
  return isinstance(obj, mjClassInstanceCreation)

# las constantes deben ser negativas, asi se puede usar el id de los tokens transparentemente
class mjPrimary(mjCheckable):
  # Constantes de tipo de primary
  # a estas hay que "sumarle" las de token que estan implicitas
  Expr           = -1
  ClassInstCreat = -2
  MethodInv      = -3
  Assignment     = -4

  def __init__(self, ref, type=0):
    self.ref = ref
    self.type = type
    self.ts = None
    self.goesto = None

  def set_ts(self,ts):
    self.ts = ts
    if not self.goesto is None:
      self.goesto.set_ts(ts)

  def type_to_str(self):
    t = self.type
    if t < 0:
      if t == -1:
        return "Expr"
      elif t == -2:
        return "ClassInstCreat"
      elif t == -3:
        return "MethodInv"
      elif t == -4:
        return "Assignment"
      else:
        return "Unknown"
    else:
      return self.ref.get_type()._name

  def to_string(self):
    return "[" + self.type_to_str() + "::" + self.ref.get_lexeme() + "]"

  def pprint(self, tabs=0):
    print "  "*tabs + self.to_string()
    if not self.goesto is None:
      self.goesto.pprint(tabs+1)

  def get_type(self):
    return self.type # las expressions reimplementan esto para resolverse y devolver un INT_TYPE o STRING_TYPE

  def resolve(self):
    if self.ref.get_type() in FIRST_literal:
      return self.lit_or_string_resolve()

    if self.goesto is None:
      return self.inmediate_resolve()
    else:
      val = self.goesto.resolve()
      # Si no es inmediato, tenemos varias posibilidades
      # En esta implementacion de resolve, sabemos que el actual es un identificador
      if isClass(val): # es un mjClass, por ende este es un acceso a una variable estatica, si es que existe
        print "Accessing a static var..."
        # tenemos qeu buscar en el ts de la clase, si hay una variable con el nombre este
        # y ver si es estatica y publica
        return self._resolve_class(val)
      elif isMethod(val):
        # o es el caso de algo.unmetodo().attr
        print "Member of an object returned in a method invocation..."
        return self._resolve_method(val)
      elif isVariable(val):
        # o es el caso de que es una variable, no importa de que (ya se resolvio antes)
        # ....atributo.attr
        print "Member of an object..."
        return self._resolve_var(val)
      elif isToken(val):
        # o es un token, en cuyo caso algo anduvo mal, o es un literal
        # el unico tipo de literal qeu tiene metodos es String, y eso se devuelve como var
        # asi que esto es un error no mas
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Los tipos primitivos no puede ser dereferenciados")
      else:
        print val
        raise Exception()

  def _resolve_class(self, val):
    if val.ts.varExists(self.ref.get_lexeme()):
      var = val.ts.getVar(self.ref.get_lexeme())
      if var.isPublic() and var.isStatic():
        return var
      else:
        if var.isProtected():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Se esta tratando de acceder a un miembro protegido de %s"
                              % val.name.get_lexeme())
        else:
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Para acceder a %s debe crear una instancia de %s primero."
                              % (self.ref.get_lexeme(), val.name.get_lexeme()))
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "%s no pertenece a la clase %s"
                          % (self.ref.get_lexeme(), val.name.get_lexeme()))

  def _resolve_method(self, val):
    # Hay que ver que tipo devuelve el metodo para ver si un objeto de ese tipo
    # tiene un miembro publico no estatico llamado como self.ref.get_lexeme()

    # si es un tipo primitivo, es un error
    if val.ret_type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "%s no puede ser dereferenciado."
                          % val.ret_type.get_lexeme())

    # sino
    t = self.ts.recFindType(val.ret_type.get_lexeme())
    (hasvar, var) = t.hasVarAtAll(self.ref.get_lexeme())
    if hasvar:
      return var
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun miembro llamado %s"
                          % (t.name.get_lexeme(), self.ref.get_lexeme()))

  def _resolve_var(self, val):
    if isToken(val.type) and val.type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Los tipos primitivos no no pueden ser dereferenciados")

    t = val.ts.recFindType(val.type.get_lexeme())
    (hasvar, var) = t.hasVarAtAll(self.ref.get_lexeme())
    if not hasvar:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun miembro llamado %s"
                          % (t.name.get_lexeme(), self.ref.get_lexeme()))

    # a menos que sea un caso del estilo this.variable
    if val.name.get_lexeme() != "@this" and \
       val.name.get_lexeme() != "@super":
      if not var.isPublic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Se esta tratando de acceder a un miembro protegido de la clase %s"
                            % t.name.get_lexeme())
    return var

  def lit_or_string_resolve(self):
    if self.ref.get_type() == STRING_LITERAL:
      name = Token()
      name._lexeme = "@" + ("".join(random.choice(string.letters + string.digits) for i in xrange(10)))
      t = Token()
      t._lexeme = "String"
      t._line = self.ref.get_line()
      t._col = self.ref.get_col()
      t._type = STRING_LITERAL
      var = mjVariable(t, name, self.ref, self.ts)
      return var
    else:
      return self.ref

  def find_class_ts(self, ts=None):
    if ts is None:
      ts = self.ts
    if isClass(ts.owner()):
      return ts
    elif not ts.parent() is None:
      return self.find_class_ts(ts.parent())
    return None

  def inmediate_resolve(self):
    if self.ref.get_type() == THIS:
      # caso especial: this.loquesea o this
      # hay qeu devolver una variable del tipo actual, para que sea consistente con el resto de los checkeos
      # pero este this puede estar en bloques anidados, asi que hay qeu buscar la primer ts parent que isClassTs() == True
      cts = self.find_class_ts()
      if cts is None: # grave problema
        raise Exception("No existe ts de clase!!")

      cl = cts.owner()
      name = Token()
      name._lexeme = "@this"
      return mjVariable(cl.name, name, self.ref, ts=cts)
    elif self.ref.get_type() == SUPER:
      raise NotImplementedError()

    tmpts = self.ts
    found = False
    possible_static_var = False
    while (not tmpts is None) and (not found):
      found = tmpts.varExists(self.ref.get_lexeme())
      if not found:
        # tal vez sea un miembro estatico de una clase
        found = tmpts.typeExists(self.ref.get_lexeme())
        if found:
          possible_static_var = True
      if not found:
        tmpts = tmpts.parent()

    if not found:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Referencia a identificador desconocido: %s"
                          % self.ref.get_lexeme())
    else:
      if not possible_static_var:
        return tmpts.getVar(self.ref.get_lexeme())
      else:
        return tmpts.getType(self.ref.get_lexeme())

  def compatibleWith(self, othertype):
    if self.type > 0: #token
      if literalToType(self.type) != REF_TYPE:
        return literalToType(self.type) == othertype.get_type() # othertype siempre va a ser un token
      else:
        # en este caso es un IDENTIFIER, asi qeu hay qeu resolverlo
        self.pprint()
        t = self.resolve()
        # si sale bien, me deberia dar una var
        return t.type.get_lexeme() == othertype.get_lexeme()
    else:
      return False # cada uno reimplementa esto

class mjMethodInvocation(mjPrimary):
  def __init__(self, prim, args):
    super(mjMethodInvocation, self).__init__(prim.ref, mjPrimary.MethodInv)
    self.goesto = prim.goesto
    self.args = args

  def set_ts(self,ts):
    self.ts = ts
    for a in self.args:
      if isinstance(a, mjPrimary):
        a.set_ts(ts)
    if not self.goesto is None:
      self.goesto.set_ts(ts)

  def inmediate_resolve(self):
    if self.ref.get_type() == THIS:
      # caso especial: this.loquesea o this
      # hay qeu devolver una variable del tipo actual, para que sea consistente con el resto de los checkeos
      # pero este this puede estar en bloques anidados, asi que hay qeu buscar la primer ts parent que isClassTs() == True
      cts = self.find_class_ts()
      if cts is None: # grave problema
        raise Exception("No existe ts de clase!!")

      cl = cts.owner()
      name = Token()
      name._lexeme = "@this"
      return mjVariable(cl.name, name, self.ref, ts=cts)
    elif self.ref.get_type() == SUPER:
      raise NotImplementedError()

    tmpts = self.ts
    found = False
    possible_static_var = False
    while (not tmpts is None) and (not found):
      found = tmpts.methodExists(self.call_signature())
      if not found:
        tmpts = tmpts.parent()

    if not found:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Referencia a metodo desconocido: %s"
                          % self.call_signature())
    else:
      return tmpts.getMethod(self.call_signature())

  def _resolve_class(self, val):
    print "DESDE METHODINV"
    # Este es el caso de acceso a un metodo estatico
    if val.ts.methodExists(self.call_signature()):
      method = val.ts.getMethod(self.call_signature())
      if method.isPublic() and method.isStatic():
        return method
      else:
        if method.isProtected():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Se esta tratando de acceder a un miembro protegido de %s"
                              % val.name.get_lexeme())
        else:
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Para acceder a %s debe crear una instancia de %s primero."
                              % (self.ref.get_lexeme(), val.name.get_lexeme()))
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "%s no pertenece a la clase %s"
                          % (self.ref.get_lexeme(), val.name.get_lexeme()))

  def _resolve_method(self, val):
    print "DESDE METHODINV2"
    raise NotImplementedError()

  def _resolve_var(self, val):
    print "DESDE METHODINV3"
    if val.type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Los tipos primitivos no no pueden ser dereferenciados")
    t = val.ts.recFindType(val.type.get_lexeme())
    t.pprint()
    raise NotImplementedError()


  def to_string(self):
    return "[" + self.type_to_str() + "::" + self.ref.get_lexeme() + "]"

  def pprint(self, tabs=0):
    print "  "*tabs + self.to_string()
    print "  "*tabs + "((("
    for a in self.args:
      a.pprint(tabs+1)
    print "  "*tabs + ")))"
    if not self.goesto is None:
      self.goesto.pprint(tabs+1)

  def call_signature(self):
    param_str = []
    for a in self.args:
      res = a.resolve()
      if isToken(res) and literalToType(res.get_type()) != REF_TYPE:
        param_str.append(typeToStr(literalToType(res.get_type())))
      elif isToken(res.type):
        param_str.append(res.type.get_lexeme())
      else: # es un mjClass
        param_str.append(res.type.name.get_lexeme())

    return self.ref.get_lexeme()+"("+(",".join(param_str))+")"

  def compatibleWith(self, othertype):
    m = self.resolve()
    if m.ret_type > 0: #token
      if literalToType(m.ret_type.get_type()) != REF_TYPE:
        return literalToType(m.ret_type.get_type()) == othertype.get_type() # othertype siempre va a ser un token
      else:
        # en este caso es un IDENTIFIER, asi qeu hay qeu resolverlo
        t = self.resolve()
        # si sale bien, me deberia dar un method
        return t.ret_type.get_lexeme() == othertype.get_lexeme()
    else:
      return False

class mjClassInstanceCreation(mjMethodInvocation):
  def __init__(self, prim, args):
    super(mjClassInstanceCreation, self).__init__(prim, args)
    self.type = mjPrimary.ClassInstCreat

  def compatibleWith(self, othertype):
    if self.type > 0:
      if literalToType(self.type) != REF_TYPE:
        return False
      else:
        raise Exception()
        return False
    else:
      t = self.resolve()
      return t.type.get_lexeme() == othertype.get_lexeme()

  def inmediate_resolve(self):
    if self.ref.get_type() == THIS:
      # caso especial: this.loquesea o this
      # hay qeu devolver una variable del tipo actual, para que sea consistente con el resto de los checkeos
      # pero este this puede estar en bloques anidados, asi que hay qeu buscar la primer ts parent que isClassTs() == True
      cts = self.find_class_ts()
      if cts is None: # grave problema
        raise Exception("No existe ts de clase!!")

      cl = cts.owner()
      name = Token()
      name._lexeme = "@this"
      return mjVariable(cl.name, name, self.ref, ts=cts)
    elif self.ref.get_type() == SUPER:
      raise NotImplementedError()

    tmpts = self.ts
    found = False
    possible_static_var = False
    while (not tmpts is None) and (not found):
      # buscamos una clase que se llame como el metodo
      found = tmpts.typeExists(self.ref.get_lexeme())
      if not found:
        tmpts = tmpts.parent()

    if not found:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Referencia a constructor desconocido: %s"
                          % self.call_signature())
    else:
      cl = tmpts.getType(self.ref.get_lexeme())
      if cl.ts.methodExists(self.call_signature()):
        return cl.ts.getMethod(self.call_signature())
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No existe ningun constructor con el signature %s"
                            % self.call_signature())

  def resolve(self):
    if self.ref.get_type() in FIRST_literal:
      return self.lit_or_string_resolve()

    if self.goesto is None:
      # resolvemos el metodo
      t = self.inmediate_resolve()
      # si no es un constructor
      if not t.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "%s no es una clase valida"
                            % self.ref.get_lexeme())
      name = Token()
      name._lexeme = "@" + ("".join(random.choice(string.letters + string.digits) for i in xrange(10)))
      return mjVariable(t.name, name, ts=self.ts)
    else:
      # esto se levanta en la etapa sintactica, pero por las dudas...
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "No se pueden crear clases de tipos dereferenciados")

class mjExpression(mjPrimary):
  def __init__(self, op):
    super(mjExpression, self).__init__(op, type=mjPrimary.Expr)

  def to_string(self):
    return "[" + self.type_to_str() + "]"

  def pprint(self, tabs=0):
    print "-"*15
    print "  "*tabs + self.to_string()
    if instanceof(self.ref, mjOp):
      self.ref.pprint()
    print "-"*15
    if not self.goesto is None:
      self.goesto.pprint(tabs+1)

class mjAssignment(mjPrimary):
  def __init__(self, prim, expr):
    if isMethodInv(prim):
      raise SemanticError(prim.ref.get_line(), prim.ref.get_col(),
                          "Lado izquierdo de la asignacion no valido")
    super(mjAssignment, self).__init__(prim.ref, mjPrimary.Assignment)
    self.goesto = prim.goesto
    self.expr = expr

  def to_string(self):
    return "[" + self.type_to_str() + "]"

  def pprint(self, tabs=0):
    s = self.to_string()
    print "  "*tabs + s
    print "  "*(tabs+1) + self.ref.get_lexeme()
    if not self.goesto is None:
      self.goesto.pprint(tabs+1)
    self.expr.pprint(tabs+1)

  def check(self):
    left = self.resolve()
    right = self.expr.resolve()

    if isToken(left): # los stringlits se devuelven como mjvars
      raise SemanticError(left.get_line(), left.get_col(),
                          "No se puede realizar una asignacion hacia un literal")
    elif left.type.get_lexeme() == "String" and left.name.get_lexeme().startswith("@"):
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "No se puede realizar una asignacion hacia un literal")
    if isToken(right):
      t = literalToType(right.get_type())
      if t == REF_TYPE:
        if right.get_type() != STRING_LITERAL:
          raise Exception("Error interno, token no resuelto")
        else:
          raise NotImplementedError()
      else:
        if left.type.get_type() == t:
          # entonces los tipos son compatibles
          print "YEAH"
        else:
          raise SemanticError(right.get_line(), right.get_col(),
                              "Tipos incompatibles en asignacion")
    else:
      print left.type
      print right.type
      if left.type.get_lexeme() != right.type.get_lexeme():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Tipos incompatibles en asignacion, no se puede asignar"
                            "un %s a un %s."
                            % (right.type.get_lexeme(), left.type.get_lexeme()))

class mjOp(mjPrimary):
  def __init__(self, symbol, operands):
    self.symbol = symbol
    self.operands = operands

  def pprint(self, tabs=0):
    print "  "*tabs + self.symbol
    for o in self.operands:
      o.pprint(tabs+1)

class mjOr(mjOp):
  def __init__(self, operands):
    super(mjOr, self).__init__("||", operands)

class mjAnd(mjOp):
  def __init__(self, operands):
    super(mjAnd, self).__init__("&&", operands)

class mjEq(mjOp):
  def __init__(self, operands):
    super(mjEq, self).__init__("==", operands)

class mjNotEq(mjOp):
  def __init__(self, operands):
    super(mjNotEq, self).__init__("!=", operands)

class mjLt(mjOp):
  def __init__(self, operands):
    super(mjLt, self).__init__("<", operands)

class mjGt(mjOp):
  def __init__(self, operands):
    super(mjGt, self).__init__(">", operands)

class mjLtEq(mjOp):
  def __init__(self, operands):
    super(mjLtEq, self).__init__("<=", operands)

class mjGtEq(mjOp):
  def __init__(self, operands):
    super(mjGtEq, self).__init__(">=", operands)

class mjAdd(mjOp):
  def __init__(self, operands):
    super(mjAdd, self).__init__("+", operands)

class mjSub(mjOp):
  def __init__(self, operands):
    super(mjSub, self).__init__("-", operands)

class mjMul(mjOp):
  def __init__(self, operands):
    super(mjMul, self).__init__("*", operands)

class mjDiv(mjOp):
  def __init__(self, operands):
    super(mjDiv, self).__init__("/", operands)

class mjMod(mjOp):
  def __init__(self, operands):
    super(mjMod, self).__init__("%", operands)

class mjNot(mjOp):
  def __init__(self, operands):
    super(mjNot, self).__init__("!", operands)

ops = {ADD             : mjAdd,
       SUB             : mjSub,
       DIV             : mjDiv,
       MUL             : mjMul,
       MOD             : mjMod,
       NOT             : mjNot,
       LT              : mjLt,
       GT              : mjGt,
       LT_EQ           : mjLtEq,
       GT_EQ           : mjGtEq,
       EQUALS          : mjEq,
       NOT_EQUALS      : mjNotEq,
       CONDITIONAL_AND : mjAnd,
       CONDITIONAL_OR  : mjOr,
       }
