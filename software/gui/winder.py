#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib, Gio
import threading
import serial
import time
import RPi.GPIO as GPIO
import subprocess

end_switch_channel = 21
panic_channel = 26

scaling_factor = 1.23597
tolerance = 1e-6

WIRE_DIA_MINMAX = [50, 10000]
PIT_WIDTH_MINMAX = [0.1, 5000]
loc = "/dev/ttyACM0"
baudrate = 115200


class Winder(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_prgname('Winder')
        self.windings = 0
        self.achieved_windings = 0
        self.position = 0
        self.positions = []
        self.previous_move_right = 0
        self.connect("activate", self._on_activate)
        self.offset_pos = 0
        self.offset_rot = 0
        self.moveset = []
        self.cont = False
        self.sent_windings = 0
        self.move_setting = 0
        self.buffer_size = 10
        self.on_start_clicked = False
        self.counter = 0
        self.prev = time.time()

        self.grbl = serial.Serial(loc, baudrate)
        time.sleep(5)
        self.grbl.read(self.grbl.inWaiting())
        self.grbl.write("$X\n")
        self.grbl.readline()
        self.grbl.write("?\n")
        self.grbl.readline()
        self.grbl.write("?\n")
        self.grbl.readline()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(end_switch_channel, GPIO.IN)
        GPIO.setup(panic_channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(end_switch_channel, GPIO.FALLING, callback=self.end_switch_cb, bouncetime=400)
        GPIO.add_event_detect(panic_channel, GPIO.RISING, callback=self.panic_cb, bouncetime=400) 

    def exit(self, *args):
        self.quit()

    def _on_activate(self, app):
        self.win = Gtk.ApplicationWindow(Gtk.WindowType.TOPLEVEL, application=app)
        self.win.set_title("Coil Winding Machine")

        self.win.set_default_size(800,480)
        
        buttonclose = Gtk.Button("Close")
        buttonclose.connect("clicked", self.exit)
        
        wire_dimension_label = Gtk.Label("Wire Diameter (um)")
        self.wire_dimension = Gtk.Entry()
        self.diameter = 102
        self.wire_dimension.set_text(str(self.diameter))
        
        winds_label = Gtk.Label("Winds")
        self.winds = Gtk.Entry()
        self.set_windings = 2000
        self.winds.set_text(str(self.set_windings))
        
        feedrate_label = Gtk.Label("Pit width (mm)")
        self.feed = 8
        self.feedrate = Gtk.Entry()
        self.feedrate.set_text(str(self.feed))
        imageleft = Gtk.Image(stock=Gtk.STOCK_GO_BACK)
        imageright = Gtk.Image(stock=Gtk.STOCK_GO_FORWARD)
        self.buttonfeed = [Gtk.ToggleButton(image=imageleft), Gtk.ToggleButton(image=imageright)]
        self.buttonfeed[0].set_active(False)
        self.buttonfeed[1].set_active(True) 
        
        move_label = Gtk.Label("Move (mm)")
        self.move = Gtk.Entry()
        imageleft = Gtk.Image(stock=Gtk.STOCK_GO_BACK)
        imageright = Gtk.Image(stock=Gtk.STOCK_GO_FORWARD)
        self.buttonmove = [Gtk.ToggleButton(image=imageleft), Gtk.ToggleButton(image=imageright)]
        
        self.button_reset_winds = Gtk.Button("Reset winds")
        
        self.button_increase_speed = Gtk.Button("+10%")
        self.button_decrease_speed = Gtk.Button("-10%")

        self.windings_label = Gtk.Label('<b><span font_desc=\"30.0\">%d wdgs</span></b>'%self.windings)
        self.windings_label.set_use_markup(True)
        
        self.position_label = Gtk.Label('<b><span font_desc=\"30.0\">%f mm</span></b>'%self.position)
        self.position_label.set_use_markup(True)
        
        self.button_start = Gtk.Button("START")
        self.button_start.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#78d678'))
        self.button_start.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#007000"))
        self.button_start.set_property("width-request", 200)
        self.button_start.set_property("height-request", 50)
        self.button_stop = Gtk.Button("STOP")
        self.button_stop.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#fd8181'))
        self.button_stop.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#974D4D"))
        self.button_stop.set_property("width-request", 200)
        self.button_stop.set_property("height-request", 50)
       
        
        self.button_home = Gtk.Button("Home")
        self.button_panic = Gtk.Button("Panic")
        self.button_unlock = Gtk.Button("Unlock")

            
        vboxall = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxbuttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxmain = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxleft = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        vboxdia = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabeldia = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxentrydia = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxwinds = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabelwinds = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxentrywinds = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxfeed = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabelfeed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxentryfeed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxfeedbuttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxmove = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hboxlabelmove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxresetwinds = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxentrymove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxmovebuttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxwindingslabel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxpositionlabel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxright = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vboxbuttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        hboxbutton2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxspeedadjust = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hboxlabeldia.pack_start(wire_dimension_label, False, False, 0)
        hboxentrydia.pack_start(self.wire_dimension, False, False, 0)
        vboxdia.pack_start(hboxlabeldia, False, False, 5)
        vboxdia.pack_start(hboxentrydia, False, False, 2)
        
        hboxlabelwinds.pack_start(winds_label, False, False, 0)
        hboxentrywinds.pack_start(self.winds, False, False, 0)
        vboxwinds.pack_start(hboxlabelwinds, False, False, 5)
        vboxwinds.pack_start(hboxentrywinds, False, False, 2)
        
        hboxlabelfeed.pack_start(feedrate_label, False, False, 0)
        hboxentryfeed.pack_start(self.feedrate, False, False, 0)
        vboxfeed.pack_start(hboxlabelfeed, False, False, 5)
        vboxfeed.pack_start(hboxentryfeed, False, False, 2)
        hboxfeedbuttons.pack_start(self.buttonfeed[0], False, False, 0)
        hboxfeedbuttons.pack_start(self.buttonfeed[1], False, False, 0)
        vboxfeed.pack_start(hboxfeedbuttons, False, False, 2)

        hboxspeedadjust.pack_start(self.button_increase_speed, False, False, 10)
        hboxspeedadjust.pack_start(self.button_decrease_speed, False, False, 10)
        vboxspeedadjust = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vboxspeedadjust.pack_start(hboxspeedadjust, True, True, 80)

        hboxlabelmove.pack_start(move_label, False, False, 0)
        hboxentrymove.pack_start(self.move, False, False, 0)
        vboxmove.pack_start(hboxlabelmove, False, False, 5)
        vboxmove.pack_start(hboxentrymove, False, False, 2)
        hboxmovebuttons.pack_start(self.buttonmove[0], False, False, 0)
        hboxmovebuttons.pack_start(self.buttonmove[1], False, False, 0)
        vboxmove.pack_start(hboxmovebuttons, False, False, 2)

        hboxresetwinds.pack_start(self.button_reset_winds, False, True, 0)

        vboxbuttons.pack_start(self.button_start, False, False, 5)
        vboxbuttons.pack_start(self.button_stop, False, False, 5)
        hboxbutton2.pack_start(vboxbuttons, True, False, 20)
        
        vboxleft.pack_start(vboxdia, True, True, 0)
        vboxleft.pack_start(vboxwinds, True, True, 0)
        vboxleft.pack_start(vboxfeed, True, True, 0)
        vboxleft.pack_start(vboxmove, True, True, 0)
        vboxleft.pack_start(hboxresetwinds, False, True, 0)

        hboxwindingslabel.pack_start(self.windings_label, False, False, 40)
        hboxpositionlabel.pack_start(self.position_label, False, False, 40)
        vboxright.pack_start(hboxwindingslabel, False, False, 10)
        vboxright.pack_start(hboxpositionlabel, False, False, 10)
        vboxright.pack_start(hboxbutton2, False, False, 10)
        vboxright.pack_start(vboxspeedadjust, False, False, 30)        

        hboxbuttons.pack_start(self.button_home, False, False, 10)
        hboxbuttons.pack_start(self.button_unlock, False, False, 10)
        #hboxbuttons.pack_start(self.button_panic, False, False, 10)
        hboxbuttons.pack_end(buttonclose, False, False, 20)
        hboxmain.pack_start(vboxleft, True, True, 10)
        hboxmain.pack_start(vboxright, True, True, 10)
        vboxall.pack_start(hboxmain, True, True, 10)
        vboxall.pack_start(hboxbuttons, False, False, 20)
        
        self.buttonfeed[0].connect("clicked", self._on_feed_button_clicked, 0)
        self.buttonfeed[1].connect("clicked", self._on_feed_button_clicked, 1)
        self.button_start.connect("clicked", self._on_start_button_clicked)
        self.button_stop.connect("clicked", self._on_stop_button_clicked)
        self.button_home.connect("clicked", self._on_button_home_clicked)
        self.button_unlock.connect("clicked", self._on_button_unlock_clicked)
        self.buttonmove[0].connect("clicked", self._on_move_button_clicked, -1)
        self.buttonmove[1].connect("clicked", self._on_move_button_clicked, 1)
        self.button_reset_winds.connect("clicked", self._on_button_reset_windings_clicked)
        self.button_panic.connect("clicked", self._on_button_panic_clicked)
        self.button_decrease_speed.connect("clicked", self._on_button_speed_clicked, -1)        
        self.button_increase_speed.connect("clicked", self._on_button_speed_clicked, 1)                

        GLib.timeout_add(100, self.update_labels)
        self.win.add(vboxall)
        self.win.show_all()
        self.win.fullscreen()
        self.add_window(self.win)

    def _on_button_home_clicked(self, widget):
        self.set_widgets_sensitive(False)
        self.button_start.set_sensitive(False)
        self.button_stop.set_sensitive(False)
        self.button_home.set_sensitive(False)
        self.grbl.write("$H\n")
        GLib.timeout_add(500, self.move_home)

    def _on_button_unlock_clicked(self, widget):
        self.grbl.write("$X\n")
        self.grbl.read(self.grbl.inWaiting())

    def _on_button_panic_clicked(self, widget):
        self.grbl.write("\x18\n")
        self.grbl.flush()
        time.sleep(0.5)
        self.grbl.write("$X\n")
        self.grbl.read(self.grbl.inWaiting())

    def panic_cb(self, channel):
        print("cb detected")

    def _on_button_speed_clicked(self, widget, dir):
        time.sleep(0.5)
        if dir== 1:
            self.grbl.write("\x91\n")
        elif dir== -1:
            self.grbl.write("\x92\n")
        self.grbl.read(self.grbl.inWaiting())

    def _on_move_button_clicked(self, widget, side):
        if widget.get_active():
            dist = self.move.get_text()
            try:
                dist = float(dist)*side
            except:
                return False
            self.set_widgets_sensitive(False)
            self.button_start.set_sensitive(False)
            self.button_stop.set_sensitive(False)
            self.button_home.set_sensitive(False)
            
            self.move_around(dist)
            GLib.timeout_add(500, self.move_feed, dist)

    def _on_start_button_clicked(self, widget):
        ret = self.check_widgets_input()
        if ret:
            if not self.on_start_clicked:
                self.set_widgets_sensitive(False)
                
                if self.buttonfeed[0].get_active() and not self.buttonfeed[1].get_active():
                    self.move_setting = -1
                elif self.buttonfeed[1].get_active() and not self.buttonfeed[0].get_active():
                    self.move_setting = 1
                temp, rot = self.get_current_pos()
                if temp:
                    self.offset_pos = temp
                    self.offset_rot = rot
                self.position = self.offset_pos
                self.diameter = float(self.wire_dimension.get_text())
                self.feed = float(self.feedrate.get_text())
                self.set_windings = float(self.winds.get_text())
                self.moveset = self.create_moveset(self.set_windings, self.diameter, self.feed, self.move_setting)
                self.on_start_clicked = True
                self.cont = True
                self.do_winding(self.diameter, self.feed, self.moveset)
            self.grbl.write("~\n")
            self.cont = True

    def _on_stop_button_clicked(self, widget):
        self.cont = False
        self.button_reset_winds.set_sensitive(True)
        self.grbl.write(b"!\n")

    def _on_button_reset_windings_clicked(self, widget):
        self.achieved_windings = 0
        self.position = 0
        self.move_setting = 0
        self.on_start_clicked = False
        self.counter = 0
        self.offset_pos = 0
        self.offset_rot = 0
        self.sent_windings = 0
        self.cont = False
        self.windings_label.set_markup('<b><span font_desc=\"30.0\">0 wdgs</span></b>')
        self.position_label.set_markup('<b><span font_desc=\"30.0\">%.3f mm</span></b>'%self.position)
        self.grbl.write("\x18\n")
        time.sleep(0.5)
        self.grbl.write("$X\n")
        time.sleep(0.1)
        self.grbl.read(self.grbl.inWaiting())
        self.set_widgets_sensitive(True)

    def _on_feed_button_clicked(self, widget, side):
        state = widget.get_active()
        other_widget = self.buttonfeed[not side]
        other_state = other_widget.get_active()
        if (state) and (other_state):
            other_widget.set_active(0)

    def update_labels(self):
        self.position_label.set_markup('<b><span font_desc=\"30.0\">%.3f mm</span></b>'%(self.position-self.offset_pos))
        self.windings_label.set_markup('<b><span font_desc=\"30.0\">%d wdgs</span></b>'%(self.achieved_windings))
        return True

    def end_switch_cb(self, channel):
        ret, rot = self.get_current_pos()
        if ret:
            self.position = ret
        else:
            rot = 0
        self.achieved_windings = int(round(abs(rot-self.offset_rot)))
        windings_per_feed = int(self.feed/(1e-3*self.diameter))
        if (self.achieved_windings + 15)%windings_per_feed == 0:
            self.do_winding(self.diameter, self.feed, self.moveset)
        if self.check_windings() <= 0:
            self.set_widgets_sensitive(True)
            self.button_start.set_sensitive(True)
            self.button_stop.set_sensitive(True)
            self.button_home.set_sensitive(True)
            self.buttonmove[0].set_active(0)
            self.buttonmove[1].set_active(0)

    def move_feed(self, dist):
        state = self.ask_grbl_finished()
        if state:
            self.set_widgets_sensitive(True)
            self.button_start.set_sensitive(True)
            self.button_stop.set_sensitive(True)
            self.button_home.set_sensitive(True)
            self.buttonmove[0].set_active(0)
            self.buttonmove[1].set_active(0)
            return False
        else:
            return True

    def move_home(self):
        state = self.ask_grbl_finished()
        if state:
            self.grbl.write(b"G21 G91 G1 Z40 F2000\n")
            time.sleep(6)
            self.grbl.write("$X\n")
            self.set_widgets_sensitive(True)
            self.button_start.set_sensitive(True)
            self.button_stop.set_sensitive(True)
            self.button_home.set_sensitive(True)
            self.buttonmove[0].set_active(0)
            self.buttonmove[1].set_active(0)
            return False
        else:
            return True

    def ask_grbl_finished(self):
        self.grbl.read(self.grbl.inWaiting())
        self.grbl.write(b"?\n")
        time.sleep(0.1)
        ret = self.grbl.readline()
        state = ret.split("|")[0]
        if state == "<Idle":
            return True
        else:
            return False

    def get_current_pos(self):
        self.grbl.read(self.grbl.inWaiting())
        self.grbl.write(b"?\n")
        time.sleep(0.1)
        ret = self.grbl.read(self.grbl.inWaiting())
        if ret == '':
            return None, None
        try:
            val = ret.split("|")[1]
        except:
            return None, None
        return float(val.split(",")[2]), float(val.split(",")[1])

    def start_cycle(self, diameter, feed, moveset):
        while True:
            if not self.cont: break
            ret = self.do_winding(diameter, feed, moveset)
            if not self.cont: break
            time.sleep(2)

    def do_winding(self, diameter, feed, commands):
        if self.counter > len(commands) - 1:
            self.cont = False
            return False
        self.grbl.read(self.grbl.inWaiting())
        command = commands[self.counter]
        self.grbl.write(command)
        resp = self.grbl.readline()
        if self.cont:
            self.counter += 1
        if self.counter > len(commands)-1:
            self.cont = False
            resp = False
        return resp

    def create_moveset(self, windings, diameter, feed, initial_move):
        windings_per_feed = int(feed/(1e-3*diameter))
        n = int(windings/windings_per_feed)
        move_right = initial_move
        moveset = []
        for i in range(n):
            if i==0:
                moveset.append(b"G21 G91 G1 Y-%d Z%f F60\n"%(windings_per_feed, move_right*feed))  
            else:
                moveset.append(b"G21 G91 G1 Y-%d Z%f\n"%(windings_per_feed, move_right*feed))
            move_right *= -1         
        remaining_windings = int(windings - n*windings_per_feed)
        moveset.append(b"G21 G91 G1 Y-%d Z%f\n"%(remaining_windings, move_right*diameter*1e-3*remaining_windings))
        return moveset

    def check_windings_sent(self):
        return self.set_windings - self.sent_windings

    def check_windings(self):
        return self.set_windings - self.achieved_windings

    def move_around(self, dist):
        while not self.ask_grbl_finished():
            time.sleep(0.5)
        self.grbl.write(b"G21 G91 G1 Z%f F1000\n"%(dist))
        return True

    def set_widgets_sensitive(self, sens):
        self.wire_dimension.set_sensitive(sens)
        self.feedrate.set_sensitive(sens)
        self.winds.set_sensitive(sens)
        self.buttonfeed[0].set_sensitive(sens)
        self.buttonfeed[1].set_sensitive(sens)
        self.buttonmove[0].set_sensitive(sens)
        self.buttonmove[1].set_sensitive(sens)
        self.move.set_sensitive(sens)
        self.button_reset_winds.set_sensitive(sens)

    def check_widgets_input(self):
        diameter = self.wire_dimension.get_text()
        feed = self.feedrate.get_text()
        winds = self.winds.get_text()
        if not diameter or not feed or not winds:
            return False
        try:
            diameter = float(diameter)
            feed = float(feed)
            winds = float(winds)
        except:
            return False

        if diameter > WIRE_DIA_MINMAX[1] or diameter < WIRE_DIA_MINMAX[0]:
            return False
        if feed > PIT_WIDTH_MINMAX[1] or feed < PIT_WIDTH_MINMAX[0]:
            return False

        return True


if __name__ == "__main__":
    win = Winder()
    win.run(None)

