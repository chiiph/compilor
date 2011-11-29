import copy
import random
import string

from memoize import memoized

from mjts import mjTS
from lexor import Token
from constants import IDENTIFIER, PUBLIC, STATIC, PROTECTED, VOID_TYPE, BOOLEAN_TYPE
from errors import SemanticError
from firsts import FIRST_primitive_type

from mjcheckers import mjCheckable
import mjprimary as mjp

def isVariable(obj):
  return isinstance(obj, mjVariable)

def isClassVariable(obj):
  return isinstance(obj, mjClassVariable)

def isClass(obj):
  return isinstance(obj, mjClass)

def isMethod(obj):
  return isinstance(obj, mjMethod)

def isReturn(obj):
  return isinstance(obj, mjReturn)

def isVariableDecl(obj):
  return isinstance(obj, mjVariableDecl)

def isBlock(obj):
  return isinstance(obj, mjBlock)

def isIf(obj):
  return isinstance(obj, mjIf)

def isWhile(obj):
  return isinstance(obj, mjWhile)

def isId(obj):
  return obj.type >= 0

class mjClass(mjCheckable):
  def __init__(self, name, ext_name, decls, ts, localts = None):
    super(mjClass, self).__init__()
    self.name = name
    self.ext_name = ext_name
    self.ext_class = None # no resuelto todavia
    self.decls = decls
    self.long = 0
    self.vtable = "VT_%s" % self.name.get_lexeme()
    self.cr = "CR_%s" % self.name.get_lexeme()
    self.preconstruct = "%s_spreconstr" % self.name.get_lexeme()
    self.ipreconstruct = "%s_ipreconstr" % self.name.get_lexeme()

    if not ts is None:
      (redef, other) = ts.classExists(self)
      if redef:
        raise SemanticError(other.name.get_line(), other.name.get_col(),
                            "Clase ya definida")

      ts.addClass(self)
    self.ts = localts
    if localts is None:
      self.ts = mjTS(ts)

    self.ts.set_owner(self)

    self.gen_default_construct()

    if self.ext_name is None and self.name.get_lexeme() != "Object":
      e = Token()
      e._lexeme = "Object"
      e._type = IDENTIFIER
      e._line = 0
      e._col = 0
      self.ext_name = e

  def pprint_ts(self, tabs=0):
    print "  "*tabs + "** Class::" + self.name.get_lexeme() + " **"
    self.ts.pprint(tabs)
    for d in self.decls:
      if isinstance(d, mjMethod):
        d.pprint_ts(tabs+1)

  def pprint(self, tabs=0):
    print "  "*tabs + "Class::" + self.name.get_lexeme()
    if not self.ext_name is None:
      print "  "*tabs + "Extends::" + self.ext_name.get_lexeme()
    for d in self.decls:
      d.pprint(tabs+1)

  def hasVarAtAll(self, v):
    if self.ts.varExists(v):
      return (True, self.ts.getVar(v))
    elif not self.ext_class is None:
      return self.ext_class.hasVarAtAll(v)
    else:
      return (False, None)

  def hasMethodInvAtAll(self, v):
    if self.ts.methodInvExists(v):
      return (True, self.ts.getMethod(v))
    elif not self.ext_class is None:
      return self.ext_class.hasMethodInvAtAll(v)
    else:
      return (False, None)

  def hasMethodAtAll(self, v):
    if self.ts.methodExists(v):
      return (True, self.ts.getExactMethod(v))
    elif not self.ext_class is None:
      return self.ext_class.hasMethodAtAll(v)
    else:
      return (False, None)

  def inheritsFrom(self, cl):
    if self.name.get_lexeme() == cl:
      return True

    if self.ext_class is None:
      return False

    if self.ext_class.name.get_lexeme() == cl:
      return True

    return self.ext_class.inheritsFrom(cl)

  def pre_check(self):
    for d in self.decls:
      d.pre_check()

  def solve_extends(self):
    if not self.ext_name is None:
      (valid, ref) = self.ts.parent().validExtend(self.ext_name)
      # copiamos para mantener los offsets de esta clase en particular
      self.ext_class = ref
      if not valid:
        raise SemanticError(self.ext_name.get_line(), self.ext_name.get_col(),
                            "No existe la clase padre")

  @memoized
  def sort(self):
    static_vars = []
    vars = []
    static_methods = []
    methods = []

    for v in self.ts._sections["variables"].values():
      if v.isStatic():
        static_vars.append(v)
      else:
        vars.append(v)

    for m in self.decls:
      if not isMethod(m):
        continue
      if m.is_constructor():
        m.label = "%s" % (m.get_signature().replace("(", "$").replace(")", "$").replace(",","_"))
        continue
      if m.isStatic():
        static_methods.append(m)
      else:
        methods.append(m)

    return static_vars, vars, static_methods, methods

  def set_offsets(self, static_init = 0, vars_init = 1, methods_init = 0):
    # Clasificamos las declaraciones
    static_vars, vars, static_methods, methods = self.sort()

    for m in methods:
      m.label = "%s_%s" % (self.name.get_lexeme(),
                           m.get_signature().replace("(", "$").replace(")", "$").replace(",","_"))

    for m in static_methods:
      m.label = "%s_%s" % (self.name.get_lexeme(),
                           m.get_signature().replace("(", "$").replace(")", "$").replace(",","_"))

    if self.ext_name is None:
      static_vars_offset = static_init
      vars_offset = vars_init # empieza en 1 porque en 0 estara la vtable
      methods_offset = methods_init

      # Seteamos los offsets
      for v in static_vars:
        v.offset = static_vars_offset
        static_vars_offset += 1

      for v in vars:
        v.offset = vars_offset
        vars_offset += 1

      for m in methods:
        m.offset = methods_offset
        methods_offset += 1
    else:
      if self.ext_class is None:
        raise Exception("Herencia no resuelta!")

      static_vars_offset, vars_offset, methods_offset = self.ext_class.set_offsets()

      # los offsets de variables son iguales, pero "arriba" de quienes heredan
      for v in static_vars:
        v.offset = static_vars_offset
        static_vars_offset += 1

      for v in vars:
        v.offset = vars_offset
        vars_offset += 1

      for m in methods:
        redef = self.get_redef(m)
        if redef is None:
          m.offset = methods_offset
          methods_offset += 1
        else:
          m.offset = redef.offset

    return static_vars_offset, vars_offset, methods_offset

  def get_redef(self, m):
    if self.ext_class is None:
      return None

    redef = self.ext_class.ts.getExactMethod(m)
    if redef is None:
      return self.ext_class.get_redef(m)
    return redef

  def get_all(self):
    static_vars, vars, static_methods, methods = self.sort()
    if self.ext_class is None:
      return static_vars, vars, static_methods, methods

    all_static_vars, all_vars, all_static_methods, all_methods = self.ext_class.get_all()

    sorted_methods = []
    for m in all_methods:
      sorted_methods.append(m)
      for m_son in methods:
        if m_son.offset == m.offset:
          # solo deberia haber uno
          # si hay redefinicion, se sobreescribe en la lista
          sorted_methods[len(sorted_methods)-1] = m_son

    methods = sorted(methods, key = lambda m: m.offset)

    return (static_vars,
            all_vars+vars,
            all_static_methods+static_methods,
            sorted_methods+methods)

  @memoized
  def check(self):
    code = ""

    self.set_offsets()
    all_static_vars, all_vars, all_static_methods, all_methods = self.get_all()

    vt_labels = []
    for m in all_methods:
      if m.is_constructor():
        continue
      vt_labels.append(m.label)

    if len(vt_labels) == 0:
      vt_labels.append("0")

    code += ".data\n"
    # Creamos el CR
    if len(all_static_vars) == 0:
      code += "CR_%s: dw 0\n" % (self.name.get_lexeme(),)
    else:
      code += "CR_%s: dw %d DUP(0)\n" % (self.name.get_lexeme(),
                                         len(all_static_vars))

    # Creamos el VT
    self.vtable = "VT_%s" % self.name.get_lexeme()
    code += "%s: dw %s\n" % (self.vtable,
                             ",".join(vt_labels))

    code += ".code\n"
    # Creamos el spreconstr
    code += "%s: loadfp\n" % self.preconstruct
    code += "loadsp\n"
    code += "storefp\n"

    if not self.ext_class is None:
      code += "push %s\n" % self.ext_class.preconstruct
      code += "call\n"

    for sv in all_static_vars:
      init_code = ""
      if not sv.val is None:
        init_code = sv.val.check()
      if len(init_code) != 0:
        code += init_code
        code += "dup\n"
        code += "push CR_%s\n" % self.name.get_lexeme()
        code += "swap\n"
        code += "storeref %d ; offset a %s\n" % (sv.offset, sv.name.get_lexeme())
        code += "pop\n"

    code += "storefp\n"
    code += "ret 0\n"

    # Creamos el ipreconstr
    code += "%s: loadfp\n" % self.ipreconstruct
    code += "loadsp\n"
    code += "storefp\n"

    self.long = len(all_vars)+1 # +1: vtable

    if not self.ext_class is None:
      code += "load 3 ; this\n"
      code += "push %s\n" % self.ext_class.ipreconstruct
      code += "call\n"

    for v in self.ts._sections["variables"].values():
      if v.isStatic():
        continue
      init_code = ""
      if not v.val is None:
        init_code = v.val.check()
      if len(init_code) != 0:
        code += init_code
        code += "dup\n"
        code += "load 3 ; this\n"
        code += "swap\n"
        code += "storeref %d ; offset a %s\n" % (v.offset,
                                                 v.name.get_lexeme())
        code += "pop\n"

    code += "storefp\n"
    code += "ret 1\n"

    for d in self.decls:
      if not d is None:
        code += d.check()

    return code

  def gen_default_construct(self):
    for d in self.decls:
      if isMethod(d) and d.is_constructor():
        return

    p = Token()
    p._lexeme = "public"
    p._type = PUBLIC
    modifs = [p]

    m = mjMethod(modifs, None, self.name, [], mjBlock(), self.ts)
    self.decls.append(m)

