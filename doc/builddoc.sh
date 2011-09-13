asciidoc -a lang=es -v -b docbook -d book $1.txt
dblatex -V -T db2latex $1.xml
rm $1.xml
