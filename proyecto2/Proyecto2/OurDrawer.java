package Proyecto2;

import Proyecto2.Drawer;

public class OurDrawer {

    private Drawer drawer;

    public OurDrawer() {
        drawer = new Drawer();
    }

    public void evaluate(String command) {

        String[] command_parameters = command.split(",");

        if (command.startsWith("draw")) {
            drawer.draw(new Integer(command_parameters[1]));
        }
        if (command.startsWith("draw_named")) {
            drawer.drawNamedDraw(new Integer(command_parameters[1]));
        }
        if (command.startsWith("rotate")) {
            drawer.rotate(new Integer(command_parameters[1]));
        }
        if (command.startsWith("move")) {
            drawer.move(new Integer(command_parameters[1]));
        }
    }

    public void reset() {
        drawer.reset();
    }

    public void setColor(int r, int g, int b) {
        drawer.setColor(r, g, b);
    }

    public void setNamedDraw(int id, String list) {
        String[] cmds = list.split(";");
        drawer.beginNamedDraw(id);
        for(int i = 0; i < cmds.length; i++)
            evaluate(cmds[i]);

        drawer.endNamedDraw();
    }
}
