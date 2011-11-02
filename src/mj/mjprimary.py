from mjcheckers import mjCheckable
from constants import *
from errors import SemanticError
from mjclass import isClass, mjVariable, isVariable, isMethod, isClassVariable
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
    self.var = None

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

    if val.is_constructor():
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "No se puede dereferenciar la llamada a un constructor")

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

  def find_method_ts(self, ts=None):
    if ts is None:
      ts = self.ts
    if isMethod(ts.owner()):
      return ts
    elif not ts.parent() is None:
      return self.find_method_ts(ts.parent())
    return None

  def set_var(self, v):
    self.var = v
    if not self.goesto is None:
      self.goesto.set_var(v)

  def inmediate_resolve(self):
    cts = self.find_class_ts()
    if cts is None: # grave problema
      raise Exception("No existe ts de clase!!")

    cl = cts.owner()

    mts = None
    mt = None
    # caso especial!
    # o estamos adentro de un metodo, o en un initializer de una var de clase
    # en el segundo caso, el parent del parent de la ts actual es None, porque el parent
    # es el ts global
    if self.ts.parent().parent() is None:
      # esto significa que es un llamado _*FUERA*_ de un metodo!
      # entonces los checkeos de metodo (en mt) ahora en realidad se tienen
      # que hacer sobre la variable hacia la cual se le asigna esto
      mt = self.var
    else:
      mts = self.find_method_ts()
      if mts is None:
        raise Exception("No existe ts de metodo!!!")
      mt = mts.owner()

    if self.ref.get_type() == THIS:
      # caso especial: this.loquesea o this
      # si el metodo donde se lo llama es estatico es un error
      if mt.isStatic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No se puede usar this en un metodo static.")

      # hay qeu devolver una variable del tipo actual, para que sea consistente con el resto de los checkeos
      # pero este this puede estar en bloques anidados, asi que hay qeu buscar la primer ts parent que isClassTs() == True
      name = Token()
      name._lexeme = "@this"
      return mjVariable(cl.name, name, self.ref, ts=cts)
    elif self.ref.get_type() == SUPER:
      if mt.isStatic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No se puede usar super en un metodo static.")

      if cl.ext_class is None:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No se encontro la clase padre.")
      name = Token()
      name._lexeme = "@super"
      return mjVariable(cl.name, name, self.ref, ts=cts)

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
        v = tmpts.getVar(self.ref.get_lexeme())
        if mt.isStatic() and isClassVariable(v) and not v.isStatic():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Referencia a identificador no static desde un metodo static")
        return v
      else:
        return tmpts.getType(self.ref.get_lexeme())

  def compatibleWith(self, othertype):
    if literalToType(self.type) != REF_TYPE:
      return literalToType(self.type) == othertype.get_type() # othertype siempre va a ser un token
    else:
      # en este caso es un IDENTIFIER, asi qeu hay qeu resolverlo
      self.pprint()
      t = self.resolve()
      # si sale bien, me deberia dar una var
      return t.type.get_lexeme() == othertype.get_lexeme()

  def check(self):
    self.resolve()

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
    mts = None
    mt = None
    # caso especial!
    # o estamos adentro de un metodo, o en un initializer de una var de clase
    # en el segundo caso, el parent del parent de la ts actual es None, porque el parent
    # es el ts global
    if self.ts.parent().parent() is None:
      # esto significa que es un llamado _*FUERA*_ de un metodo!
      # entonces los checkeos de metodo (en mt) ahora en realidad se tienen
      # que hacer sobre la variable hacia la cual se le asigna esto
      mt = self.var
    else:
      mts = self.find_method_ts()
      if mts is None:
        raise Exception("No existe ts de metodo!!!")
      mt = mts.owner()

    cts = self.find_class_ts()
    if cts is None: # grave problema
      raise Exception("No existe ts de clase!!")

    cl = cts.owner()
    if self.ref.get_type() == THIS:
      # caso especial: this()
      if not isMethod(mt) or not mt.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Las llamadas explicitas a constructores solo pueden realizarse dentro de otros constructores.")
      # llama a otro constructor
      call = self.call_signature().replace("this", cl.name.get_lexeme())
      if cl.ts.methodExists(call):
        return cl.ts.getMethod(call)
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a constructor desconocido: %s"
                            % call)
    elif self.ref.get_type() == SUPER:
      # llama a constructor de la clase padre
      if not isMethod(mt) or not mt.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Las llamadas explicitas a constructores solo pueden realizarse dentro de otros constructores.")

      if cl.ext_class is None:
        raise Exception("Extends no resuelto!")

      call = self.call_signature().replace("super", cl.ext_name.get_lexeme())
      if cl.ext_class.ts.methodExists(call):
        return cl.ext_class.ts.getMethod(call)
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a constructor desconocido: %s"
                            % call)

    cts = self.find_class_ts()
    if cts is None: # grave problema
      raise Exception("No existe ts de clase!!")

    cl = cts.owner()

    (hasmethod, method) = cl.hasMethodAtAll(self.call_signature())
    if hasmethod:
      if mt.isStatic() and not method.isStatic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a metodo no static desde uno static")
      # se llama al constructor como si fuera un metodo cualquiera
      if method.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No se puede realizar una llamada a un constructor de esta forma.")
      # aca no se checkea por visibilidad porque es la misma clase
      return method
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Referencia a metodo desconocido: %s"
                          % self.call_signature())

  def _resolve_class(self, val):
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
    if val.ret_type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "%s no puede ser dereferenciado."
                          % val.ret_type.get_lexeme())

    # sino
    t = self.ts.recFindType(val.ret_type.get_lexeme())
    (hasvar, var) = t.hasMethodAtAll(self.ref.get_lexeme())
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
    (hasmethod, method) = t.hasMethodAtAll(self.call_signature())
    if not hasmethod:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun metodo %s"
                          % (t.name.get_lexeme(), self.call_signature()))

    # a menos que sea un caso del estilo this.variable
    if val.name.get_lexeme() != "@this" and \
       val.name.get_lexeme() != "@super":
      if not method.isPublic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Se esta tratando de acceder a un miembro protegido de la clase %s"
                            % t.name.get_lexeme())
    return method

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
      elif isMethod(res):
        # si la llamada es this() o super()
        if res.is_constructor():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "No se puede llamar a un constructor como un parametro para otra funcion.")
        else:
          param_str.append(res.ret_type.get_lexeme())
      elif isToken(res.type):
        param_str.append(res.type.get_lexeme())
      else: # es un mjClass
        param_str.append(res.type.name.get_lexeme())

    return self.ref.get_lexeme()+"("+(",".join(param_str))+")"

  def compatibleWith(self, othertype):
    m = self.resolve()
    if m.is_constructor():
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La llamada a un constructor debe realizarse con una sentencia new o como una sentencia individual.")

    if literalToType(m.ret_type.get_type()) != REF_TYPE:
      return literalToType(m.ret_type.get_type()) == othertype.get_type() # othertype siempre va a ser un token
    else:
      # en este caso es un IDENTIFIER, asi qeu hay qeu resolverlo
      t = self.resolve()
      # si sale bien, me deberia dar un method
      return t.ret_type.get_lexeme() == othertype.get_lexeme()

  def check(self):
    self.resolve()

