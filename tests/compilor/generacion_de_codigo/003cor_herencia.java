public class A
{
  protected static int m = 1;
  public static char b = 'b';

  protected int k = 0;
  protected char a = '2';

  public int metodo()
    {
      return 42;
    }

  public A(int b)
    {
      System.print("Desde el constructor de A!, con b = ");
      System.println(b);
    }

  public A()
    {
    }
}

public class B extends A
{
  public B(String test)
    {
      System.print("Desde B(String), con test = ");
      System.println(test);
    }

  public B()
    {
      super(2);
      this("llamo a otro constructor!");

      B.m = 42;

      System.println("Prueba de statics:");
      System.print("A.m = ");
      System.println(A.m);
      System.print("B.m = ");
      System.println(B.m);

      System.println("Prueba de super dinamico:");
      System.print("metodo() = ");
      System.println(metodo());
      System.print("super.metodo() = ");
      System.println(super.metodo());

    }

  public static void main()
    {
      B b = new B();

      System.println("Prueba de linkeo dinamico:");

      A a;
      a = new A();

      System.print("a = new A(); a.metodo() = ");
      System.println(a.metodo());

      a = b;

      System.print("a = new B(); a.metodo() = ");
      System.println(a.metodo());

    }

  public int metodo()
    {
      return 24;
    }
}
