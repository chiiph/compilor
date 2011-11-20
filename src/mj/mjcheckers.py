class mjCheckable(object):
  def __init__(self):
    super(mjCheckable, self).__init__()
    self.label = ""
    self.offset = 0
    self.ts = None

  def check(self):
    raise NotImplementedError()

  def set_ts(self, ts):
    self.ts = ts
