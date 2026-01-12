#!/usr/bin/env python3

# V. 0.9.2

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
# gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf

import os,sys,shutil
import subprocess
import time
from threading import Thread
from threading import Event
import signal

from menusettings import *

##############

# _display = Gdk.Display.get_default()
# display_type = GObject.type_name(_display.__gtype__)

# is_wayland = display_type=="GdkWaylandDisplay"
# if not is_wayland:
    # _error_log("Wayland required.")
    # print("Wayland required.")
    # sys.exit()

# is_x11 = display_type=="GdkX11Display"
# if is_x11:
    # _error_log("Wayland required.")
    # print("Wayland required.")
    # sys.exit()

# if is_wayland:
    # ret = GtkLayerShell.is_supported()
    # if ret == False:
        # _error_log("Gtk layer shell support required.")
        # sys.exit()

##############

# theme variation: 0 toggle buttons - 1 plain buttons (a label appears below) 
USER_THEME=0

# program directory
main_dir = os.getcwd()
icon_dir = os.path.join(main_dir, "icons")
FIFO = os.path.join(main_dir,'myfifo')

if not os.path.exists(os.path.join(main_dir,"favorites")):
    _f = open(os.path.join(main_dir,"favorites"),"w")
    _f.write("\n")
    _f.close()

# WWIDTH = 880
# WEIGHT = 600
# try:
    # with open(os.path.join(main_dir,"menusize"),"r") as f:
        # _line = f.readline()
        # _WWIDTH, _WEIGHT = _line.strip().split(";")
    # WWIDTH = int(_WWIDTH)
    # WEIGHT = int(_WEIGHT)
# except:
    # pass

WWIDTH = WIN_WIDTH
WEIGHT = WIN_HEIGHT

################### MENU

from modules import pop_menu
from modules import pop_menu_item

import queue
q = queue.Queue(maxsize=1)

# add a monitor after adding a new path
app_dirs_user = [os.path.join(os.path.expanduser("~"), ".local/share/applications")]
app_dirs_system = ["/usr/share/applications", "/usr/local/share/applications"]

#### main application categories
Bookmarks = []
Development = []
Education = []
Game = []
Graphics = []
Multimedia = []
Network = []
Office = []
Settings = []
System = []
Utility = []
Other = []

# # commands: __open __close __exit
# if not os.path.exists(FIFO):
    # os.mkfifo(FIFO)

