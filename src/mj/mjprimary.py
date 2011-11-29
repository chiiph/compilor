from mjcheckers import mjCheckable
from constants import *
from errors import SemanticError
from mjclass import isClass, mjVariable, isVariable, isMethod, isClassVariable, mjClass, mjMethod, mjBlock
from firsts import FIRST_literal, FIRST_primitive_type
from lexor import Token, isToken

from memoize import memoized

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

def isAssignment(obj):
  return isinstance(obj, mjAssignment)

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

    self.code = ""

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

  @memoized
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
        # tenemos qeu buscar en el ts de la clase, si hay una variable con el nombre este
        # y ver si es estatica y publica
        return self._resolve_class(val)
      elif isMethod(val):
        # o es el caso de algo.unmetodo().attr
        return self._resolve_method(val)
      elif isVariable(val):
        # o es el caso de que es una variable, no importa de que (ya se resolvio antes)
        # ....atributo.attr
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
    (hasvar, var) = val.hasVarAtAll(self.ref.get_lexeme())
    if hasvar:
      if var.isPublic() and var.isStatic():

        cr = var.ts.owner().cr
        ### CODE
        self.code += "push %s ; %s\n" % (cr, val.name.get_lexeme())
        self.code += "loadref %d ; .%s\n" % (var.offset, var.name.get_lexeme())
        ### /CODE

        return var
      else:
        if var.isProtected():
          cts = self.find_class_ts()
          if cts is None: # grave problema
            raise Exception("No existe ts de clase!!")

          cl = cts.owner()
          if not cl.inheritsFrom(val.name.get_lexeme()):
            raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                "Se esta tratando de acceder a un miembro protegido de %s"
                                % val.name.get_lexeme())

          cr = var.ts.owner().cr
          ### CODE
          self.code += "push %s ; %s\n" % (cr, val.name.get_lexeme())
          self.code += "loadref %d ; .%s\n" % (var.offset, var.name.get_lexeme())
          ### /CODE


          return var
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
    if val.ret_type.get_type() == VOID_TYPE:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "void no puede ser dereferenciado.")

    t = self.ts.recFindType(val.ret_type.get_lexeme())
    (hasvar, var) = t.hasVarAtAll(self.ref.get_lexeme())
    if hasvar:

      ### CODE
      self.code += "loadref %d ; %s\n" % (var.offset, var.name.get_lexeme())
      ### /CODE

      return var
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun miembro llamado %s"
                          % (t.name.get_lexeme(), self.ref.get_lexeme()))

  def _resolve_var(self, val):
    if isToken(val.type) and val.type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Los tipos primitivos no no pueden ser dereferenciados")

    if val.type.get_type() == VOID_TYPE:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "void no puede ser dereferenciado.")

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
        cts = self.find_class_ts()
        if cts is None: # grave problema
          raise Exception("No existe ts de clase!!")

        cl = cts.owner()
        if not cl.inheritsFrom(val.type.get_lexeme()):
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Se esta tratando de acceder a un miembro protegido de la clase %s"
                              % t.name.get_lexeme())
    ### CODE
    self.code += "loadref %d ; %s\n" % (var.offset, var.name.get_lexeme())
    ### /CODE
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

      ### CODE
      # len + 1 (\0) + 1 (vtable)
      self.code += "rmem 1\n"
      self.code += "push %d ; len(%s) + \\0 + vtable \n" % (len(self.ref.get_lexeme()[:-1][1:])+1+1,
                                                            self.ref.get_lexeme())
      self.code += "push simple_malloc\n"
      self.code += "call\n"
      self.code += "dup\n"
      self.code += "push VT_String\n"
      self.code += "storeref 0\n"
      self.code += "dup\n"
      i = 0
      for ch in self.ref.get_lexeme()[:-1][1:]:
        if ch == "\\":
          continue
        i += 1
        self.code += "push '%s'\n" % ch
        self.code += "storeref %d\n" % i
        self.code += "dup\n"
      i += 1
      self.code += "push 0\n"
      self.code += "storeref %d\n" % i
      ### /CODE

      return var
    else:

      ### CODE
      if self.ref.get_type() == CHAR_LITERAL:
        self.code += "push %d; char lit %s \n" % (ord(self.ref.get_lexeme()[1:][:-1]),
                                                  self.ref.get_lexeme())
      elif self.ref.get_type() == TRUE:
        t = 1
        self.code += "push %d; %s\n" % (t, self.ref.get_lexeme())
      elif self.ref.get_type() == FALSE:
        t = 0
        self.code += "push %d; %s\n" % (t, self.ref.get_lexeme())
      else: # INT_LITERAL
        self.code += "push %s ; int lit\n" % self.ref.get_lexeme()
      ### /CODE

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
    ### Casos especiales
    if self.ref.get_lexeme() == "System":
      return mjClass(self.ref, None, [], None)
    ### /Casos especiales

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

      ### CODE
      self.code += "load %d ; this\n" % 3 # fp -> d -> r -> this
      ### /CODE

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

      ### CODE
      # es igual a this, el cambio esta mas adelante cuando se resuelva
      # la parte siguiente del primary
      self.code += "load %d ; super\n" % 3 # fp -> d -> r -> this
      ### /CODE

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
        if isClassVariable(v) and v.isStatic():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Para acceder a variables estaticas se debe hacer Clase.variable")
        ### CODE
        if isClassVariable(v):
          # si es una var de instancia, cargo this y despues loadref del offset en el CIR
          self.code += "load %d ; this\n" % 3 # agregamos el this
          self.code += "loadref %d ; .%s\n" % (v.offset, self.ref.get_lexeme())
        else:
          # sino, es una variable local o un parametro
          self.code += "load %d ; %s\n" % (v.offset, self.ref.get_lexeme())
        ### /CODE

        return v
      else:
        ### CODE
        # No se hace nada, en la siguiente parte del primary
        # se buscara un label de metodo o un offset del CR
        ### /CODE
        return tmpts.getType(self.ref.get_lexeme())

  def compatibleWith(self, othertype):
    # othertype siempre es un tipo, este se llama para casos como
    # declaracion de variables, y en othertype esta el tipo de la decl

    right = ""
    left = ""

    right_t = literalToType(self.ref.get_type())
    if right_t == REF_TYPE:
      # aca hay que hacer resolve
      if right_t == STRING_LITERAL:
        right = "String"
      else:
        right = self.resolve()
        if isToken(right):
          right = typeToStr(literalToType(right.get_type()))
        else:
          if isMethod(right):
            right = right.ret_type.get_lexeme()
          else:
            right = right.type.get_lexeme()
    else:
      right = typeToStr(right_t)

    left_t = othertype.get_lexeme()
    if not left_t in ["int", "char", "boolean", "String"]:
      left = othertype.get_lexeme()
    else:
      left = left_t

    mjType.compatible(left, right, self.ts,
                      self.ref.get_line(), self.ref.get_col())

    return True

  def get_rec_code(self):
    if self.goesto is None:
      return self.code

    return self.goesto.get_rec_code() + self.code

  @memoized
  def check(self):
    self.resolve()
    return self.get_rec_code()

