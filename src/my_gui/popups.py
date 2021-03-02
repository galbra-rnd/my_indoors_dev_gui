from Tkinter import *


class NewHomePosition(object):
    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.l = Label(top, text="New Home Position")
        self.l.grid(column=0, row=0)

        # Position
        self.x_label = Label(top, text="X:")
        self.x_label.grid(column=0, row=1)
        self.x_input = Entry(top)
        self.x_input.grid(column=1, row=1)

        self.y_label = Label(top, text="Y:")
        self.y_label.grid(column=0, row=2)
        self.y_input = Entry(top)
        self.y_input.grid(column=1, row=2)

        self.z_label = Label(top, text="Z:")
        self.z_label.grid(column=0, row=3)
        self.z_input = Entry(top)
        self.z_input.grid(column=1, row=3)

        # Orientation
        self.qx_label = Label(top, text="qX:")
        self.qx_label.grid(column=0, row=4)
        self.qx_input = Entry(top)
        self.qx_input.grid(column=1, row=4)

        self.qy_label = Label(top, text="qY:")
        self.qy_label.grid(column=0, row=5)
        self.qy_input = Entry(top)
        self.qy_input.grid(column=1, row=5)

        self.qz_label = Label(top, text="qZ:")
        self.qz_label.grid(column=0, row=6)
        self.qz_input = Entry(top)
        self.qz_input.grid(column=1, row=6)

        self.qw_label = Label(top, text="qW:")
        self.qw_label.grid(column=0, row=7)
        self.qw_input = Entry(top)
        self.qw_input.grid(column=1, row=7)

        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.grid(column=1, row=4)
        self.home_position_xyz = [0.0, 0.0, 0.0]
        self.home_orientation_xyzw = [0.0, 0.0, 0.0, 0.0]

    def cleanup(self):
        self.value = self.x_input.get()
        self.home_position_xyz = [
            float(self.x_input.get()), float(self.y_input.get()), float(self.z_input.get())]

        self.home_orientation_xyzw = [float(self.qx_input .get()), float(self.qy_input.get()), float(self.qz_input.get()),float(self.qw_input.get())]
        self.top.destroy()


class mainWindow(object):
    def __init__(self, master):
        self.master = master
        self.b = Button(master, text="Set HomePosition",
                        command=self.new_home_popup)
        self.b.pack()
        self.b2 = Button(master, text="print value",
                         command=lambda: sys.stdout.write(self.entryValue()+'\n'))
        self.b2.pack()

    def new_home_popup(self):
        self.new_home_window = NewHomePosition(self.master)
        self.b["state"] = "disabled"
        self.master.wait_window(self.w.top)
        self.b["state"] = "normal"

    def entryValue(self):
        # return self.w.value
        return self.new_home_window.home_position_xyz


if __name__ == "__main__":
    root = Tk()
    m = mainWindow(root)
    root.mainloop()
