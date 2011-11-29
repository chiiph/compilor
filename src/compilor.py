import sys,os
from syntaxor import Syntaxor
from lexor import Token
from constants import *
from errors    import LexicalError, SemanticError, SyntaxError

from mj.mjclass import mjClass
from mj.mjts import mjTS

def find_biggest_label(code):
  biggest = 0
  for l in code.split("\n"):
    cur = l.find(":")
    if cur > biggest:
      biggest = cur

  return biggest

def find_farthest_comment(code):
  biggest = 0
  for l in code.split("\n"):
    cur = find_comment(l)
    if cur > biggest:
      biggest = cur

  return biggest

def find_comment(line):
  pos = 0
  found = False
  while not found and pos < len(line):
    if line[pos] == ";":
      return pos
    if line[pos] == "'":
      pos += 1
      while line[pos] != "'":
        pos += 1

    pos += 1

  return -1

def align_comments(code):
  s = find_farthest_comment(code)
  pretty_code = ""
  for l in code.split("\n"):
    has = find_comment(l)
    if has == -1:
      pretty_code += l + "\n"
    else:
      parts = [l[:-(len(l)-has)], l[has:]]
      pretty_code += parts[0] + " "*(s-len(parts[0])) + parts[1] + "\n"

  return pretty_code

def align_labels(code):
  i = find_biggest_label(code)
  pretty_code = ""
  char_dots = -1
  for l in code.split("\n"):
    char_dots = l.find("':'")
    has = l.find(":")
    if char_dots != -1 and char_dots+1 == has:
      has = l.find(":", char_dots+2)
    if has == -1:
      sep = " "*(i+2)
      if l.find(".") == 0:
        sep = ""
      pretty_code += sep + l + "\n"
    else:
      parts = l.split(":")
      label = parts[0]
      rest = ":".join(parts[1:])
      pretty_code += label + ":" + " "*(i-has) + rest + "\n"

  return pretty_code

def prettify_code(code):
  return align_comments(align_labels(code))

def strip_code(code):
  final = ""
  for l in code.split("\n"):
    s = l.strip()
    if len(s) == 0:
      continue
    final += s + "\n"
  return final

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
      #system_classes = open("src/system_classes.java", "r").read()
      syntaxor = Syntaxor(input_filepath)
    except IOError as ioe:
      print "Error: no such file."
      sys.exit()

    if (argv_len == 3):
      output_filepath = sys.argv[2]
      output_file = open(output_filepath, 'w')

    code = ""
    try:
      ts = mjTS()
      ast = syntaxor.check_syntax(ts)

      # for cl in ast:
      #   cl.pprint()
      #   cl.pprint_ts()

      code = prettify_code(strip_code(ts.check())).replace("\n", os.linesep)
      #code = ts.check().replace("\n", os.linesep)

      fileobj = None
      if argv_len == 3:
        fileobj = output_file
      else:
        output_filepath = input_filepath.replace(".java", ".asm")
        fileobj = open(output_filepath, 'w')

      fileobj.write(code)

    except SemanticError as se:
      pretty_print_error_message(input_filepath, se)
    except SyntaxError as se:
      pretty_print_error_message(input_filepath, se)
    except LexicalError as le:
      pretty_print_error_message(input_filepath, le)

    print "%s es un archivo MiniJava correcto." % input_filepath
    print "El output ha sido generado en %s" % output_filepath

    if (argv_len == 3):
      output_file.close()
    else:
      fileobj.close()
  else:
    usage()