class mjReturn(mjCheckable):
  def __init__(self, ret = None, expr = None, method = None):
    super(mjReturn, self).__init__()
    self.expr = expr
    self.method = method
    self.ts = None
    self.ret = ret

  def pprint(self, tabs=0):
    if not self.expr is None:
      print "  "*tabs + "return ..."
      self.expr.pprint(tabs+1)
    else:
      print "  "*tabs + "return;"

  def set_ts(self, ts):
    self.ts = ts
    if not self.expr is None:
      self.expr.set_ts(ts)

  @memoized
  def check(self):
    if self.method.is_constructor():
      if not self.expr is None:
        raise SemanticError(self.ret.get_line(), self.ret.get_col(),
                            "Los return en constructores no deben retornar valores")
      else:
        return ""

    if self.expr is None:
      if self.method.ret_type.get_type() != VOID_TYPE:
        raise SemanticError(self.ret.get_line(), self.ret.get_col(),
                            "La sentencia return debe contener una expresion de tipo %s"
                            % self.method.ret_type.get_lexeme())
    else:
      t = self.expr.resolve()
      #raise Exception("Checkear compatibilidad de herencia tambien!")
      if mjp.isToken(t):
        rt = mjp.literalToType(t.get_type())
        if rt != self.method.ret_type.get_type():
          raise SemanticError(self.ret.get_line(), self.ret.get_col(),
                              "Se esta retornando %s en un metodo de tipo %s"
                              % (mjp.typeToStr(rt), self.method.ret_type.get_lexeme()))
      else:
        if t.type.get_lexeme() != self.method.ret_type.get_lexeme():
          raise SemanticError(self.ret.get_line(), self.ret.get_col(),
                              "Se esta retornando %s en un metodo de tipo %s"
                              % (t.type.get_lexeme(), self.method.ret_type.get_lexeme()))

      offset = 3
      if self.method.isStatic():
        offset = 2 # no hay this
      return self.expr.check()+"store %d ; offset a ret_val\n" % (offset + len(self.method.params) + 1)
    return ""

