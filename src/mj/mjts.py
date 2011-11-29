from errors import SemanticError
from lexor import Token
from constants import IDENTIFIER
from mj.string_predef import string_code
import mjclass as mjc

class mjTS(object):
  def __init__(self, parent=None, owner=None):
    # Pueden ser classes, variables, methods
    self._sections = {}
    # Si parent es None, entonces es la TS global
    self._parent = parent
    # *cosa* que tiene como ts a self
    self._owner = owner

    # Usada en la global
    self._sections["classes"] = {}

    # Usadas en el resto
    self._sections["variables"] = {}
    self._sections["methods"] = {}

  def owner(self):
    return self._owner

  def set_owner(self, o):
    self._owner = o

  def parent(self):
    return self._parent

  def has(self, section, value):
    if section in self._sections.keys():
      return (True, self._sections[section][value])

    return (False, None)

  def addClass(self, c):
    self._sections["classes"][c.name.get_lexeme()] = c

  def addMethod(self, m):
    if self.methodExists(m):
      return False
    if m.name.get_lexeme() in self._sections["methods"].keys():
      self._sections["methods"][m.name.get_lexeme()].append(m)
    else:
      self._sections["methods"][m.name.get_lexeme()] = [m]
    return True

  def typeExists(self, t):
    # built-in
    if t == "String":
      return True

    for c in self._sections["classes"].keys():
      if c == t:
        return True

    return False

  def classExists(self, cl):
    redef = False
    other = None
    for c in self._sections["classes"].keys():
      if c == cl.name.get_lexeme():
        redef = (cl != self._sections["classes"][c])
        if redef:
          other = self._sections["classes"][c]
          break
    return (redef, other)

  def validExtend(self, ext_name):
    if ext_name.get_lexeme() in self._sections["classes"].keys():
      return (True, self._sections["classes"][ext_name.get_lexeme()])
    return (False, None)

  def addVar(self, v):
    if self.varExists(v.name.get_lexeme()):
      return False
    self._sections["variables"][v.name.get_lexeme()] = v
    return True

  def varExists(self, v):
    return v in self._sections["variables"].keys()

  def methodInvExists(self, m):
    if not (m.ref.get_lexeme() in self._sections["methods"].keys()):
      return False

    # un metodo existe, si hay un metodo declarado con los mismos parametros
    # un parametro es el mismo que otro si tiene el mismo tipo
    for method in self._sections["methods"][m.ref.get_lexeme()]:
      if self._compParams(m.args, method.params):
        return True
    return False

  def _compParams(self, params1, params2):
    if len(params1) != len(params2):
      return False
    i = 0
    for i in range(0, len(params1)):
      try:
        if not params1[i].compatibleWith(params2[i][0]):
          return False
      except SemanticError, e:
        return False
    return True

  def methodExists(self, m):
    if not (m.name.get_lexeme() in self._sections["methods"].keys()):
      return False

    # un metodo existe, si hay un metodo declarado con los mismos parametros
    # un parametro es el mismo que otro si tiene el mismo tipo
    for method in self._sections["methods"][m.name.get_lexeme()]:
      if self._sameParams(m.params, method.params):
        return True
    return False

  def getExactMethod(self, m):
    if not (m.name.get_lexeme() in self._sections["methods"].keys()):
      return None

    for method in self._sections["methods"][m.name.get_lexeme()]:
      if self._sameParams(m.params, method.params):
        return method
    return None

  def _sameParams(self, params1, params2):
    if len(params1) != len(params2):
      return False
    i = 0
    for i in range(0, len(params1)):
      if params1[i][0].get_lexeme() != params2[i][0].get_lexeme():
        return False
    return True

  def getVar(self, v):
    return self._sections["variables"][v]

  def getType(self, v):
    if not v in self._sections["classes"]:
      raise SemanticError(0,0,
                          "No existe ningun tipo llamado %s" % v)
    return self._sections["classes"][v]

  def getMethod(self, m):
    return self._sections["methods"][m.ref.get_lexeme()]

  def recFindType(self, t):
    if self.typeExists(t):
      return self.getType(t)
    else:
      if not self._parent is None:
        return self._parent.recFindType(t)
    return None

  def pprint(self, tabs=0):
    print "  "*tabs + "-"*30
    for k in self._sections.keys():
      print "  "*tabs + k + ":"
      for j in self._sections[k].keys():
        print "  "*tabs + " " + j
    print "  "*tabs + "-"*30

  def create_predefs(self):
    o = Token()
    o._lexeme = "Object"
    o._type = IDENTIFIER
    o._line = 0
    o._col = 0

    cl = mjc.mjClass(o, None, [], self)

  def check(self):
    self.create_predefs()

    for t in self._sections["classes"]:
      self._sections["classes"][t].solve_extends()

    code = ".code\n"
    code += "push simple_heap_init\n"
    code += "call\n"

    for t in self._sections["classes"]:
      if t == "Object":
        continue
      code += "push %s\n" % self._sections["classes"][t].preconstruct
      code += "call\n"

    rest_code = ""

    ### PREDEF
    rest_code += "simple_heap_init: ret 0\n"
    rest_code += "simple_malloc: loadfp\n"
    rest_code += "loadsp\n"
    rest_code += "storefp\n"
    rest_code += "loadhl\n"
    rest_code += "dup\n"
    rest_code += "push 1\n"
    rest_code += "add\n"
    rest_code += "store 4\n"
    rest_code += "load 3\n"
    rest_code += "add\n"
    rest_code += "storehl\n"
    rest_code += "storefp\n"
    rest_code += "ret 1\n"
    rest_code += string_code

    for t in self._sections["classes"]:
      rest_code += self._sections["classes"][t].check()
    main_label = self.hasMain()
    code += "push %s\n" % main_label
    code += "call\n"
    code += "halt\n"
    code += rest_code

    return code

  def hasMain(self):
    mains = []
    for clstr in self._sections["classes"]:
      cl = self.getType(clstr)
      if "main" in cl.ts._sections["methods"].keys():
        ms = cl.ts._sections["methods"]["main"]
        for m in ms:
          if len(m.params) == 0 and \
             m.isStatic() and \
             m.isPublic():
            mains.append(m)

    if len(mains) == 0:
      raise SemanticError(0,0,
                          "No existe ningun metodo static void main()")

    if len(mains) > 1:
      raise SemanticError(0,0,
                          "Existen mas de un metodo static void main()")

    return mains[0].label

