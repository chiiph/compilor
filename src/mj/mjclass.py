from mjts import mjTS
from lexor import Token
from constants import IDENTIFIER
from errors import SemanticError

from mjcheckers import mjCheckable
from mjts import mjTS

def isBlock(obj):
  return isinstance(obj, mjBlock)

def isIf(obj):
  return isinstance(obj, mjIf)

def isWhile(obj):
  return isinstance(obj, mjWhile)

def isMethodInv(obj):
  return isinstance(obj, mjMethodInvocation)

def isId(obj):
  return (isinstance(obj.ref, Token) and obj.ref.get_type() == IDENTIFIER)

class mjClass(mjCheckable):
  def __init__(self, name, ext_name, decls, ts, localts = None):
    self.name = name
    self.ext_name = ext_name
    self.ext_class = None # no resuelto todavia
    self.decls = decls

    ts.addClass(self)
    self.ts = localts
    if localts is None:
      self.ts = mjTS(ts)

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

  def gen_code(self):
    return ""

  def check(self):
    (redef, other) = self.ts.parent().classExists(self)
    if redef:
      raise SemanticError(other.name.get_line(), other.name.get_col(),
                          "Clase ya definida")

    if not self.ext_name is None:
      (valid, self.ext_class) = self.ts.parent().validExtend(self.ext_name)
      if not valid:
        raise SemanticError(self.ext_name.get_line(), self.ext_name.get_col(),
                            "No existe la clase padre")

    return (True, self.gen_code())

class mjReturn(mjCheckable):
  def __init__(self, expr = None):
    self.expr = expr

  def pprint(self, tabs=0):
    if not self.expr is None:
      print "  "*tabs + "return ..."
      self.expr.pprint(tabs+1)
    else:
      print "  "*tabs + "return;"

class mjWhile(mjCheckable):
  def __init__(self, expr, statement):
    self.expr = expr
    self.statement = statement

  def pprint(self, tabs=0):
    print "  "*tabs + "while"
    print "  "*tabs + "((("
    self.expr.pprint(tabs+1)
    print "  "*tabs + ")))"
    print "  "*tabs + "{{{"
    if not self.statement is None:
      self.statement.pprint(tabs+1)
    print "  "*tabs + "}}}"

class mjIf(mjCheckable):
  def __init__(self, expr, stat, elsestat=None):
    self.expr = expr
    self.stat = stat
    self.elsestat = elsestat

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

class mjVariableDecl(mjCheckable):
  def __init__(self, ref, args):
    self.ref = ref
    self.args = args

  def pprint(self, tabs=0):
    print "  "*tabs + "Decl::" + self.ref.get_lexeme()
    for (v, e) in self.args:
      if not v is None:
        print "  "*(tabs+1) + v.get_lexeme()
      if not e is None:
        e.pprint(tabs+1)

class mjBlock(mjCheckable):
  def __init__(self, stats = [], ts=None):
    self.stats = stats
    self.ts = ts

  def set_ts(self, ts):
    self.ts = ts

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

class mjVariable(object):
  def __init__(self, typ, name, val=None):
    self.type = typ
    self.name = name
    self.val = val

class mjMethod(mjCheckable):
  def __init__(self, modifs, ret_type, name, params, body, ts, localts=None):
    self.modifs = modifs
    self.ret_type = ret_type
    self.name = name
    self.params = params
    self.processed_params = []
    self.body = body

    ts.addMethod(self)
    self.ts = localts
    if localts is None:
      self.ts = mjTS(ts)

    for (t, v) in params:
      var = mjVariable(t, v)
      self.processed_params.append(var)
      self.ts.addVar(var)

    self.create_block_ts()

  def create_block_ts(self, stat = None, last_ts = None):
    """ Crea un ts para cada block con parent en el anterior """
    if last_ts is None:
      last_ts = self.ts
    if stat is None:
      stat = self.body
    if isBlock(stat):
      ts = mjTS(last_ts)
      stat.set_ts(ts)
      for s in stat.stats:
        if not s is None:
          self.create_block_ts(s, ts)
    elif isIf(stat):
      if not stat.stat is None:
        self.create_block_ts(stat.stat, last_ts)
      if not stat.elsestat is None:
        self.create_block_ts(stat.elsestat, last_ts)
    elif isWhile(stat):
      if not stat.statement is None:
        self.create_block_ts(stat.statement, last_ts)

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

class mjClassVariableDecl(mjCheckable):
  def __init__(self, modifs, t, list_ids, ts):
    self.modifs = modifs
    self.type = t
    self.list_ids = list_ids

    for v, i in self.list_ids:
      ts.addVar(mjClassVariable(self.type, v, i, modifs))

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

class mjClassVariable(mjVariable):
  def __init__(self, ty, val, init, modifs):
    super(mjClassVariable, self).__init__(ty, val, init)
    self.modifs = modifs