class mjWhile(mjCheckable):
  def __init__(self, expr, statement):
    super(mjWhile, self).__init__()
    self.expr = expr
    self.statement = statement

  def set_ts(self, ts):
    self.expr.set_ts(ts)
    self.statement.set_ts(ts)

  def pprint(self, tabs=0):
    print "  "*tabs + "while"
    print "  "*tabs + "((("
    self.expr.pprint(tabs+1)
    print "  "*tabs + ")))"
    print "  "*tabs + "{{{"
    if not self.statement is None:
      self.statement.pprint(tabs+1)
    print "  "*tabs + "}}}"

  @memoized
  def check(self):
    e = self.expr.resolve()
    if mjp.isToken(e):
      if mjp.literalToType(e.get_type()) != BOOLEAN_TYPE:
        raise SemanticError(e.get_line(), e.get_col(),
                            "La expresion debe ser de tipo boolean")
    elif isVariable(e):
      if e.type.get_type() != BOOLEAN_TYPE:
        raise SemanticError(e.name.get_line(), e.name.get_col(),
                            "La expresion debe ser de tipo boolean")
    elif isMethod(e):
      if e.is_constructr() or e.ret_type.get_type() != BOOLEAN_TYPE:
        raise SemanticError(self.expr.ref.get_line(), self.expr.ref.get_col(),
                             "La expresion debe ser de tipo boolean")
    else:
      raise Exception()

    rand = "".join(random.choice(string.letters + string.digits) for i in xrange(10))
    label_true = "while_true_%s" % rand
    label_false = "while_false_%s" % rand

    code = "%s: nop\n" % label_true
    code += self.expr.check()
    code += "bf %s\n" % label_false
    code += self.statement.check()
    code += "jump %s\n" % label_true
    code += "%s: nop\n" % label_false

    return code

