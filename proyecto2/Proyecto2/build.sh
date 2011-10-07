#!/bin/bash

rm parser.java sym.java *.lex.java
jlex *.lex
cup *.cup
CLASSPATH=$CLASSPATH:.:/usr/share/java/cup.jar javac -d . *.java