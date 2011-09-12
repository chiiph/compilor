asciidoc -a lang=es -v -b docbook -d book informe_lexor.txt
dblatex -V -T db2latex informe_lexor.xml
rm informe_lexor.xml
