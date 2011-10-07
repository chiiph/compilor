package Proyecto2;

public class OurSymbol {
    private String type;
    private String name;
    private Integer value;

    public OurSymbol(String type, String name, Integer value) {
        this.type = type;
        this.name = name;
        this.value = value;
    }

    public String getName() { return name; }
    public String getType() { return type; }
    public Integer getValue() { return value; }

    public void setValue(Integer v) { this.value = v; }
}
