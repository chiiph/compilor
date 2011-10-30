from mjcheckers import mjCheckable
from constants import *
from errors import SemanticError
from mjclass import isClass, mjVariable, isVariable
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
      if self.ref.get_type() == STRING_LITERAL:
        name = Token()
        name._lexeme = "".join(random.choice(string.letters + string.digits) for i in xrange(10))
        t = Token()
        t._lexeme = "String"
        t._type = STRING_LITERAL
        var = mjVariable(t, name, self.ref, self.ts)
        return var
      else:
        return self.ref

    if self.goesto is None:
      tmpts = self.ts
      found = False
      possible_static_var = False
      possible_static_method = False
      while (not tmpts is None) and (not found):
        found = tmpts.varExists(self.ref.get_lexeme())
        if not found:
          # tal vez sea un miembro estatico de una clase
          found = tmpts.typeExists(self.ref.get_lexeme())
          if found:
            possible_static_var = True
        if not found:
          found = tmpts.methodExists(self.ref.get_lexeme())
          if found:
            possible_static_method = True
        if not found:
          tmpts = tmpts.parent()

      if not found:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a identificador desconocido: %s"
                            % self.ref.get_lexeme())
      else:
        if not possible_static_var and not possible_static_method:
          return tmpts.getVar(self.ref.get_lexeme())
        elif not possible_static_method:
          return tmpts.getType(self.ref.get_lexeme())
        else:
          return tmpts.getMethod(self.ref.get_lexeme())
    else:
      val = self.goesto.resolve()
      print "BBBBBBBBBBBBBB", val, self.ref
      if isClass(val):
        val.ts.pprint()
        print "UAUAUA"
        # el goesto es una mjClass, por ende puede ser un static var
        if isVariable(val):
          if val.ts.varExists(self.ref.get_lexeme()):
            print "POR ACAA SIIIIII"
            var = val.ts.getVar(self.ref.get_lexeme())
            if var.isStatic() and var.isPublic():
              return var
            else:
              if var.isProtected():
                raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                    "Se esta tratando de acceder a un miembro protegido de la clase %s"
                                    % val.name.get_lexeme())
              else:
                raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                    "Debe crear una instancia de %s para acceder al miembro %s"
                                    % (val.name.get_lexeme(), var.name.get_lexeme()))
        elif isMethodInv(val):
          if val.ts.methodExists(self):
            var = val.ts.getMethod(self.ref.get_lexeme())
            if var.isStatic() and var.isPublic():
              return var
            else:
              if var.isProtected():
                raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                    "Se esta tratando de acceder a un miembro protegido de la clase %s"
                                    % val.name.get_lexeme())
              else:
                raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                    "Debe crear una instancia de %s para acceder al miembro %s"
                                    % (val.name.get_lexeme(), var.name.get_lexeme()))
      elif isMethodInv(val):
        raise NotImplementedError()
      elif isVariable(val):
        if val.type.get_type() in FIRST_primitive_type:
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Los tipos primitivos no no pueden ser dereferenciados")
        t = val.ts.recFindType(val.type.get_lexeme())
        t.pprint()
        if isMethodInv(self):
          if not t.ts.methodExists(self.call_signature()):
            raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                "La clase %s no tiene ningun metodo con el signature %s"
                                % (t.name.get_lexeme(), self.call_signature()))

        raise NotImplementedError()
      elif isToken(val):
        print val
        raise NotImplementedError()

  def compatibleWith(self, othertype):
    if self.type > 0: #token
      if literalToType(self.type) != REF_TYPE:
        return literalToType(self.type) == othertype.get_type() # othertype siempre va a ser un token
      else:
        raise Exception()
        return False
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
    self.ts.parent().parent().pprint()
    param_str = []
    for a in self.args:
      res = a.resolve()
      if isToken(res) and literalToType(res.get_type()) != REF_TYPE:
        param_str.append(typeToStr(literalToType(res.get_type())))
      else:
        print type(res)
        param_str.append(res.type.get_lexeme())

    return self.ref.get_lexeme()+"("+(",".join(param_str))+")"

class mjClassInstanceCreation(mjMethodInvocation):
  def __init__(self, prim, args):
    super(mjClassInstanceCreation, self).__init__(prim, args)
    self.type = mjPrimary.ClassInstCreat

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

    if isToken(left) or left.type.get_lexeme() == "String": # los stringlits se devuelven como mjvars
      raise SemanticError(left.get_line(), left.get_col(),
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
      if left.type.get_type() == right.type.get_type():
        print "YEAH PARA VARS"
      else:
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