class mjMethodInvocation(mjPrimary):
  def __init__(self, prim, args):
    super(mjMethodInvocation, self).__init__(prim.ref, mjPrimary.MethodInv)
    self.goesto = prim.goesto
    self.args = args

  def set_var(self, var):
    super(mjMethodInvocation, self).set_var(var)
    for a in self.args:
      if isinstance(a, mjPrimary):
        a.set_var(var)

  def set_ts(self,ts):
    self.ts = ts
    for a in self.args:
      if isinstance(a, mjPrimary):
        a.set_ts(ts)
    if not self.goesto is None:
      self.goesto.set_ts(ts)

  def compatible_args(self, params):
    if len(self.args) != len(params):
      return False

    for i in range(0, len(self.args)):
      try:
        if not self.args[i].compatibleWith(params[i][0]):
          return False
      except SemanticError, e:
        return False
    return True

  def get_compatible_methods(self, method_list):
    ret = []
    for m in method_list:
      if self.compatible_args(m.params):
        ret.append(m)
    return ret

  def get_call_distance(self, method):
    nums = []
    for i in range(0, len(self.args)):
      if method.params[i][0].get_type() == IDENTIFIER:
        a = self.args[i].resolve()
        type = ""
        if isMethod(a):
          type = a.ret_type.get_lexeme()
        else:
          type = a.type.get_lexeme()
        nums.append(mjType.distance(method.params[i][0].get_lexeme(),
                                    type,
                                    self.ts)
                    )
    if len(nums) == 0:
      return 0
    return float(sum(nums)) / float(len(nums))

  def get_most_specific_call(self, method_list):
    comp = self.get_compatible_methods(method_list)
    min_dst = 99999999999
    cur_dst = 0.0
    min_meth = None
    ret_list = []
    for m in comp:
      cur_dst = self.get_call_distance(m)
      if cur_dst <= min_dst:
        min_meth = m
        min_dst = cur_dst
    for m in comp:
      if self.get_call_distance(m) == min_dst:
        ret_list.append(m)
    return ret_list

  def get_THE_method(self, methods, line, col):
    specific = self.get_most_specific_call(methods)
    if len(specific) > 1:
      candidates = ""
      for m in specific:
        candidates += "  " + m.get_signature() + "\n"
      raise SemanticError(line, col,
                          "Llamada ambigua, los candidatos son:\n"
                          "%s" % candidates)
    elif len(specific) < 1:
      raise SemanticError(line, col,
                          "No existe metodo")
    return specific[0]

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
                            "Las llamadas explicitas a constructores solo "
                            "pueden realizarse dentro de otros constructores.")
      # llama a otro constructor
      call = self.call_signature().replace("this", cl.name.get_lexeme())
      # cambiamos el "super" por el nombre de la clase para buscar el constructor
      self.ref._lexeme = cl.name.get_lexeme()
      if cl.ts.methodInvExists(self):
        methods = cl.ts.getMethod(self)
        self.ref._lexeme = "this"
        m = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())

        ### CODE
        self.code += "load 3 ; this\n"
        self.code += "push %s ; %s\n" % (m.label, m.get_signature())
        self.code += "call\n"
        ### /CODE

        return m
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a constructor desconocido: %s"
                            % call)
    elif self.ref.get_type() == SUPER:
      # llama a constructor de la clase padre
      if not isMethod(mt) or not mt.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Las llamadas explicitas a constructores solo pueden "
                            "realizarse dentro de otros constructores.")

      if cl.ext_class is None:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a constructor de super clase desconocido.")

      call = self.call_signature().replace("super", cl.ext_class.name.get_lexeme())
      # cambiamos el "super" por el nombre de la clase para buscar el constructor
      self.ref._lexeme = cl.ext_name.get_lexeme()
      if cl.ext_class.ts.methodInvExists(self):
        methods = cl.ext_class.ts.getMethod(self)
        self.ref._lexeme = "super"
        m = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())

        ### CODE
        self.code += "load 3 ; super\n"
        self.code += "push %s ; %s\n" % (m.label, m.get_signature())
        self.code += "call\n"
        ### /CODE

        return m
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a constructor desconocido: %s"
                            % call)

    cts = self.find_class_ts()
    if cts is None: # grave problema
      raise Exception("No existe ts de clase!!")

    cl = cts.owner()

    (hasmethod, methods) = cl.hasMethodInvAtAll(self)

    if hasmethod:
      method = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())
      if mt.isStatic() and not method.isStatic():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Referencia a metodo no static desde uno static")
      # se llama al constructor como si fuera un metodo cualquiera
      if method.is_constructor():
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No se puede realizar una llamada a un constructor de esta forma.")
      # aca no se checkea por visibilidad porque es la misma clase

      ### CODE
      if method.isStatic():
        self.code += "push %s ; (static)%s\n" % (method.label, method.get_signature())
      else:
        self.code += "load %d ; this\n" % 3
        self.code += "dup\n" # duplica para que quede this en la llamada
        self.code += "loadref 0 ; vtable\n"
        self.code += "loadref %d ; offset de %s en la vtable\n" % (method.offset,
                                                                   method.get_signature())
      self.code += "call\n"
      ### /CODE
      return method
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Referencia a metodo desconocido: %s"
                          % self.call_signature())

  def _resolve_class(self, val):
    ### Casos especiales
    if val.name.get_lexeme() == "System":
      if not self.ref.get_lexeme() in ["print", "println", "read"]:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "El metodo %s no pertenece a System."
                            % self.ref.get_lexeme())
      if self.ref.get_lexeme() == "read":
        if len(self.args) != 0:
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Llamada con parametros invalidos a %s."
                              % self.ref.get_lexeme())

      if self.ref.get_lexeme() == "read" and len(self.args) != 0 or \
         self.ref.get_lexeme() == "print" and len(self.args) != 1 or \
         self.ref.get_lexeme() == "println" and len(self.args) > 1:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Llamada con parametros invalidos a %s."
                            % self.ref.get_lexeme())

      r = self.args[0].resolve()
      if len(self.args) == 1:
        if isMethodInv(r):
          if not r.ret_type.get_lexeme() in ["boolean", "int", "char", "String"]:
            raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                "Llamada con parametros invalidos a %s."
                                % self.ref.get_lexeme())
        elif isVariable(r):
          if (not r.type.get_type() in [BOOLEAN_TYPE, INT_TYPE, CHAR_TYPE, STRING_LITERAL]) and \
             (r.type.get_type() == IDENTIFIER and r.type.get_lexeme() != "String"):
            print r.type
            raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                                "Llamada con parametros invalidos a %s."
                                % self.ref.get_lexeme())


      m = self.ref.get_lexeme()
      t = None
      if len(self.args) == 1:
        r = self.args[0].resolve()
        if isMethod(r):
          t = r.ret_type.get_lexeme()
        else:
          if isToken(r):
            t = typeToStr(literalToType(r.get_type()))
          else:
            t = r.type.get_lexeme()

      if m == "print" or m == "println" and len(self.args) == 1:
        if t == "boolean":
          self.code += "bprint\n"
        elif t == "int":
          self.code += "iprint\n"
        elif t == "char":
          self.code += "cprint\n"
        elif t == "String":
          self.code += "push 1\n"
          self.code += "add\n"
          self.code += "sprint\n"

      if m == "println":
        self.code += "prnln\n"

      if m == "read":
        self.code += "read\n"
      ret = Token()
      ret._lexeme = "void"
      ret._type = VOID_TYPE
      return mjMethod([], ret, self.ref, [], mjBlock(), None)
    ### /Casos especiales

    # Este es el caso de acceso a un metodo estatico
    if val.ts.methodInvExists(self):
      methods = val.ts.getMethod(self)
      method = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())
      if method.isPublic() and method.isStatic():

        ### CODE
        self.code += "push %s ; (static)%s.%s\n" % (method.label,
                                                    val.name.get_lexeme(),
                                                    method.get_signature())
        self.code += "call\n"
        ### /CODE

        return method
      else:
        if method.isProtected():
          cts = self.find_class_ts()
          if cts is None: # grave problema
            raise Exception("No existe ts de clase!!")

          cl = cts.owner()
          if not cl.inheritsFrom(val.name.get_lexeme()):
            raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Se esta tratando de acceder a un miembro protegido de %s"
                              % val.name.get_lexeme())
          return method
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

    (doret, retval) = self.handle_string(val)
    if doret:
      return retval

    # sino
    if val.ret_type.get_type() == VOID_TYPE:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "void no puede ser dereferenciado.")

    t = self.ts.recFindType(val.ret_type.get_lexeme())
    (hasmethod, methods) = t.hasMethodInvAtAll(self)
    if hasmethod:
      m = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())

      ### CODE
      self.code += "dup\n" # duplico el this de la variable que viene de val
      self.code += "loadref 0 ; vtable \n"
      self.code += "loadref %d ; offset a %s\n" % (m.offset, m.get_signature())
      self.code += "call\n"
      ### /CODE

      return m
    else:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun metodo %s"
                          % (t.name.get_lexeme(), self.call_signature()))

  def _resolve_var(self, val):
    if isToken(val.type) and val.type.get_type() in FIRST_primitive_type:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Los tipos primitivos no pueden ser dereferenciados")

    if val.type.get_type() == VOID_TYPE:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "void no puede ser dereferenciado.")

    (doret, retval) = self.handle_string(val)
    if doret:
      return retval

    t = val.ts.recFindType(val.type.get_lexeme())
    (hasmethod, methods) = t.hasMethodInvAtAll(self)
    if not hasmethod:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "La clase %s no posee ningun metodo %s"
                          % (t.name.get_lexeme(), self.call_signature()))

    method = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())
    # a menos que sea un caso del estilo this.metodo()
    if val.name.get_lexeme() != "@this" and \
       val.name.get_lexeme() != "@super":
      if not method.isPublic():
        cts = self.find_class_ts()
        if cts is None: # grave problema
          raise Exception("No existe ts de clase!!")

        cl = cts.owner()
        if not cl.inheritsFrom(val.type.get_lexeme()):
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "Se esta tratando de acceder a un miembro protegido de la clase %s"
                              % t.name.get_lexeme())

    ### CODE
    if val.name.get_lexeme() == "@super":
      # buscamos el metodo en el parent
      m = method.ts.parent().owner().ext_class.ts.getExactMethod(method)
      self.code += "push %s\n" % m.label
      self.code += "call\n"
    else:
      self.code += "dup\n"
      self.code += "loadref 0 ; vtable \n"
      self.code += "loadref %d ; offset a %s\n" % (method.offset, method.get_signature())
      self.code += "call\n"
    ### /CODE
    return method

  def handle_string(self, val):
    if isMethod(val):
      if val.ret_type.get_lexeme() != "String":
        return (False, None)
    elif isVariable(val):
      if val.type.get_lexeme() != "String":
        return (False, None)

    if self.ref.get_lexeme() == "concat":
      return self.handle_concat(val)
    elif self.ref.get_lexeme() == "length":
      return self.handle_length(val)
    elif self.ref.get_lexeme() == "charAt":
      return self.handle_charAt(val)
    elif self.ref.get_lexeme() == "equals":
      return self.handle_equals(val)

    return (False, None)

  def handle_concat(self, val):
    if len(self.args) != 1:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "concat toma un unico parametro de tipo String")
    r = self.args[0].resolve()
    if isMethod(r) and r.ret_type.get_lexeme() != "String" or \
       isVariable(r) and r.type.get_lexeme() != "String":
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "concat toma un unico parametro de tipo String")

    self.code += "push String_concat\n"
    self.code += "call\n"
    ret = Token()
    ret._lexeme = "String"
    ret._type = IDENTIFIER
    return (True, mjMethod([], ret, self.ref, [], mjBlock(), None))

  def handle_length(self, val):
    if len(self.args) != 0:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "length se llama sin parametros")

    self.code += "push String_length\n"
    self.code += "call\n"
    ret = Token()
    ret._lexeme = "int"
    ret._type = INT_TYPE
    return (True, mjMethod([], ret, self.ref, [], mjBlock(), None))

  def handle_charAt(self, val):
    if len(self.args) != 1:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "charAt toma un unico parametro de tipo int")
    r = self.args[0].resolve()
    if isMethod(r) and r.ret_type.get_lexeme() != "int" or \
       isVariable(r) and r.type.get_lexeme() != "int":
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "charAt toma un unico parametro de tipo int")

    self.code += "push String_charAt\n"
    self.code += "call\n"
    ret = Token()
    ret._lexeme = "char"
    ret._type = CHAR_TYPE
    return (True, mjMethod([], ret, self.ref, [], mjBlock(), None))

  def handle_equals(self, val):
    if len(self.args) != 1:
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "equals toma un unico parametro de tipo String")
    r = self.args[0].resolve()
    if isMethod(r) and r.ret_type.get_lexeme() != "String" or \
       isVariable(r) and r.type.get_lexeme() != "String":
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "equals toma un unico parametro de tipo String")

    self.code += "push String_equals\n"
    self.code += "call\n"
    ret = Token()
    ret._lexeme = "boolean"
    ret._type = BOOLEAN_TYPE
    return (True, mjMethod([], ret, self.ref, [], mjBlock(), None))

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
                              "No se puede llamar a un constructor como un "
                              "parametro para otra funcion.")
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
                          "La llamada a un constructor debe realizarse con"
                          " una sentencia new o como una sentencia individual.")

    mjType.compatible(m.ret_type.get_lexeme(), othertype.get_lexeme(), self.ts,
                      self.ref.get_line(), self.ref.get_col())
    return True

  @memoized
  def check(self):
    m = self.resolve()
    code = ""

    if not m.ret_type is None:
      if m.ret_type.get_type() != VOID_TYPE:
        code += "rmem 1\n"
    for a in self.args:
      code += a.check()
    return code + self.get_rec_code()

