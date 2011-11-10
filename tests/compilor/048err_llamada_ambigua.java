public class test
{
  public static void main()
    {
    }

  public test()
    {
      ambiguo(new C(), new C());
    }
  public void ambiguo(A p, B p2)
    {
    }

  public void ambiguo(B p, A p2)
    {
    }

}

public class A
{
}

public class B extends A
{
}

public class C extends B
{
}
