#@+leo-ver=4-thin
#@+node:eric.20090722212922.2759:@shadow tooltip.py
# Stolen from: http://tkinter.unpythonic.net/wiki/ToolTip
"""
Michael Lange <klappnase at 8ung dot at>

The ToolTip class provides a flexible tooltip widget for Tkinter; it is
based on IDLE's ToolTip module which unfortunately seems to be broken
(at least the version I saw).

INITIALIZATION OPTIONS:

    anchor
        where the text should be positioned inside the widget; must be one
        of "n", "s", "e", "w", "nw" and so on; default is "center"
    bd
        borderwidth of the widget; default is 1 (NOTE: don't
        use "borderwidth" here)
    bg
        background color to use for the widget; default is
        "lightyellow" (NOTE: don't use "background")
    delay
        time in ms that it takes for the widget to appear on the
        screen when the mouse pointer has entered the parent
        widget; default is 1500
    fg
        foreground (i.e. text) color to use; default is "black"
        (NOTE: don't use "foreground")
    follow_mouse
        if set to 1 the tooltip will follow the mouse pointer
        instead of being displayed outside of the parent widget;
        this may be useful if you want to use tooltips for
        large widgets like listboxes or canvases; default is 0
    font
        font to use for the widget; default is system specific
    justify
        how multiple lines of text will be aligned, must be
        "left", "right" or "center"; default is "left"
    padx
        extra space added to the left and right within the widget; 
        default is 4
    pady
        extra space above and below the text; default is 2
    relief
        one of "flat", "ridge", "groove", "raised", "sunken" or
        "solid"; default is "solid"
    state
        must be "normal" or "disabled"; if set to "disabled" the
        tooltip will not appear; default is "normal"
    text
        the text that is displayed inside the widget
    textvariable
        if set to an instance of Tkinter.StringVar() the variable's
        value will be used as text for the widget
    width
        width of the widget; the default is 0, which means that
        "wraplength" will be used to limit the widgets width
    wraplength
        limits the number of characters in each line; default is 150

WIDGET METHODS:

    configure(``**opts``)
        change one or more of the widget's options as described
        above; the changes will take effect the next time the
        tooltip shows up; NOTE: follow_mouse cannot be changed
        after widget initialization

Other widget methods that might be useful if you want to subclass ToolTip:

    enter
        callback when the mouse pointer enters the parent widget
    leave
        called when the mouse pointer leaves the parent widget
    motion
        is called when the mouse pointer moves inside the
        parent widget if follow_mouse is set to 1 and the
        tooltip has shown up to continually update the
        coordinates of the tooltip window
    coords
        calculates the screen coordinates of the tooltip window
    create_contents
        creates the contents of the tooltip window (by default a Tkinter.Label)
"""

__all__ = ['ToolTip']

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

#@+others
#@+node:eric.20090722212922.2761:class ToolTip
class ToolTip:
    """A Tooltip widget for Tkinter.
    """
    #@    @+others
    #@+node:eric.20090723160216.3598:_defaults
    _defaults = {
        'anchor': 'center',
        'bd': 1,
        'bg': 'lightyellow',
        'fg': 'black',
        'follow_mouse': 0,
        'font': None,
        'justify': 'left',
        'padx': 4,
        'pady': 2,
        'relief': 'solid',
        'state': 'normal',
        'textvariable': None,
        'width': 0,
        'wraplength': 150
    }

    #@-node:eric.20090723160216.3598:_defaults
    #@+node:eric.20090722212922.2762:__init__
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = self._defaults.copy()
        self._opts.update({'delay': delay, 'text': text})
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1


    #@-node:eric.20090722212922.2762:__init__
    #@+node:eric.20090722212922.2763:configure
    def configure(self, **opts):
        """Update tooltip configuration.
        """
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:
                raise KeyError('Unknown option: "%s"' % key)

    #@-node:eric.20090722212922.2763:configure
    #@+node:eric.20090723212423.3630:Event handlers
    ### Event handlers
    #@+node:eric.20090722212922.2764:enter
    def enter(self, event=None):
        """Called when mouse pointer enters the parent widget.
        """
        self._schedule()


    #@-node:eric.20090722212922.2764:enter
    #@+node:eric.20090722212922.2765:leave
    def leave(self, event=None):
        """Called when mouse pointer leaves the parent widget.
        """
        self._unschedule()
        self._hide()


    #@-node:eric.20090722212922.2765:leave
    #@+node:eric.20090722212922.2766:motion
    def motion(self, event=None):
        """Called when mouse pointer moves inside the tooltip region.
        """
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    #@-node:eric.20090722212922.2766:motion
    #@-node:eric.20090723212423.3630:Event handlers
    #@+node:eric.20090723212423.3629:Helpers
    ### Helpers
    #@+node:eric.20090722212922.2767:_schedule
    def _schedule(self):
        """Schedule the tooltip for display after ``delay`` milliseconds.
        """
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)


    #@-node:eric.20090722212922.2767:_schedule
    #@+node:eric.20090722212922.2768:_unschedule
    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)


    #@-node:eric.20090722212922.2768:_unschedule
    #@+node:eric.20090722212922.2769:_show
    def _show(self):
        """Show the tooltip.
        """
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = tk.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle",
                           "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()


    #@-node:eric.20090722212922.2769:_show
    #@+node:eric.20090722212922.2770:_hide
    def _hide(self):
        """Hide the tooltip.
        """
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()


    #@-node:eric.20090722212922.2770:_hide
    #@-node:eric.20090723212423.3629:Helpers
    #@+node:eric.20090722212922.2771:coords
    ##these methods might be overridden in derived classes:##

    def coords(self):
        """Return the (x, y) coordinates of the tip window.
        """
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the
        # tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    #@-node:eric.20090722212922.2771:coords
    #@+node:eric.20090722212922.2772:create_contents
    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = tk.Label(self._tipwindow, **opts)
        label.pack()

    #@-node:eric.20090722212922.2772:create_contents
    #@-others
#@-node:eric.20090722212922.2761:class ToolTip
#@-others

#@-node:eric.20090722212922.2759:@shadow tooltip.py
#@-leo