package Proyecto2;

public class OurDrawer {

    private drawer;

    public OurDrawer() {
        drawer = new Drawer();
    }

    public void eval(String command) {

        String[] command_parameters = command.split(",");

        if (command.startsWith("draw")) {
            drawer.draw(Integer(command_parameters[1]));
        }
        if (command.startsWith("draw_named")) {
            drawer.drawNameDraw(Integer(command_parameters[1]));
        }
        if (command.startsWith("rotate")) {
            drawer.rotate(Integer(command_parameters[1]));
        }
        if (command.startsWith("move")) {
            drawer.move(Integer(command_parameters[1]));
        }
    }

    public void reset() {
        drawer.reset();
    }

    public void setColor(int r, int g, int b) {
        drawer.seColor(r, g, b);
    }

    public void setNamedDraw(int id, String list) {
        String cmds[] = list.split(";");
        drawer.beginNamedDraw(id);
        for(int i = 0; i < cmds.size(), i++)
            eval(cmds[i]);

        drawer.endNamedDraw();
    }
}