class mjIf(mjCheckable):
  def __init__(self, expr, stat, elsestat=None):
    super(mjIf, self).__init__()
    self.expr = expr
    self.stat = stat
    self.elsestat = elsestat

  def set_ts(self, ts):
    self.stat.set_ts(ts)
    if not self.elsestat is None:
      self.elsestat.set_ts(ts)

  def pprint(self, tabs=0):
    print "  "*tabs + "if"
    print "  "*tabs + "((("
    self.expr.pprint(tabs+1)
    print "  "*tabs + ")))"
    print "  "*tabs + "{{{"
    self.stat.pprint(tabs+1)
    print "  "*tabs + "}}}"
    if not self.elsestat is None:
      print "  "*tabs + "else"
      print "  "*tabs + "{{{"
      self.elsestat.pprint(tabs+1)
      print "  "*tabs + "}}}"

  @memoized
  def check(self):
    e = self.expr.resolve()
    if mjp.isToken(e):
      if mjp.literalToType(e.get_type()) != BOOLEAN_TYPE:
        raise SemanticError(e.get_line(), e.get_col(),
                            "La expresion debe ser de tipo boolean")
    elif isVariable(e):
      if e.type.get_type() != BOOLEAN_TYPE:
        raise SemanticError(e.name.get_line(), e.name.get_col(),
                            "La expresion debe ser de tipo boolean")
    elif isMethod(e):
      if e.is_constructor() or e.ret_type.get_type() != BOOLEAN_TYPE:
        raise SemanticError(self.expr.ref.get_line(), self.expr.ref.get_col(),
                            "La expresion debe ser de tipo boolean")
    else:
      raise Exception()

    rand = "".join(random.choice(string.letters + string.digits) for i in xrange(10))
    label_true = "if_true_%s" % rand
    label_false = "if_false_%s" % rand
    label_end = "else_false_%s" % rand

    self.expr.label_cc_true = label_true
    self.expr.label_cc_false = label_false
    code = self.expr.check()
    code += "bf %s\n" % label_false
    code += "%s: nop\n" % label_true
    code += self.stat.check()
    code += "jump %s\n" % label_end
    code += "%s: nop\n" %label_false

    if not self.elsestat is None:
      code += self.elsestat.check()

    code += "%s: nop\n" % label_end

    return code

