from mjcheckers import mjCheckable
from constants import *

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

    self.goesto = None

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

class mjMethodInvocation(mjPrimary):
  def __init__(self, prim, args):
    super(mjMethodInvocation, self).__init__(prim.ref, mjPrimary.MethodInv)
    self.args = args

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
    super(mjAssignment, self).__init__(prim.ref, mjPrimary.Assignment)
    self.expr = expr

  def to_string(self):
    return "[" + self.type_to_str() + "]"

  def pprint(self, tabs=0):
    s = self.to_string()
    print "  "*tabs + s
    print "  "*(tabs+1) + self.ref.get_lexeme()
    self.expr.pprint(tabs+1)
    if not self.goesto is None:
      self.goesto.pprint(tabs+1)

class mjOp(object):
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
