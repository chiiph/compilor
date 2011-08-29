Descripción:
  Algunos operadores contienen más de un carácter, la idea este caso
  de test es mostrar que se detectan situaciones erroneas como la
  escritura de "&" en lugar de "&&", siendo este último, el único
  operador con el caracter '&' válido.

Resultado esperado:
  Se deberá detectar el token erróneo, y se mostrará por pantalla la
  posición del mismo en el archivo de código fuente.