class mjVariableDecl(mjCheckable):
  def __init__(self, ref, args):
    super(mjVariableDecl, self).__init__()
    self.ref = ref
    self.args = args
    self.ts = None

  def pprint(self, tabs=0):
    print "  "*tabs + "Decl::" + self.ref.get_lexeme()
    for (v, e) in self.args:
      if not v is None:
        print "  "*(tabs+1) + v.get_lexeme()
      if not e is None:
        e.pprint(tabs+1)

  def set_ts(self, ts):
    self.ts = ts
    for (v, e) in self.args:
      if not e is None:
        e.set_ts(ts)

  @memoized
  def check(self):
    code = "rmem %d\n" % len(self.args)
    for v, e in self.args:
      if not e is None:
        code += e.check()
        if not e.compatibleWith(self.ref):
          raise SemanticError(v.get_line(), v.get_col(),
                              "Inicializacion de tipo incompatible")
      var = mjVariable(self.ref, v, e, self.ts)
      if not self.ts.addVar(var):
        raise SemanticError(v.get_line(), v.get_col(),
                            "Variable redefinida")
      var.offset = self.offset
      self.offset -= 1
      if not e is None:
        code += "dup\n"
        code += "store %d ; offset a %s \n" % (var.offset, var.name.get_lexeme())
        code += "pop\n"

    return code

class mjBlock(mjCheckable):
  def __init__(self, stats = [], ts=None):
    super(mjBlock, self).__init__()
    self.stats = stats
    self.ts = ts
    self.code = ""

  def set_ts(self, ts):
    self.ts = ts
    for stat in self.stats:
      if not stat is None:
        if isBlock(stat):
          bts = mjTS(ts)
          stat.set_ts(bts)
        elif isIf(stat):
          stat.expr.set_ts(ts)
          if not stat.stat is None:
            bts = mjTS(ts)
            stat.stat.set_ts(bts)
          if not stat.elsestat is None:
            bts = mjTS(ts)
            stat.elsestat.set_ts(bts)
        elif isWhile(stat):
          stat.expr.set_ts(ts)
          if not stat.statement is None:
            bts = mjTS(ts)
            stat.statement.set_ts(bts)
        else:
          stat.set_ts(ts)

  def pprint(self, tabs=0):
    print "  "*tabs + "{{{"
    for s in self.stats:
      if s is None:
        continue
      s.pprint(tabs+1)
    print "  "*tabs + "}}}"

  def pprint_ts(self, tabs=0):
    print "  "*tabs + "** Block **"
    self.ts.pprint(tabs)
    for s in self.stats:
      if not s is None:
        if isBlock(s):
          s.pprint_ts(tabs+1)
        elif isIf(s):
          if not s.stat is None:
            s.stat.pprint_ts(tabs+1)
          if not s.elsestat is None:
            s.elsestat.pprint_ts(tabs+1)
        elif isWhile(s):
          if not s.statement is None:
            s.statement.pprint_ts(tabs+1)

  def has_non_accesible_code(self):
    for i in range(0, len(self.stats)):
      stat = self.stats[i]
      if isBlock(stat):
        if stat.has_non_accesible_code():
          return True
      elif isIf(stat):
        if not stat.stat is None:
          if isBlock(stat.stat):
            if stat.stat.has_non_accesible_code():
              return True
        if not stat.elsestat is None:
          if isBlock(stat.elsestat):
            if stat.elsestat.has_non_accesible_code():
              return True
      elif isWhile(stat):
        if not stat.statement is None:
          if isBlock(stat.statement):
            if stat.statement.has_non_accesible_code():
              return True
      elif isReturn(self.stats[i]) and \
         i < (len(self.stats) - 1):
        return True
    return False

  @memoized
  def check(self):
    self.code = ""

    for s in self.stats:
      if not s is None:
        if isVariableDecl(s) or isBlock(s):
          s.offset = self.offset
          self.code += s.check()
          self.offset = s.offset
        else:
          self.code += s.check()
          if mjp.isAssignment(s):
            self.code += "pop\n"
          if mjp.isClassInstanceCreation(s) or \
             (mjp.isMethodInv(s) and s.resolve().ret_type and s.resolve().ret_type.get_type() != VOID_TYPE):
            self.code += "fmem 1\n"

    if len(self.ts._sections["variables"]) > 0:
      vars_freed =  ",".join(self.ts._sections["variables"])
      self.code += "fmem %d ; liberando %s\n" % (len(self.ts._sections["variables"]), vars_freed)
    return self.code

  def set_owning_method(self, m):
    for stat in self.stats:
      if not stat is None:
        if isBlock(stat):
          stat.set_owning_method(m)
        elif isIf(stat):
          if not stat.stat is None:
            if isBlock(stat.stat):
              stat.stat.set_owning_method(m)
            elif isReturn(stat):
              stat.method = m
          if not stat.elsestat is None:
            if isBlock(stat.elsestat):
              stat.elsestat.set_owning_method(m)
            elif isReturn(stat):
              stat.method = m
        elif isWhile(stat):
          if not stat.statement is None:
            if isBlock(stat.statement):
              stat.statement.set_owning_method(m)
            elif isReturn(stat):
              stat.method = m
        elif isReturn(stat):
          stat.method = m

  def has_reachable_ret(self):
    # hay return alcanzable si
    for s in self.stats:
      # 1: hay un return en el bloque
      if isReturn(s):
        return True

    # hay que ciclar por todas las statements en cada caso
    for s in self.stats:
      # 2: si hay un block, tiene un reachable return
      if isBlock(s):
        return s.has_reachable_ret()

    for s in self.stats:
      # 3: si hay un if
      # si llegamos aca, significa que no hay ningun return antes o despues
      # de este if, entonces,
      if isIf(s):
        # si tiene else, tiene que tener reachable rets en ambos statements
        has_ret_then = (isBlock(s.stat) and s.stat.has_reachable_ret()) or isReturn(s.stat)
        has_ret_else = False
        if not s.elsestat is None:
          has_ret_else = (isBlock(s.elsestat) and s.elsestat.has_reachable_ret()) or isReturn(s.elsestat)

        return has_ret_then and has_ret_else

    # por default...
    return False