class mjClassInstanceCreation(mjMethodInvocation):
  def __init__(self, prim, args):
    super(mjClassInstanceCreation, self).__init__(prim, args)
    self.type = mjPrimary.ClassInstCreat

  def compatibleWith(self, othertype):
    # othertype siempre es un tipo, este se llama para casos como
    # declaracion de variables, y en othertype esta el tipo de la decl
    return mjPrimary.compatibleWith(self, othertype)

  def inmediate_resolve(self):
    tmpts = self.ts
    found = False
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
      if self.ref.get_lexeme() == "String":
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "Un string no puede crearse de esta forma.")

      cl = tmpts.getType(self.ref.get_lexeme())
      if cl.ts.methodInvExists(self):
        methods = cl.ts.getMethod(self)
        m = self.get_THE_method(methods, self.ref.get_line(), self.ref.get_col())

        if m.isProtected():
          raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                              "%s es un constructor protegido."
                              % self.call_signature())

        ### CODE
        self.code += "rmem 1\n"
        self.code += "push %d ; long CIR %s\n" % (cl.long, cl.name.get_lexeme())
        self.code += "push simple_malloc\n"
        self.code += "call\n"
        self.code += "dup\n"
        self.code += "push %s ; vtable\n" % (cl.vtable)
        self.code += "storeref 0\n"
        self.code += "dup\n"
        self.code += "push %s ; preconstructor\n" % cl.ipreconstruct
        self.code += "call\n"
        self.code += "dup\n"
        self.code += "push %s ; constructor\n" % m.label
        self.code += "call\n"
        ### /CODE

        return m
      else:
        raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                            "No existe ningun constructor con el signature %s"
                            % self.call_signature())

  @memoized
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
      name._line = self.ref.get_line()
      name._col = self.ref.get_col()
      return mjVariable(t.name, name, ts=self.ts)
    else:
      # esto se levanta en la etapa sintactica, pero por las dudas...
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "No se pueden crear clases de tipos dereferenciados")

  @memoized
  def check(self):
    self.resolve()
    code = ""

    for a in self.args:
      code += a.check()
    return code + self.get_rec_code()

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
    self.left.pprint(tabs+1)
    self.expr.pprint(tabs+1)

  @memoized
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

    right_str = ""
    if isToken(right):
      right_str = typeToStr(literalToType(right.get_type()))
    else:
      if isMethod(right):
        right_str = right.ret_type.get_lexeme()
      else:
        right_str = right.type.get_lexeme()

    mjType.compatible(left.type.get_lexeme(), right_str,
                      self.ts, self.ref.get_line(), self.ref.get_col())

    ### CODE
    self.code += self.expr.check()
    self.code += "dup\n"

    left_code = self.left.check()

    if isClassVariable(left):
      self.code += "\n".join(left_code.split("\n")[:-2]) + "\n"
      self.code += "swap\n"
      self.code += "storeref %d ; assignment (class var) %s\n" % (left.offset, left.name.get_lexeme())
    else:
      self.code += "store %d ; assignment (local var) %s\n" % (left.offset, left.name.get_lexeme())
    ### /CODE
    return self.code

  @memoized
  def resolve(self):
    return self.expr.resolve()

