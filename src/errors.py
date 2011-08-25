class LexicalError(Exception):
    def __init__(self, line, col, msg = "Token no reconocido."):
        self.message = "ERROR: Line: %d, Col: %d :: %s" % (line, col, msg)

    def __str__(self):
        return self.message

