public class Algo
{
  public static void main()
    {
      Algo b = new Algo();

      b.metodo_solo();
      int r = b.metodo();
      System.println("metodo() retorno:");
      System.println(r);

      b.metodo(1);
      b.metodo(2, b.metodo_mult());
      r = b.metodo('a', 42);
      System.println("metodo(char,int) retorno:");
      System.println(r);
    }

  public void metodo_solo()
    {
      System.println("Desde metodo_solo");
    }

  public int metodo()
    {
      System.println("Desde metodo");
      return 1;
    }

  public Algo metodo_mult()
    {
      System.println("Desde metodo_mult");

      return this;
    }

  public void metodo(int a)
    {
      System.println("Desde metodo(char)");
      System.println(a);
    }

  public void metodo(int a, Algo b)
    {
      System.println("Desde metodo(char,char)");
      System.println(a);
    }

  public int metodo(char a, int b)
    {
      System.println("Desde metodo(char,int)");
      System.println(a);
      System.println(b);

      return b;
    }
}
