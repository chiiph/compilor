#!/bin/bash

rm parser.java sym.java *.lex.java
jlex *.lex
cup *.cup
javac *.java