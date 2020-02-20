import pygtk
pygtk.require('2.0')
import gtk

class MainWindow(gtk.Window):
   def __init__(self):
     gtk.Window.__init__(self)
     self.set_default_size(300, 300)
     self.addServer()

   def launchBrowser(self, widget, event, host, *args):
      if event.type == gtk.gdk.BUTTON_PRESS:
        if event.button == 3:
            print ("click")
     # Normal behaviour of Expander on single click
      expand = widget.get_expanded()
      if not expand: widget.set_expanded(True)
      else: widget.set_expanded(False)

   def addServer(self):
    main_expand = gtk.Expander()
    main_led = gtk.Image()
    main_led.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)

    main_srvname = gtk.Label("srvname")
    main_expand.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    main_expand.connect('button-press-event', self.launchBrowser, 'host')

    expand_title = gtk.HBox(False, 2)
    expand_title.pack_start(main_led, False, True, 0)
    expand_title.pack_start(main_srvname, True, True, 0)
    main_expand.set_property("label-widget", expand_title)

    self.add(main_expand)
    self.show_all()

def main():
 MainWindow()
 gtk.main()

if __name__ == '__main__':
 main()