class mjClassInstanceCreation(mjMethodInvocation):
  def __init__(self, prim, args):
    super(mjClassInstanceCreation, self).__init__(prim, args)
    self.type = mjPrimary.ClassInstCreat

  def compatibleWith(self, othertype):
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
        m = cl.ts.getMethod(self.call_signature())
        if m.isProtected():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "%s es un constructor protegido."
                              % self.call_signature())
        return m
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
      print self.ref
      # si no es un constructor
      if not t.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "%s no es una clase valida"
                            % self.ref.get_lexeme())
      name = Token()
      name._lexeme = "@" + ("".join(random.choice(string.letters + string.digits) for i in xrange(10)))
      name._line = self.ref.get_line()
      name._col = self.ref.get_col()
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
    self.left = prim
    self.expr = expr
    self.ts = None

  def set_ts(self, ts):
    self.ts = ts
    self.left.set_ts(ts)
    self.expr.set_ts(ts)

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
    left = self.left.resolve()
    right = self.expr.resolve()

    if isToken(left): # los stringlits se devuelven como mjvars
      raise SemanticError(left.get_line(), left.get_col(),
                          "No se puede realizar una asignacion hacia un literal")
    elif left.type.get_lexeme() == "String" and left.name.get_lexeme().startswith("@"):
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "No se puede realizar una asignacion hacia un literal")

    if not isVariable(left):
      raise SemanticError(left.name.get_line(), left.name.get_col(),
                          "El lado izquierdo de la asignacion es invalido")
    elif left.name.get_lexeme().startswith("@"):
      raise SemanticError(left.name.get_line(), left.name.get_col(),
                          "El lado izquierdo de la asignacion es invalido")

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
      if isMethod(right):
        if right.is_constructor():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "No se puede realizar una asignacion con un constructor, debe utilizar la sentencia new.")
        if left.type.get_lexeme() != right.ret_type.get_lexeme():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Tipos incompatibles en asignacion, no se puede asignar"
                              "un %s a un %s."
                              % (right.type.get_lexeme(), left.type.get_lexeme()))
      else:
        if left.type.get_lexeme() != right.type.get_lexeme():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Tipos incompatibles en asignacion, no se puede asignar"
                              "un %s a un %s."
                              % (right.type.get_lexeme(), left.type.get_lexeme()))

  def resolve(self):
    raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                        "La asignacion debe estar en un statement individual")