class mjVariable(object):
  def __init__(self, typ, name, val=None, ts=None):
    super(mjVariable, self).__init__()

    self.type = typ
    self.name = name
    self.val = val
    self.ts = ts
    self.offset = 0

  def pprint(self, tabs=0):
    print "  "*tabs + self.type.get_lexeme() + " " + self.name.get_lexeme()
    if not self.val is None:
      print "  "*tabs
      self.val.pprint(tabs+1)

class mjMethod(mjCheckable):
  def __init__(self, modifs, ret_type, name, params, body, ts, localts=None):
    super(mjMethod, self).__init__()
    self.modifs = modifs
    self.ret_type = ret_type
    self.name = name
    self.params = params
    self.processed_params = []
    self.body = body

    # hack
    self._modifiable = mjModifiable()
    self._modifiable.modifs = self.modifs
    self.isStatic = self._modifiable.isStatic
    self.isPublic = self._modifiable.isPublic
    self.isProtected = self._modifiable.isProtected

    self.ts = localts
    if localts is None:
      self.ts = mjTS(ts)

    self.ts.set_owner(self)

    if not ts is None:
      if not ts.addMethod(self):
        raise SemanticError(self.name.get_line(), self.name.get_col(),
                            "Redefinicion de metodo.")

    param_offset = 3
    if not self.isStatic():
      param_offset = 4

    param_offset = len(self.params) + param_offset

    for (t, v) in self.params:
      param_offset -= 1
      var = mjVariable(t, v, ts=self.ts)
      var.offset = param_offset
      self.processed_params.append(var)
      if not self.ts.addVar(var):
        raise SemanticError(v.get_line(), v.get_col(),
                            "%s ya esta definido como parametro"
                            % v.get_lexeme())

    self.create_block_ts()
    self.body.set_owning_method(self)

  def check_type(self, t):
    if t.get_type() in FIRST_primitive_type:
      return
    if t.get_type() == VOID_TYPE:
      return
    if not self.ts.parent().parent().typeExists(t.get_lexeme()):
      raise SemanticError(t.get_line(),
                          t.get_col(),
                          "No existe ninguna clase llamada %s"
                          % t.get_lexeme())

  def check_modifs(self):
    if len(self.modifs) == 1:
      if self.modifs[0].get_type() == STATIC:
        raise SemanticError(self.modifs[0].get_line(),
                            self.modifs[0].get_col(),
                            "Las metodos no pueden ser solo static,"
                            "deben ser o public static o protected static.")
    elif len(self.modifs) == 2:
      if not (self.modifs[0].get_type() in [STATIC, PUBLIC] and
              self.modifs[1].get_type() in [STATIC, PUBLIC] and
              self.modifs[0].get_type() != self.modifs[1].get_type()) \
      and not (self.modifs[0].get_type() in [STATIC, PROTECTED] and
              self.modifs[1].get_type() in [STATIC, PROTECTED] and
              self.modifs[0].get_type() != self.modifs[1].get_type()):
        raise SemanticError(self.modifs[1].get_line(),
                            self.modifs[1].get_col(),
                            "Combinacion invalida de modificadores, las opciones son:\n"
                            "\tpublic static, static public, o\n"
                            "\tprotected static, static protected.")
    else:
      raise SemanticError(self.modifs[1].get_line(),
                          self.modifs[1].get_col(),
                          "Combinacion invalida de modificadores, las opciones son:\n"
                          "\tpublic static, static public, o\n"
                          "\tprotected static, static protected.")

    if self.is_constructor():
      if self.isStatic():
        raise SemanticError(self.name.get_line(),
                            self.name.get_col(),
                            "Los constructores no pueden ser static.")

  def get_signature(self):
    param_str = []
    for v, t in self.params:
      param_str.append(v.get_lexeme())

    return self.name.get_lexeme()+"("+(",".join(param_str))+")"

  def create_block_ts(self, stat = None, last_ts = None):
    """ Crea un ts para cada block con parent en el anterior """
    if last_ts is None:
      last_ts = self.ts
    if stat is None:
      stat = self.body
    if isBlock(stat):
      ts = mjTS(last_ts)
      stat.set_ts(ts)

  def pprint_ts(self, tabs=0):
    print "  "*tabs + "** Method::" + self.name.get_lexeme() + " **"
    self.ts.pprint(tabs)
    self.body.pprint_ts(tabs+1)

  def pprint(self, tabs=0):
    if not self.is_constructor():
      print "  "*tabs + "Method::" + self.name.get_lexeme() + " : " + self.ret_type.get_lexeme()
    else:
      print "  "*tabs + "Constructor::" + self.name.get_lexeme()
    self.body.pprint(tabs+1)

  def is_constructor(self):
    return self.ret_type is None

  @memoized
  def check(self):
    for (t, v) in self.params:
      self.check_type(t)

    if not self.ret_type is None:
      self.check_type(self.ret_type)

    self.check_modifs()

    cl = self.ts.parent().owner()
    if not self.is_constructor():
      if cl.name.get_lexeme() == self.name.get_lexeme():
        raise SemanticError(self.name.get_line(), self.name.get_col(),
                            "No se puede definir un metodo con el mismo nombre que la clase.")
    else:
      if cl.name.get_lexeme() != self.name.get_lexeme():
        raise SemanticError(self.name.get_line(), self.name.get_col(),
                            "Los constructores de clase deben llamarse igual que su clase.")

    if not cl.ext_class is None:
      # nos fijamos si es una redefinicion de metodo
      (has, method) = cl.ext_class.hasMethodAtAll(self)
      if has:
        # si lo es, no tiene que ser uno static y el otro no
        if method.isStatic() != self.isStatic():
          raise SemanticError(self.name.get_line(), self.name.get_col(),
                              "Redefinicion de metodo que cambia la visibilidad static del que redefine.")

    if not self.is_constructor() and self.ret_type.get_type() != VOID_TYPE:
      if not self.body.has_reachable_ret():
        raise SemanticError(self.name.get_line(), self.name.get_col(),
                            "El metodo puede no retornar el tipo especificado.")

    if self.body.has_non_accesible_code():
      raise SemanticError(self.name.get_line(), self.name.get_col(),
                          "El metodo contiene codigo inaccesible.")

    code = "%s: loadfp\n" % self.label
    code += "loadsp\n"
    code += "storefp\n"
    code += self.body.check()

    release = 0
    if not self.isStatic():
      release = 1 # this

    release += len(self.params)

    code += "storefp\n"
    code += "ret %d\n" % release

    return code

