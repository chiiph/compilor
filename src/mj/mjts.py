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
    if self.methodExists(m.get_signature()):
      return False
    self._sections["methods"][m.get_signature()] = m
    return True

  def typeExists(self, t):
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

  def methodExists(self, m):
    return m in self._sections["methods"].keys()

  def getVar(self, v):
    return self._sections["variables"][v]

  def getType(self, v):
    return self._sections["classes"][v]

  def getMethod(self, m):
    return self._sections["methods"][m]

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
