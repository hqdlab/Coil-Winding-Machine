import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib, Gio

class Winder(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
                                     flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_prgname('Winder')
        self.windings = 0
        self.speed = 0
        self.connect("activate", self.on_activate)

    def exit(self, *args):
        self.quit()

    def on_activate(self, app):
        self.win = Gtk.ApplicationWindow(Gtk.WindowType.TOPLEVEL, application=app)
        self.win.set_title("Coil Winding Machine")
        
        
        
        buttonclose = Gtk.Button("Close")
        buttonclose.connect("clicked", self.exit)
        
        wire_dimension_label = Gtk.Label("Wire Diameter (µm)")
        self.wire_dimension = Gtk.Entry()
        
        rpm_label = Gtk.Label("RPM")
        self.rpm = Gtk.Entry()
        
        feedrate_label = Gtk.Label("Feedrate (µm)")
        self.feedrate = Gtk.Entry()
        imageleft = Gtk.Image(stock=Gtk.STOCK_GO_BACK)
        imageright = Gtk.Image(stock=Gtk.STOCK_GO_FORWARD)
        self.buttonfeed = [Gtk.ToggleButton(image=imageleft), Gtk.ToggleButton(image=imageright)]
        
        self.button_reset_feed = Gtk.Button("Reset feed")
        self.button_reset_winds = Gtk.Button("Reset winds")
        
        self.windings_label = Gtk.Label('<b><span font_desc=\"30.0\">%d wdgs</span></b>'%self.windings)
        self.windings_label.set_use_markup(True)
        
        self.speed_label = Gtk.Label('<b><span font_desc=\"30.0\">%d rpm</span></b>'%self.speed)
        self.speed_label.set_use_markup(True)
        
        self.button_start = Gtk.Button("START")
        self.button_start.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#78d678'))
        self.button_start.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#007000"))
        self.button_stop = Gtk.Button("STOP")
        self.button_stop.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#fd8181'))
        self.button_stop.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#974D4D"))

            
        vboxall = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxbuttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)
        hboxmain = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxleft = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        vboxdia = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabeldia = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxrpm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabelrpm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxfeed = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabelfeed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxfeedbuttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxwindingslabel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxspeedlabel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxright = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vboxbuttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxbutton2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    
        hboxlabeldia.pack_start(wire_dimension_label, False, False, 0)
        vboxdia.pack_start(hboxlabeldia, False, False, 5)
        vboxdia.pack_start(self.wire_dimension, False, False, 2)
        
        hboxlabelrpm.pack_start(rpm_label, False, False, 0)
        vboxrpm.pack_start(hboxlabelrpm, False, False, 5)
        vboxrpm.pack_start(self.rpm, False, False, 2)
        
        hboxlabelfeed.pack_start(feedrate_label, False, False, 0)
        vboxfeed.pack_start(hboxlabelfeed, False, False, 5)
        vboxfeed.pack_start(self.feedrate, False, False, 2)
        hboxfeedbuttons.pack_start(self.buttonfeed[0], False, False, 0)
        
        hboxfeedbuttons.pack_start(self.buttonfeed[1], False, False, 0)
        vboxfeed.pack_start(hboxfeedbuttons, False, False, 2)
        
        vboxbuttons.pack_start(self.button_start, False, False, 5)
        vboxbuttons.pack_start(self.button_stop, False, False, 5)
        hboxbutton2.pack_start(vboxbuttons, True, True, 50)
        
        vboxleft.pack_start(vboxdia, True, True, 10)
        vboxleft.pack_start(vboxrpm, True, True, 10)
        vboxleft.pack_start(vboxfeed, True, True, 10)
        vboxleft.pack_start(hboxbuttons, False, False, 10)

        
        hboxwindingslabel.pack_start(self.windings_label, False, False, 40)
        hboxspeedlabel.pack_start(self.speed_label, False, False, 40)
        
        vboxright.pack_start(hboxwindingslabel, False, False, 10)
        vboxright.pack_start(hboxspeedlabel, False, False, 10)
        vboxright.pack_start(hboxbutton2, False, False, 50)
        
        hboxbuttons.pack_start(buttonclose, True, True, 10)
        hboxmain.pack_start(vboxleft, True, True, 10)
        hboxmain.pack_start(vboxright, True, True, 10)
        vboxall.pack_start(hboxmain, True, True, 10)
        vboxall.pack_end(hboxbuttons, True, True, 10)
        
        
        self.win.add(vboxall)
        self.win.show_all()
        #self.win.fullscreen()
        self.add_window(self.win)


if __name__ == "__main__": 
    win = Winder()
    win.run(None)
