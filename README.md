# gmenu
Menu application that lists the programs installed.

This program is a standalone graphical menu application
that lists all the programs installed, through their desktop files.

Required:
- python3
- gtk3
- Xorg or Wayland
- xdotool and xprop or wlrctl

This program can be open and closed using two bash scripts:
- xorg: xgmenu_toggle.sh (toggles show/hide); xgmenu_close.sh (closes the program)
- wayland: wgmenu_toggle.sh (toggles show/hide); wgmenu_close.sh (closes the program)
The Esc key can be used to hide the program.
To launch it the first time, one of gmenu.sh and (x/w)gmenu_toggle.sh 
must be used for the scripts above to work properly.

Some options can be setted in the menusettings.py file.

This program starts in hidden state, unless the related option in the config file is changed.

Features:
- indipendent from anything else: just execute and use it by using the scripts above;
- Bookmarks: can be reordered;
- searching entry: search applications by name and in the comments;
                   live search too;
- css style file;
- three layouts: categories at top or at left or at right;
- categories and applications icon size support;
- fixed position or centered (if supported by the window manager);
- update the menu in background automatically when needed (e.g. after a new installation or disinstallation);
- right mouse click on an item to bookmark it (also for removing it from the favourite category)
- middle mouse click (on an item) to force a menu rebuild;
- the program closes (hide state) after losing focus.

The size of the main window must be setted manually;
the number of the columns in the view depends on the column size setted
in the config file (this is the more precise way at the moment; default disabled).

The terminal needed by non-graphical applications must support the '-e' option,
and its name must be setted in the config file.

Known issues:
- the bookmarks sometimes cannot be reordered.

