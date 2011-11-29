public class TestIfs
{
  public static void main()
    {
      System.println("Antes del if...");

      if(true) {
        System.print("Bloque");
        System.println(" then...");
      } else {
        System.println("Bloque else...");
      }

      System.println("Despues del primer if...");

      if(false)
        System.print("Bloque then ...");
      else
        System.println("Bloque else...");
    }
}