class mjOp(mjPrimary):
  def __init__(self, symbol, operands):
    super(mjOp, self).__init__(symbol)
    self.symbol = symbol
    self.operands = operands
    self.ts = None
    self.label_cc_true = None
    self.label_cc_false = None
    self.is_string = False

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
      if isMethod(r):
        return (r.ret_type.get_type(), types[0])
      else:
        return (r.type.get_type(), types[0])

  @memoized
  def resolve(self):
    types = []
    r = None
    for o in self.operands:
      r = o.resolve()
      if isToken(r):
        types.append(typeToStr(literalToType(r.get_type())))
      else:
        if isMethod(r):
          types.append(r.ret_type.get_lexeme())
        else:
          types.append(r.type.get_lexeme())

    # tratamos a los chars como ints
    s = list(set([x if x != "char" else "int" for x in types]))
    diffs = len(s)
    if diffs != 1:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operacion entre tipos incompatibles.")

    if not s[0] in ["String", "int", "boolean", "char"]:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operacion con tipos no validos, solo pueden "
                          "ser int, boolean, char o String.")

    if s[0] == "String":
      self.is_string = True

    name = Token()
    name._lexeme = "@" + ("".join(random.choice(string.letters + string.digits) for i in xrange(10)))
    name._line = self.symbol.get_line()
    name._col = self.symbol.get_col()
    t = Token()
    (rt, name_type) = self._var_type(r, s)
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

  @memoized
  def check(self):
    code = ""

    for o in self.operands:
      if not self.label_cc_true is None:
        o.label_cc_true = self.label_cc_true
        o.label_cc_false = self.label_cc_false
      code += o.check()

      # si es el ultimo, no hay cc
      if o is self.operands[-1]:
        break

      if self.symbol.get_type() == CONDITIONAL_AND:
        if not self.label_cc_false is None:
          code += "bf %s ; && por cc\n" % self.label_cc_false
          code += "push 1 ; retorna el valor de verdad\n"
      elif self.symbol.get_type() == CONDITIONAL_OR:
        if not self.label_cc_true is None:
          code += "bt %s ; || por cc\n" % self.label_cc_true
          code += "push 0 ; retorna el valor de verdad\n"

    self.resolve()
    if self.is_string and self.symbol.get_type() == ADD:
      code += "swap\npush String_concat\ncall\n"
    else:
      code += "%s \n" % mne_ops[self.symbol.get_lexeme()]

    if self.is_string:
      code = "rmem 1\n" + code
    return code

class mjArithOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjArithOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if not (types[0] in ["int", "char"]):
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                         "No se puede realizar esta operacion sobre otro tipo "
                          "que no sea int o char.")
    return (INT_TYPE, "int")

class mjBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "boolean" in types or "int" in types or "char" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones "
                          "booleanas solo aceptan int, char o boolean.")

class mjStrictIntBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjStrictIntBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "int" in types or "char" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones "
                          "booleanas solo aceptan int o char.")

class mjStrictBoolOp(mjOp):
  def __init__(self, symbol, operands):
    super(mjStrictBoolOp, self).__init__(symbol, operands)

  def _var_type(self, r, types):
    if "boolean" in types:
      return (BOOLEAN_TYPE, "boolean")
    else:
      raise SemanticError(self.symbol.get_line(), self.symbol.get_col(),
                          "Operandos de tipo invalido, las operaciones "
                          "booleanas solo acepta boolean.")

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

class mjType(object):
  @staticmethod
  def compatible(left, right, ts, line, col):
    if left in ["int", "char", "boolean", "String"] or \
           right in ["int", "char", "boolean", "String"]:
      if left != right:
        raise SemanticError(line, col,
                            "Tipos incompatibles")
      return

    if left == "void" or right == "void":
      raise SemanticError(self.ref.get_line(), self.ref.get_col(),
                          "Tipos incompatibles.")


    # Aca sabemos que no son tipos primitivos
    left_type = ts.recFindType(left)
    right_type = ts.recFindType(right)

    if left_type is None:
      raise SemanticError(line, col,
                          "No existe el tipo %s" % left)

    if right_type is None:
      raise SemanticError(line, col,
                          "No existe el tipo %s" % right)

    if not right_type.inheritsFrom(left_type.name.get_lexeme()):
      raise SemanticError(line, col,
                          "Tipos incompatibles")

  @staticmethod
  def distance(left, right, ts):
    if left == right:
      return 0

    left_type = ts.recFindType(left)
    right_type = ts.recFindType(right)

    if not left_type.inheritsFrom(right_type) and \
           not right_type.inheritsFrom(left_type):
      # si no son tipos compatibles, la distancia es maxima
      return 999999999

    father = left_type
    son = right_type

    if left_type.inheritsFrom(right_type):
      father = right_type
      son = left_type

    dst = 0
    cur = son.ext_class
    while cur.name.get_lexeme() != father.name.get_lexeme():
      dst += 1
      cur = cur.ext_class

    return dst

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

mne_ops = {"+"  : "add",
           "-"  : "sub",
           "/"  : "div",
           "*"  : "mul",
           "%"  : "mod",
           "!"  : "not",
           "<"  : "lt",
           ">"  : "gt",
           "<=" : "le",
           ">=" : "ge",
           "==" : "eq",
           "!=" : "ne",
           "&&" : "and",
           "||" : "or",
           }