class mjOp(mjPrimary):
  def __init__(self, symbol, operands):
    super(mjOp, self).__init__(symbol)
    self.symbol = symbol
    self.operands = operands
    self.ts = None

  def set_ts(self, ts):
    self.ts = ts
    for o in self.operands:
      o.set_ts(ts)

  def pprint(self, tabs=0):
    print "  "*tabs + self.symbol.get_lexeme()
    for o in self.operands:
      o.pprint(tabs+1)

  def _var_type(self, r, types):
    if isToken(r):
      return (literalToType(r.get_type()), types[0])
    else:
      return (r.type.get_type(), types[0])

  def resolve(self):
    types = []
    r = None
    for o in self.operands:
      r = o.resolve()
      if isToken(r):
        types.append(typeToStr(literalToType(r.get_type())))
      else:
        types.append(r.type.get_lexeme())

    s = list(set(types))
    diffs = len(s)
    if diffs != 1:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operacion entre tipos incompatibles.")

    if not s[0] in ["String", "int", "boolean"]:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operacion con tipos no validos, solo pueden ser int, boolean o String.")

    name = Token()
    name._lexeme = "@" + ("".join(random.choice(string.letters + string.digits) for i in xrange(10)))
    name._line = self.symbol.get_line()
    name._col = self.symbol.get_col()
    t = Token()
    (rt, name_type) = self._var_type(r, types)
    t._lexeme = name_type
    t._line = self.symbol.get_line()
    t._col = self.symbol.get_col()
    t._type = rt
    var = mjVariable(t, name, ts=self.ts)
    return var

  def compatibleWith(self, othertype):
    m = self.resolve()
    if m.type.get_type() > 0: #token
      if literalToType(m.type.get_type()) != REF_TYPE:
        return literalToType(m.type.get_type()) == othertype.get_type() # othertype siempre va a ser un token
      else:
        return m.type.get_lexeme() == othertype.get_lexeme()
    else:
      return False

  def check(self):
    self.resolve()

class mjArithOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjArithOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if types[0] != "int":
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                         "No se puede realizar esta operacion sobre otro tipo que no sea int.")
    return (INT_TYPE, "int")

class mjBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "boolean" in types or "int" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones booleanas solo aceptan int o boolean.")

class mjStrictIntBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjStrictIntBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "int" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones booleanas solo aceptan int o boolean.")

class mjStrictBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjStrictBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "boolean" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones booleanas solo aceptan int o boolean.")

class mjOr(mjStrictBoolOp):
  def __init__(self, symbol, operands):
    super(mjOr, self).__init__(symbol, operands)

class mjAnd(mjStrictBoolOp):
  def __init__(self, symbol, operands):
    super(mjAnd, self).__init__(symbol, operands)

class mjEq(mjBoolOp):
  def __init__(self, symbol, operands):
    super(mjEq, self).__init__(symbol, operands)

class mjNotEq(mjBoolOp):
  def __init__(self, symbol, operands):
    super(mjNotEq, self).__init__(symbol, operands)

class mjLt(mjStrictIntBoolOp):
  def __init__(self, symbol, operands):
    super(mjLt, self).__init__(symbol, operands)

class mjGt(mjStrictIntBoolOp):
  def __init__(self, symbol, operands):
    super(mjGt, self).__init__(symbol, operands)

class mjLtEq(mjStrictIntBoolOp):
  def __init__(self, symbol, operands):
    super(mjLtEq, self).__init__(symbol, operands)

class mjGtEq(mjStrictIntBoolOp):
  def __init__(self, symbol, operands):
    super(mjGtEq, self).__init__(symbol, operands)

class mjAdd(mjOp):
  def __init__(self, symbol, operands):
    super(mjAdd, self).__init__(symbol, operands)

class mjSub(mjArithOp):
  def __init__(self, symbol, operands):
    super(mjSub, self).__init__(symbol, operands)

class mjMul(mjArithOp):
  def __init__(self, symbol, operands):
    super(mjMul, self).__init__(symbol, operands)

class mjDiv(mjArithOp):
  def __init__(self, symbol, operands):
    super(mjDiv, self).__init__(symbol, operands)

class mjMod(mjArithOp):
  def __init__(self, symbol, operands):
    super(mjMod, self).__init__(symbol, operands)

class mjNot(mjStrictBoolOp):
  def __init__(self, symbol, operands):
    super(mjNot, self).__init__(symbol, operands)

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
