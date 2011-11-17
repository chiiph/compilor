class mjCheckable(object):
  def __init__(self):
    super(mjCheckable, self).__init__()
    self.label = ""
    self.offset = 0

  def check(self):
    raise NotImplementedError()

  def gen_code(self):
    raise NotImplementedError()
