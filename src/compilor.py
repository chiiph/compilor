import sys
from syntaxor import Syntaxor
from lexor import Token
from constants import *
from errors    import LexicalError, SemanticError, SyntaxError

from mj.mjclass import mjClass
from mj.mjts import mjTS

def pretty_print_error_message(input_filepath, exc):
  input_file = open(input_filepath, 'r')
  line = exc.line
  col  = exc.col
  print exc
  print "In line %s:%s" % (line, col)
  i = 0
  line_str = ""
  while (i < line):
    line_str = input_file.readline()
    i += 1

  if len(line_str) > 0 and line_str[-1] == "\n":
    print line_str,
  else:
    print line_str
  i = 0
  while (i < col):
    sys.stdout.write("-")
    i += 1
  print "^"
  input_file.close()
  sys.exit()

def usage():
  usage_str = """
  Error: two arguments required.
  Usage:
    compilor INPUTFILE OUTPUTFILE

  """
  print usage_str

if __name__ == "__main__":
  argv_len = len(sys.argv)
  if ((argv_len == 3) or (argv_len == 2)):
    input_filepath = sys.argv[1]
    try:
      syntaxor = Syntaxor(input_filepath)
    except IOError as ioe:
      print "Error: no such file."
      sys.exit()

    if (argv_len == 3):
      output_filepath = sys.argv[2]
      output_file = open(output_filepath, 'w')
      sys.stdout = output_file

    try:
      ts = mjTS()
      s = Token()
      s._lexeme = "String"
      mjClass(s, None, [], ts)
      ast = syntaxor.check_syntax(ts)
      print ts, "=================="
      ts.pprint()
      print "==================="

      for cl in ast:
        cl.pprint()
        #cl.pprint_ts()
        cl.check()

    except SemanticError as se:
      pretty_print_error_message(input_filepath, se)
    except SyntaxError as se:
      pretty_print_error_message(input_filepath, se)
    except LexicalError as le:
      pretty_print_error_message(input_filepath, le)

    print "La sintaxis de %s es correcta." % input_filepath

    if (argv_len == 3):
      output_file.close()
  else:
    usage()