class mjClassVariableDecl(mjCheckable):
  def __init__(self, modifs, t, list_ids, ts):
    super(mjClassVariableDecl, self).__init__()
    self.modifs = modifs
    self.type = t
    self.list_ids = list_ids
    self.ts = ts

    for v, i in self.list_ids:
      var = mjClassVariable(self.type, v, i, self.modifs, self.ts)
      if not i is None:
        i.set_ts(ts)
        i.set_var(var)
      if not self.ts.addVar(var):
        raise SemanticError(v.get_line(), v.get_col(),
                            "Variable redefinida")

  def pprint(self, tabs=0):
    ms = ""
    for m in self.modifs:
      ms += m.get_lexeme()
      ms += " "
    print "  "*tabs + ms + " " + self.type.get_lexeme()
    for (name, init) in self.list_ids:
      if init is None:
        print "   "*tabs + name.get_lexeme()
      else:
        print "   "*tabs + name.get_lexeme() + " = "
        init.pprint(tabs+1)

  @memoized
  def check(self):
    self.check_type()
    self.check_modifs()
    for v, i in self.list_ids:
      if not i is None:
        i.check()
        if not i.compatibleWith(self.type):
          raise SemanticError(v.get_line(), v.get_col(),
                              "Inicializacion de tipo incompatible")
    return ""

  def check_type(self):
    if self.type.get_type() in FIRST_primitive_type:
      return
    if not self.ts.parent().typeExists(self.type.get_lexeme()):
      raise SemanticError(self.type.get_line(),
                          self.type.get_col(),
                          "No existe ninguna clase llamada %s"
                          % self.type.get_lexeme())

  def check_modifs(self):
    if len(self.modifs) == 1:
      if self.modifs[0].get_type() == STATIC:
        raise SemanticError(self.modifs[0].get_line(),
                            self.modifs[0].get_col(),
                            "Las variables de instancia no pueden ser solo static,"
                            "deben ser o public static o protected static.")
    elif len(self.modifs) == 2:
      if not (self.modifs[0].get_type() in [STATIC, PUBLIC] and
              self.modifs[1].get_type() in [STATIC, PUBLIC] and
              self.modifs[0].get_type() != self.modifs[1].get_type()) \
      and not (self.modifs[0].get_type() in [STATIC, PROTECTED] and
              self.modifs[1].get_type() in [STATIC, PROTECTED] and
              self.modifs[0].get_type() != self.modifs[1].get_type()):
        raise SemanticError(self.modifs[1].get_line(),
                            self.modifs[1].get_col(),
                            "Combinacion invalida de modificadores, las opciones son:\n"
                            "\tpublic static, static public, o\n"
                            "\tprotected static, static protected.")
    else:
      raise SemanticError(self.modifs[1].get_line(),
                          self.modifs[1].get_col(),
                          "Combinacion invalida de modificadores, las opciones son:\n"
                          "\tpublic static, static public, o\n"
                          "\tprotected static, static protected.")

class mjClassVariable(mjVariable):
  def __init__(self, ty, val, init, modifs, ts=None):
    super(mjClassVariable, self).__init__(ty, val, init, ts)
    self.modifs = modifs

    # hack
    self._modifiable = mjModifiable()
    self._modifiable.modifs = self.modifs
    self.isStatic = self._modifiable.isStatic
    self.isPublic = self._modifiable.isPublic
    self.isProtected = self._modifiable.isProtected

    self.modifs = modifs

class mjModifiable(object):
  def __init__(self):
    super(mjModifiable, self).__init__()

  def isStatic(self):
    for m in self.modifs:
      if m.get_type() == STATIC:
        return True
    return False

  def isProtected(self):
    for m in self.modifs:
      if m.get_type() == PROTECTED:
        return True
    return False

  def isPublic(self):
    for m in self.modifs:
      if m.get_type() == PUBLIC:
        return True
    return False
