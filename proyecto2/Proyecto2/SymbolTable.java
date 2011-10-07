package Proyecto2;

import java.security.SecureRandom;
import java.math.BigInteger;
import java.util.LinkedList;

public class SymbolTable {
    private LinkedList<OurSymbol> table;
    private int lastAnon;

    public SymbolTable() {
        lastAnon = 0;
        table = new LinkedList();
    }

    // 0: Ok
    // 1: Variable ya declarada del mismo tipo
    // 2: Variable declarada de distinto tipo
    public int addVar(String type, String name, Integer value) {
        for(int i = 0; i < table.size(); i++) {
            if(table.get(i).getName().equals(name) &&
               table.get(i).getType().equals(type))
                return 1;
            if(table.get(i).getName().equals(name) &&
               !(table.get(i).getType().equals(type)))
                return 2;
        }

        table.add(new OurSymbol(type, name, value));
        return 0;
    }

    public boolean isDeclared(String name) {
        for(int i = 0; i < table.size(); i++) {
            if(table.get(i).getName().equals(name))
                return true;
        }

        return false;
    }

    public OurSymbol get(String name) {
        for(int i = 0; i < table.size(); i++) {
            if(table.get(i).getName().equals(name))
                return table.get(i);
        }

        return null;
    }

    public Integer getValue(String name) {
        for(int i = 0; i < table.size(); i++) {
            if(table.get(i).getName().equals(name))
                return table.get(i).getValue();
        }

        return null;
    }

    public void setValue(String name, Integer value) {
        int pos = -1;
        for(int i = 0; i < table.size(); i++) {
            if(table.get(i).getName().equals(name)) {
                pos = i;
                break;
            }
        }

        if(pos == -1)
            return;

        table.get(pos).setValue(value);
    }

    public String addAnonymVar(String type, Integer value) {
        int res = 1;
        String name = "__anon" + lastAnon++;

        res = addVar(type, name, value);
        return name;
    }
}