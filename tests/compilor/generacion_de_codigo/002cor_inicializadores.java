public class Algo
{
  public int a = 4;
  public String h = "hola";
  public int d = metodo();
  public char j = otro_metodo(this);

  public static int m = algo();
  public static String jh = "chau";
  public static char q = 'm';

  public Algo()
    {
      System.println(a);
      System.println(h);
      System.println(d);
      System.println(j);
      System.println(Algo.m);
      System.println(Algo.jh);
      System.println(Algo.q);
    }

  public static int algo()
    {
      return 1;
    }

  public int metodo()
    {
      return 3;
    }

  public char otro_metodo(Algo b)
    {
      return 'a';
    }

  public static void main()
    {
      Algo b = new Algo();
    }
}

public class AlgoMas
{
  public static int j = 3;
  public static char m = '5';
}