USE_LABEL_CATEGORY=1

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gmenu-1")
        self.set_icon_from_file(icon_dir+"/menu.svg")
        self.set_title("Gmenu-1")
        self.set_decorated(False)
        # self.set_property("decorated", False)
        # self.set_property("skip-taskbar-hint", True)
        # self.set_property("skip-pager-hint", True)
        self.connect("delete-event", self._to_close)
        self.connect('hide', self.on_hide)
        self.connect('show', self.on_show)
        if CLOSE_FOCUS_LOST:
            self.connect('focus-out-event', self.on_lost_focus)
        self.set_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.connect('key-press-event', self.on_key_pressed)
        self.set_keep_above(True)
        if WIN_POSITION != "":
            self.WX,self.WY = WIN_POSITION.split(":")
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
        #
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_decorated(False)
        #
        self.TERMINAL = TERMINAL
        #
        self.set_border_width(5)
        self.set_default_size(WWIDTH, WEIGHT)
        self.set_resizable(True)
        # # vertical box for all widgets
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.hbox.set_homogeneous(False)
        self.add(self.hbox)
        # # 1 top - 2 left - 3 right
        if CAT_LAYOUT == 1:
            # # category box
            self.cbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            self.cbox.set_homogeneous(True)
            # self.hbox.add(self.cbox)
            self.hbox.pack_start(self.cbox, False, False, 1)
        elif CAT_LAYOUT == 2 or CAT_LAYOUT == 3:
            self.cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            self.cbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.cbox.set_homogeneous(True)
            if CAT_LAYOUT == 2:
                # self.cat_box.add(self.cbox)
                self.cat_box.pack_start(self.cbox, False, False, 1)
                self.hbox.pack_start(self.cat_box, False, False, 1)
        #
        if USER_THEME == 1 and USE_LABEL_CATEGORY == 1:
            self.clabel = Gtk.Label(label="co")
            self.clabel.set_name("myclabel")
            self.hbox.pack_start(self.clabel, False, False, 1)
        # separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox.pack_start(separator, False, False, 1)
        # # iconview
        self.ivbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.ivbox.set_homogeneous(True)
        if CAT_LAYOUT == 1:
            # self.hbox.add(self.ivbox)
            self.hbox.pack_start(self.ivbox, True, True, 1)
        elif CAT_LAYOUT == 2:
            self.cat_box.pack_start(self.ivbox, True, True, 1)
        elif CAT_LAYOUT == 3:
            self.cat_box.pack_start(self.ivbox, True, True, 1)
            self.cat_box.pack_start(self.cbox, False, False, 1)
            self.hbox.pack_start(self.cat_box, False, False, 1)
        # scrolled window
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.ivbox.pack_start(self.scrolledwindow, True, True, 0)
        # iconview - icon name comment exec terminal folder_path desktop_file_full_path
        self.liststore = Gtk.ListStore(Pixbuf, str, str, str, bool, str, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_tooltip_column(2)
        self.iconview.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.iconview.set_property("activate-on-single-click", True)
        self.iconview.set_name("myiconview")
        # self.iconview.set_columns(APP_COL)
        #
        target_entry = Gtk.TargetEntry.new('calculon', 1, 666)
        # self.DRAG_ACTION = Gdk.DragAction.MOVE
        self.DRAG_ACTION = Gdk.DragAction.COPY
        self._start_path = None
        self.iconview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [target_entry], self.DRAG_ACTION)
        self.iconview.enable_model_drag_dest([target_entry], self.DRAG_ACTION)
        self.iconview.connect("drag-data-get", self.on_drag_data_get)
        self.iconview.connect("drag-data-received", self.on_drag_data_received)
        #
        self.iconview.connect("item-activated", self.on_iv_item_activated)
        self.iconview.connect("button_press_event", self.mouse_event)
        self.scrolledwindow.add(self.iconview)
        # separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox.pack_start(separator, False, False, 1)
        # # search box
        self.scbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.scbox.set_homogeneous(True)
        #
        self.search_bar = Gtk.SearchBar()
        self.search_bar.set_search_mode(True)
        self.searchentry = Gtk.SearchEntry()
        self.searchentry.connect('icon-press', self.on_icon_press)
        self.searchentry.connect('activate', self.on_search_return)
        self.searchentry.set_name("mysearchentry")
        if LIVE_SEARCH == 1:
            self.searchentry.connect('changed', self.on_search)
        self.search_bar.connect_entry(self.searchentry)
        ###########
        # Get the correct children into the right variables
        main_box = self.search_bar.get_children()[0].get_children()[0]
        box1, box2, box3 = main_box.get_children()
        # 
        box2.props.hexpand = True
        box2.props.halign = Gtk.Align.FILL
        main_box.remove(box1)
        box3.props.hexpand = False
        ###########
        self.search_bar.add(self.searchentry)
        self.search_bar.set_show_close_button(False)
        self.search_bar.set_visible(True)
        self.search_bar.set_search_mode(True)
        self.scbox.pack_start(self.search_bar, False, True, 1)
        self.hbox.pack_start(self.scbox, False, True, 1)
        #
        # # the bookmark button
        self.btn_bookmark = None
        # the last category button pressed
        self._btn_toggled = None
        #
        self.event = Event()
        # self.thread_fifo = Thread(target=appThread, args=(self,self.event))
        # self.thread_fifo.start()
        # inhibit hiding
        self.not_hide = 0
        # # style
        if USE_CSS:
            style_provider=Gtk.CssProvider()
            style_provider.load_from_path("window.css")
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        # # populate the menu
        q.put_nowait("new")
        self.on_populate_menu()
        # #
        signal.signal(signal.SIGINT, self.sigtype_handler)
        signal.signal(signal.SIGTERM, self.sigtype_handler)
        # # populate categories
        self.bookmarks = []
        self.set_categories()
        # # monitors
        gdir1 = Gio.File.new_for_path(os.path.join(os.path.expanduser("~"), ".local/share/applications"))
        self.monitor1 = gdir1.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
        self.monitor1.connect("changed", self.directory_changed)
        #
        gdir2 = Gio.File.new_for_path("/usr/share/applications")
        self.monitor2 = gdir2.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
        self.monitor2.connect("changed", self.directory_changed)
        #
        gdir3 = Gio.File.new_for_path("/usr/local/share/applications")
        self.monitor3 = gdir3.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
        self.monitor3.connect("changed", self.directory_changed)
        #
        self.show_all()
        if START_HIDDEN == 1:
            # self.hide()
            self._hide()
        iconview_width = self.iconview.get_allocated_width()
        # self.iconview.set_item_width(int(iconview_width/(APP_COL*2)))
        self.iconview.set_item_width(int(APP_COL))
    
    def on_drag_data_get(self, widget, drag_context, data, info, time):
        #
        if self.get_cat_btn_name(self._btn_toggled) == "Bookmarks":
            selected_path = widget.get_selected_items()[0]
            self._start_path = selected_path
    
    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        _dest_path = widget.get_path_at_pos(x,y)
        #
        if _dest_path == None or self._start_path == None:
            return
        if _dest_path != self._start_path:
            _l = list(range(len(self.liststore)))
            _row1 = widget.get_item_row(self._start_path)
            _row2 = widget.get_item_row(_dest_path)
            _l.pop(_row2)
            if _row2 > _row1:
                _l.insert(_row1+1, _row2)
            elif _row2 < _row1:
                _l.insert(_row1, _row2)
            #
            self.liststore.reorder(_l)
            # reset
            self.bookmarks = []
            # rewrite the favorites file
            with open(os.path.join(main_dir, "favorites"), "w") as _f:
                for row in self.liststore:
                    _item = row[6]
                    _f.write(_item)
                    _f.write("\n")
                    self.bookmarks.append(_item)
        #
        self._start_path = None
        #
        return True
    
    # close when lost focus
    def on_lost_focus(self, w, e):
        if self.not_hide == 1:
            return
        self._hide()
        # self.hide()
        # self.iconify()
    
    def _hide(self):
        self.iconify()
        self.iconview.unselect_all()
        self.searchentry.delete_text(0,-1)
        # open bookmarks next time
        if USER_THEME == 0:
            if self._btn_toggled == self.btn_bookmark:
                return
            self.btn_bookmark.set_active(True)
            self.on_toggle_toggled(self.btn_bookmark, None)
        elif USER_THEME == 1:
            self._btn_toggled = self.btn_bookmark
            self.btn_bookmark.clicked()
            self.btn_bookmark.grab_focus()
            if USE_LABEL_CATEGORY == 1:
                self.clabel.set_label("Bookmarks")
    
    def on_search_return(self, widget):
        self.on_button_search(widget)
    
    # the label or the tooltip of the category button
    def get_cat_btn_name(self, btn):
        if btn.get_label() != None:
            return btn.get_label()
        elif btn.get_tooltip_text() != None:
            return btn.get_tooltip_text()
        else:
            return None
    
    def on_hide(self, e):
        if self.not_hide == 1:
            return
        self.iconview.unselect_all()
        self.searchentry.delete_text(0,-1)
        # open bookmarks next time
        if USER_THEME == 0:
            if self._btn_toggled == self.btn_bookmark:
                return
            self.btn_bookmark.set_active(True)
            self.on_toggle_toggled(self.btn_bookmark, None)
        elif USER_THEME == 1:
            self._btn_toggled = self.btn_bookmark
            self.btn_bookmark.clicked()
            self.btn_bookmark.grab_focus()
            if USE_LABEL_CATEGORY == 1:
                self.clabel.set_label("Bookmarks")
    
    def on_show(self, e):
        if WIN_POSITION != "":
            self.move(int(self.WX),int(self.WY))
    
    def _to_close(self, w=None, e=None):
        if w != None or e != None:
            return
        if not self.event.is_set():
            self.event.set()
        time.sleep(1)
        Gtk.main_quit()
        
    def on_populate_menu(self):
        self.thread_menu = Thread(target=menuThread, args=(app_dirs_user,app_dirs_system,q,self.event))
        self.thread_menu.start()
    
    def directory_changed(self, monitor, file1, file2, event):
        if (event == Gio.FileMonitorEvent.CREATED) or (event == Gio.FileMonitorEvent.DELETED):
            self.on_directory_changed(file1.get_path())
        
    def on_directory_changed(self, _path):
        try:
            if q.empty():
                q.put("new", timeout=0.001)
        except:
            pass
        #
        if not q.empty():
            if _path in self.bookmarks:
                self.bookmarks.remove(_path)
            with open(os.path.join(main_dir, "favorites"), "w") as _f:
                for el in self.bookmarks:
                    _f.write(el+"\n")
            # rebuild bookmarks
            self.populate_bookmarks_at_start()
            if USER_THEME == 1:
                self.btn_bookmark.clicked()
            #
            self.rebuild_menu()
            
    def rebuild_menu(self):
        # thread start
        self.on_populate_menu()
        #
        self.populate_bookmarks_at_start()
        _cat = ["Bookmarks", "Development", "Game", "Education", "Graphics", "Multimedia", "Network", "Office", "Utility", "Settings", "System", "Other"]
        for el in _cat:
            self.populate_category(el)
        # select bookmark
        self.populate_category("Bookmarks")
    
    # on iconview
    def mouse_event(self, iv, event):
        # bookmarks
        # right mouse button
        if event.button == 3:
            _path = iv.get_path_at_pos(event.x, event.y)
            if _path != None:
                _item = self.liststore[_path][6]
                # remove from bookmarks
                if _item in self.bookmarks:
                    if self.get_cat_btn_name(self._btn_toggled) != "Bookmarks":
                        return
                    self.not_hide = 1
                    dialog = ynDialog(self, "Delete from Bookmarks?", "Question")
                    response = dialog.run()
                    if response == Gtk.ResponseType.OK:
                        _content = None
                        try:
                            self.bookmarks.remove(_item)
                            with open(os.path.join(main_dir, "favorites"), "w") as _f:
                                for el in self.bookmarks:
                                    _f.write(el+"\n")
                            # rebuild bookmarks
                            self.populate_bookmarks_at_start()
                            self.populate_category("Bookmarks")
                        except Exception as E:
                            self.msg_simple("Error\n"+str(E))
                    #
                    dialog.destroy()
                    self.not_hide = 0
                # add to bookmarks
                else:
                    self.not_hide = 1
                    dialog = ynDialog(self, "Add to Bookmarks?", "Question")
                    response = dialog.run()
                    if response == Gtk.ResponseType.OK:
                        _content = None
                        try:
                            with open(os.path.join(main_dir, "favorites"), "a") as _f:
                                _f.write(_item)
                                _f.write("\n")
                            # rebuild bookmarks
                            self.populate_bookmarks_at_start()
                        except Exception as E:
                            self.msg_simple("Error\n"+str(E))
                    dialog.destroy()
                    self.not_hide = 0
        # central mouse button
        elif event.button == 2:
            self.not_hide = 1
            dialog = ynDialog(self, "Rebuild the menu?", "Question")
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.not_hide = 0
                # self.hide()
                self._hide()
                self.rebuild_menu()
            else:
                self.not_hide = 0
            dialog.destroy()
            self.show_all()
                
    # press esc to hide
    def on_key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Escape":
            # self.hide()
            self._hide()
    
    # clear icon pressed in the search entry
    def on_icon_press(self, w, p, e):
        self.liststore.clear()
    
    # application searching by pressing enter in the search entry
    def on_button_search(self, button=None):
        if len(self.searchentry.get_text()) < SEARCH_N:
            return
        else:
            if self._btn_toggled:
                if USER_THEME == 0:
                    self._btn_toggled.set_active(False)
                self._btn_toggled = None
            self.perform_searching(self.searchentry.get_text().lower())
        
    # application live searching in the search entry
    def on_search(self, _):
        if len(self.searchentry.get_text()) >= SEARCH_N:
            self.perform_searching(self.searchentry.get_text().lower())
        
    def perform_searching(self, _text):
        if USER_THEME == 1 and USE_LABEL_CATEGORY == 1:
            self.clabel.set_label("Searching...")
        _cat = ["Development", "Game", "Education", "Graphics", "Multimedia", "Network", "Office", "Utility", "Settings", "System", "Other"]
        _list = []
        # label - executable - icon - comment - path - terminal - file full path
        for cat_name in _cat:
            for el in globals()[cat_name]:
                if _text in el[0].lower() or _text in el[3].lower():
                    _list.append(el)
        #
        self.f_on_pop_iv(_list)
        
    def f_on_pop_iv(self, _list):
        self.liststore.clear()
        for el in _list:
            self.on_populate_category(el)
    
    # populate the main categories at start
    def set_categories(self):
        self._btn_toggled = None
        #
        _cat = ["Bookmarks", "Development", "Game", "Education", "Graphics", "Multimedia", "Network", "Office", "Utility", "Settings", "System", "Other"]
        _icon = ["Bookmark.svg", "Development.svg", "Game.svg", "Education.svg", "Graphics.svg", "Multimedia.svg", "Network.svg", "Office.svg", "Utility.svg", "Settings.svg", "System.svg", "Other.svg",]
        for i,el in enumerate(_cat):
            if USER_THEME == 1:
                _btn = Gtk.Button()
                _btn.connect('clicked', self.on_toggle_toggled)
                _btn.connect('focus-in-event', self.on_toggle_toggled)
            elif USER_THEME == 0:
                _btn = Gtk.ToggleButton()
                _btn.set_can_focus(False)
                _btn.connect('button-release-event', self.on_toggle_toggled)
            _btn.set_name("mybutton")
            #
            pix = Pixbuf.new_from_file_at_size(icon_dir+"/"+_icon[i], BTN_ICON_SIZE, BTN_ICON_SIZE)
            _image = Gtk.Image.new_from_pixbuf(pix)
            _btn.set_image(_image)
            _btn.set_image_position(Gtk.PositionType.TOP)
            _btn.set_always_show_image(True)
            _btn.set_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
            if BTN_USE_LABEL:
                _btn.set_label(el)
                if CAT_LAYOUT == 2 or CAT_LAYOUT == 3:
                    _btn.set_property("image-position",Gtk.PositionType.LEFT)
                    # _btn.set_property("yalign",0.0)
                    _btn.set_property("xalign",0.0)
            else:
                _btn.set_tooltip_text(el)
            #
            self.cbox.add(_btn)
            #
            if i == 0:
                if USER_THEME == 0:
                    _btn.set_active(True)
                self._btn_toggled = _btn
                self.btn_bookmark = _btn
                self.populate_bookmarks_at_start()
                self.populate_category(el)
                if USER_THEME == 1 and USE_LABEL_CATEGORY == 1:
                    self.clabel.set_label("Bookmarks")
    
    def on_toggle_toggled(self, btn, e=None):
        if USER_THEME == 1:
            self.populate_category(self.get_cat_btn_name(btn))
            self._btn_toggled = btn
            if USE_LABEL_CATEGORY == 1:
                self.clabel.set_label(self.get_cat_btn_name(btn))
            return
        if self._btn_toggled:
            if btn == self._btn_toggled:
                if e:
                    if e.button == 1:
                        btn.clicked()
                    else:
                        btn.set_active(True)
                return
            else:
                self._btn_toggled.set_active(False)
                if e and e.button != 1:
                    btn.set_active(True)
        #
        self.populate_category(self.get_cat_btn_name(btn))
        self._btn_toggled = btn
    
    def populate_bookmarks_at_start(self):
        _content = None
        with open(os.path.join(main_dir, "favorites"), "r") as _f:
            _content = _f.readlines()
        #
        self.bookmarks = []
        for el in _content:
            if el == "\n" or el == "" or el == None:
                continue
            self.bookmarks.append(el.strip("\n"))
        #
        self.populate_bookmarks()
    
    def populate_bookmarks(self):
        global Bookmarks
        Bookmarks = []
        for eel in self.bookmarks:
            el = pop_menu_item.getMenu(eel).list
            Bookmarks.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        
    def populate_category(self, cat_name):
        self.liststore.clear()
        #
        if globals()[cat_name] == []:
            return
        for el in globals()[cat_name]:
            self.on_populate_category(el)
            
    def on_populate_category(self, el):
        pixbuf = None
        # label - executable - icon - comment - path - terminal - file full path
        if not os.path.exists(el[2]):
            try:
                pixbuf = Gtk.IconTheme().load_icon(el[2], ICON_SIZE, Gtk.IconLookupFlags.FORCE_SVG)
                if pixbuf.get_width() != ICON_SIZE or pixbuf.get_height() != ICON_SIZE:
                    pixbuf = pixbuf.scale_simple(ICON_SIZE,ICON_SIZE,2)#GdkPixbuf.InterpType.BILINEAR)
            except:
                pixbuf = None
        else:
            try:
                pixbuf = Pixbuf.new_from_file_at_scale(el[2], ICON_SIZE, ICON_SIZE, 1)
            except:
                pixbuf = None
        if pixbuf == None:
            try:
                pixbuf = Gtk.IconTheme().load_icon("binary", ICON_SIZE, Gtk.IconLookupFlags.FORCE_SVG)
                if pixbuf.get_width() != ICON_SIZE or pixbuf.get_height() != ICON_SIZE:
                    pixbuf = pixbuf.scale_simple(ICON_SIZE,ICON_SIZE,2)#GdkPixbuf.InterpType.BILINEAR)
            except:
                pixbuf = Pixbuf.new_from_file_at_scale(icon_dir+"/none.svg", ICON_SIZE, ICON_SIZE, 1)
        # icon name comment exec
        self.liststore.append([ pixbuf, el[0], el[3] or None, el[1], el[5], el[4], el[6] ])
    
    # execute a command
    def execute_command(self, _cmd):
        try:
            subprocess.Popen(_cmd, shell=True)
        except Exception as E:
            self.msg_simple("Error!\n{}".format(str(E)))
    
    # launch a program
    def on_iv_item_activated(self, iconview, widget):
        self.not_hide = 1
        if self.iconview.get_selected_items() != None:
            rrow = self.iconview.get_selected_items()[0]
        #
        _to_exec = self.liststore[rrow][3]
        # check the exec is in path
        if APP_EXISTS == 1:
            if not shutil.which(_to_exec):
                dialog = ynDialog(self, "The exec\n{}\ncannot be found.\n Does execute it anyway?".format(_to_exec), "Question")
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    dialog.destroy()
                elif response == Gtk.ResponseType.CANCEL:
                    dialog.destroy()
                    self.not_hide = 0
                    return
        #
        _need_terminal = self.liststore[rrow][4]
        _item_path = self.liststore[rrow][5]
        #
        if _need_terminal:
            if self.TERMINAL == "":
                try:
                    self.TERMINAL = os.environ['TERMINAL']
                except KeyError:
                    pass
                #
                if not self.TERMINAL or not shutil.which(self.TERMINAL):
                    self.msg_simple("Terminal not found or not setted.")
                    self.not_hide = 0
                    return
            #
            try:
                if _item_path:
                    _cmd = ['cd {} && {} -e {}'.format(str(_item_path),self.TERMINAL,str(_to_exec))]
                    self.execute_command(_cmd)
                else:
                    _cmd = ['{} -e {}'.format(self.TERMINAL,str(_to_exec))]
                    self.execute_command(_cmd)
                self.not_hide = 0
                # self.hide()
                self._hide()
            except Exception as E:
                self.msg_simple("Error!\n{}".format(str(E)))
                
        else:
            try:
                if _item_path:
                    _cmd = ['cd {} && {}'.format(str(_item_path),str(_to_exec))]
                    self.execute_command(_cmd)
                else:
                    _cmd = [str(_to_exec)]
                    self.execute_command(_cmd)
                self.not_hide = 0
                # self.hide()
                self._hide()
            except Exception as E:
                self.msg_simple("Error!\n{}".format(str(E)))
        self.not_hide = 0
    
    def sigtype_handler(self, sig, frame):
        if sig == signal.SIGINT or sig == signal.SIGTERM:
            self._to_close()
    
    # only yes message dialog
    def msg_simple(self, mmessage):
        messagedialog2 = Gtk.MessageDialog(parent=self,
                              modal=True,
                              message_type=Gtk.MessageType.WARNING,
                              buttons=Gtk.ButtonsType.OK,
                              text=mmessage)
        messagedialog2.connect("response", self.dialog_response2)
        messagedialog2.show()
    
    def dialog_response2(self, messagedialog2, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog2.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog2.destroy()


# class appThread(Thread):
    
    # def __init__(self, win, event):
        # self.win = win
        # self.event = event
        # self.run()
    
    # def run(self):
        # is_true = 1
        # if is_true == 0:
            # return
        # #
        # while is_true:
            # with open(FIFO) as fifo:
                # for line in fifo:
                    # if line.strip() == "__toggle":
                        # if not self.win.is_visible():
                            # self.win.show_all()
                        # else:
                            # self.win.hide()
                            # self.win._hide()
                    # elif line.strip() == "__open":
                        # self.win.show_all()
                    # elif line.strip() == "__close":
                        # self.win.hide()
                    # elif line.strip() == "__exit":
                        # if not self.event.is_set():
                            # os.kill(os.getpid(), signal.SIGTERM)
                            # self.event.set()
                        # #
                        # self.win.destroy()
                        # is_true = 0


class menuThread(Thread):
    
    def __init__(self, app_dirs_user, app_dirs_system,q,event):
        self.app_dirs_user = app_dirs_user
        self.app_dirs_system = app_dirs_system
        self.q = q
        self.event = event
        self.run()
    
    def run(self):
        if self.event.is_set():
            return
        if not self.q.empty():
            self.q.get_nowait()
            self.on_pop_menu()
        
    # populate the menu
    def on_pop_menu(self):
        #
        global Development
        Development = []
        global Education
        Education = []
        global Game
        Game = []
        global Graphics
        Graphics = []
        global Multimedia
        Multimedia = []
        global Network
        Network = []
        global Office
        Office = []
        global Settings
        Settings = []
        global System
        System = []
        global Utility
        Utility = []
        global Other
        Other = []
        #
        menu_app = pop_menu.getMenu(self.app_dirs_user, self.app_dirs_system, 1)
        menu = menu_app.list_one
        for el in menu:
            cat = el[1]
            if cat == "Multimedia":
                # label - executable - icon - comment - path - terminal - file full path
                Multimedia.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Development":
                Development.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Education":
                Education.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Game":
                Game.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Graphics":
                Graphics.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Network":
                Network.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Office":
                Office.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Settings":
                Settings.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "System":
                System.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            elif cat == "Utility":
                Utility.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
            else:
                Other.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        #
        return


class ynDialog(Gtk.Dialog):
    def __init__(self, parent, _title1, _type):
        super().__init__(title=_type, transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        #
        self.set_default_size(150, 100)
        label = Gtk.Label(label=_title1)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


if __name__ == '__main__':
    _M = MainWindow()
    # _M.show_all()
    Gtk.main()
