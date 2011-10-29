class mjCheckable(object):
  def check(self):
    raise NotImplementedError()

  def gen_code(self):
    raise NotImplementedError()
