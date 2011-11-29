public class StringTest
{
  public static void main()
    {
      String a = "hola!";
      System.print("Prueba de length: a.length() = ");
      System.println(a.length());

      System.print("Prueba de charAt: a.charAt(0) = ");
      System.println(a.charAt(6));

      System.print("Prueba de concat: \"hola\" concatenado con \"chau!\": ");
      System.println("hola".concat("chau!"));

      System.print("Prueba de concat con +: ");
      System.println("hola"+"chau!");

      System.print("Prueba de equals \"hola\".equals(\"chau\") = ");
      System.println("hola".equals("chau"));

      System.print("Prueba de equals \"hola\".equals(\"hola\") = ");
      System.println("hola".equals("hola"));
    }
}
