===============================================================
tovid manual
===============================================================


Description
===============================================================================

**tovid** is a command-line tool for creating DVDs. It can encode your video
files to DVD-compliant MPEG format, generate simple or complex DVD menus,
author and burn a ready-to-watch DVD, with just a few shell commands. A
graphical interface is also provided to make the process even easier.

**NOTE**: As of tovid 0.32, this is the only manual page provided by tovid.
There is now a single executable frontend to all functionality in the suite, so
if you were expecting to find manpages for **todisc**, **idvid**, **makemenu**
and their kin, they can all be found in the **tovid** manpage you are reading now.

And yes, this makes for a pretty large manual page. If you are viewing this
manpage from the command-line **man** utility, which normally pages through the
**less** utility, you can skip to a section by searching with the **/** key,
followed by a **^** to match the given section name. For example, to skip to
the **mpg** command, type **/^Command:mpg**. See :manpage:`less(1)` for more on how
to navigate.

Usage
===============================================================================

::

 tovid COMMAND [OPTIONS]

Where *COMMAND* is one of the following:

    gui
        Start the tovid GUI (was **todiscgui**. See :ref:`command-gui`)
    disc
        Create a DVD with menus (was **todisc**. See :ref:`command-disc`)
    mpg
        Encode videos to MPEG format (was **tovid**. See :ref:`command-mpg`)
    id
        Identify one or more video files (was **idvid**. See :ref:`command-id`)
    menu
        Create an MPEG menu (was **makemenu**. See :ref:`command-menu`)
    xml
        Create (S)VCD or DVD .xml file (was **makexml**. See :ref:`command-xml`)
    dvd
        Author and/or burn a DVD (was **makedvd**. See :ref:`command-dvd`)
    vcd
        Author and/or burn a VCD (was **makevcd**. See :ref:`command-vcd`)
    postproc
        Post-process an MPEG video file (was **postproc**. See :ref:`command-postproc`)

The *OPTIONS* differ for each command; run **tovid <command>** with no
further arguments to get help on a command, and what options it expects.

Configuration
===============================================================================

Two configuration files are created the first time you run tovid:

``~/.tovid/preferences``
    Defines working directory for all scripts.
    In addition you can define the output directory for makempg here.
``~/.tovid/tovid.config``
    Includes command-line options that should always be passed to
    makempg.

    Edit these files if you wish to change your configuration.

The following environment variables are also honoured:

``TOVID_WORKING_DIR``
    working directory for all scripts
``TOVID_OUTPUT_DIR``
    output directory for the makempg script


.. _command-gui:

Command:gui
===============================================================================

**tovid gui** starts the graphical user interface (GUI) for tovid. This is
the easiest way to start creating DVDs with tovid. At this time, there are no
additional command-line options; the GUI controls take care of everything,
and all help is integrated in the form of tooltips.  You can also see
:ref:`command-disc` for more detail about the options.  Note: one limitation of
the gui at present is that it does not do multiple titlesets (though it will do
chapter menus).  Use the **tovid disc** command (below) for titlesets.


.. _command-disc:

Command:disc
===============================================================================

**tovid disc** creates a DVD file-system with menus, from a list of multimedia
video files and their titles.  As this is a low level script it is the easiest
command line program for creating a DVD from start to finish, including
automatically converting non-compliant videos and prompting to burn at
completion.  It does animated menus, static thumbnail menus and text only
menus.  In addition, it can do slideshows, using images as input, and combine
slideshows with videos.  It supports sub-menus for chapter breaks, configurable
menu style, animated backgrounds and transparency effects.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid disc [OPTIONS] \
   -files <file list> -titles <title list>
   -out OUT_PREFIX

For example::

 tovid disc -files File1.mpg File2.mpg File3.mpg \
   -titles "Episode 1" "Episode 2" "Episode 3" \
   -out Season_one

The number of **-files** and **-titles** must be equal, though if you do not
include any titles **tovid disc** will use the basename of the included files
as titles.  If you are doing a slideshow or multiple slideshows, use
**-slides** rather than **-files** for passing in the images.  You may use
-files and -slides more than once to create an ordering in a mixed
slideshows/videos menu.  See :ref:`usage-slideshows` under usage below.

If the input files are not mpeg, you will have the option to auto-encode them.


Display arrangements
-------------------------------------------------------------------------------

At present there are 2 display arrangements or "templates":

A. (Default)
    Thumbs will be centred, and as large as space restraints allow.

B. **-showcase** IMAGE|VIDEO
    Produces an arrangement with small buttons on
    the side and the showcase image/video in the centre.  If no IMAGE or VIDEO
    argument is supplied, the central thumb will be omitted.

    Note: **-textmenu**, **-quick-menu** and **-switched-menus** are all types
    of showcase style menus.  See descriptions in the :ref:`menu-style` section.

The **-titles** arguments should be double or single quoted, or have the spaces
backslash-escaped. Special characters (like ", !, \*, &, ?) may need to be
backslash-escaped.  To include a quoted string within a title, backslash-escape
the quotes.  These titles are used for labelling thumbnails on the main menu,
and for the submenu title for that video.  ( see also **-submenu-titles** )

The **-showcase** styles can use longer titles than the default arrangement.
With a showcase style, use: **-showcase-titles-align west** to give more space
for the title, or use **-showcase-titles-align east** to allow titles of more
than one line.

The default style can only show about 16 characters (depending on the number
of thumbs, and what **-titles-font** and **-titles-fontsize** is being used).
If your titles are too long to fit in the label area, you may try using
sub-menus, which can display longer titles, for example::

 $ tovid disc -submenus \
      -files file1.mpg file2.mpg ... \
      -titles "Short 1" "Short 2" \
      -submenu-titles "Long Title One" "Long Title Two" \
      -out foo

The **-align** argument will position both titles and thumbs either south,
north east, west, southwest, northwest, southeast, northeast, subject to
certain constraints of each arrangement.


.. _usage-titlesets:

Titlesets
-------------------------------------------------------------------------------

A word should be mentioned here about titlesets, which is really just a
hierarchy of menus.  You need to use titlesets, for example, if you have videos
of different resolutions, or otherwise want to arrange videos on separate menus.
If you want to have titlesets you need to put all the options for each titleset
menu you would like to have between **-titleset** and **-end-titleset** options.

Additionally, for the main menu (the opening menu that will let you jump to
each titleset), you need to put options between **-vmgm** and **-end-vmgm**.
You do not use **-files** for the opening menu options (**-vmgm**), but you
will need as many TITLES after **-titles** as you have menus.

Any options outside the **-titleset** **-end-titleset** and **-vmgm**
**-end-vmgm** areas will be general options applying to every titleset.
If a general option is duplicated inside a **-titleset** or **-vmgm** area, the
general option will be overridden.

Note: you do not need titlesets for a single menu with chapter break menus, for
that just use **-submenus** or **-ani-submenus**

Example of using **tovid disc** with titlesets::

 $ tovid disc -static -out MY_DVD \
   \
   -titleset -files 1.mpg 2.mpg 3.mpg \
   -titles "Title One" "Title Two" "Title Three" \
   -end-titleset \
   \
   -titleset -files 4.mpg 5.mpg \
   -titles "Title Four" "Title Five" \
   -background foo.jpg \
   -showcase bar.png \
   -end-titleset \
   \
   -vmgm \
   -titles "Season One" "Season Two" \
   -background bg.jpg \
   -bgaudio foo.mp3 \
   -titles-fontsize 20 \
   -end-vmgm

See also **-titleset** and **-vmgm**


.. _usage-slideshows:

Slideshows
-------------------------------------------------------------------------------

You can also use **tovid disc** to make slideshows.  This can either be a single
slideshow, or multiple slideshows on the same menu.
Remember to use **-slides** rather than **-files** for passing in the
images.  Images can be any filetype that imagemagick supports: for example
JPEG, PNG, GIF, TGA BMP etc.  For a single slideshow do not use **-titles**:
use -menu-title to set the slideshow title.

For a single slideshow the default is an animated menu that transitions from
slide to slide.  The default transition type is 'crossfade', which fades each
slide into the next and loops back to the first slide at the end.  If instead
you use **-static**, then a static 'polaroid stack' menu of all the slides is
created, with a single spumux'ed button for navigating with the enter key.  You
may have to experiment to find out which DVD remote button advances the slides.
Try the 'next chapter'(skip ?) button and the play or enter buttons.
If you want to limit the number of slides in the menu to a subset of all files
entered with **-slides**, then use **-menu-slide-total** INT.  Be sure to use
a long enough audio file for **-bgaudio** or set **-menu-length** so the menu
is long enough to support the slides plus transitions.

You can also put multiple slideshows on one menu.  To do this, use
**-slides IMAGES** for each slideshow desired.  You can even mix videos
with slideshows by using **-files** **-slides** **-titles** multiple times.

Example of a single slideshow with an animated menu with transitions::

 $ tovid disc -menu-title "Autumn in Toronto" -slides images/*.jpg \
    -menu-slide-total 20 -slide-transition crossfade -bgaudio slideshow.wav \
    -out myslideshow

Example of multiple slideshows on one menu::

 $ tovid disc -menu-title "Autumn in Toronto" \
   -slides photos/september/*.jpg \
   -slides photos/october/*.jpg \
   -slides photos/november/*.jpg \
   -tile3x1 -rotate -5 5 -5 -align center \
   -bgaudio background.wav \
   -out myslideshow

Example of mixed videos and slideshows::

 $ tovid disc -menu-title "Autumn in Toronto" \
   -files fall_fair.mov \
   -slides  photos/september/*.jpg \
   -files harvest.mpg \
   -slides photos/october/*.jpg \
   -titles "Fall Fair" "September" "Harvest" "October" \
   -background autumn.png \
   -bgaudio bg.mp3 \
   -out myslideshow

See the other slideshow options in the :ref:`usage-slideshows` options section.

Encoding options
-------------------------------------------------------------------------------

These are options for reencoding your non-compliant videos.  They are passed
directly to the **tovid mpg** command which is invoked by **tovid disc** when
non-compliant files are found.  For details, see the :ref:`command-mpg` section.
Here is a list of possible options you can pass:

**-config**, **-ntscfilm**, **-dvd-vcd**, **-half-dvd**, **-kvcd**,
**-kvcdx3**, **-kvcdx3a**, **-kdvd**, **-bdvd**, **-704**, **-normalize**,
**-amplitude**, **-overwrite**, **-panavision**, **-force**, **-fps**,
**-vbitrate**, **-quality**, **-safe**, **-crop**, **-filters**,
**-abitrate**, **-priority**, **-deinterlace**, **-progressive**,
**-interlaced**, **-interlaced_bf**, **-type**, **-fit**, **-discsize**,
**-parallel**, **-mkvsub**, **-autosubs**, **-subtitles**, **-update**, \
**-mplayeropts**, **-audiotrack**, **-downmix**, **-ffmpeg**, **-nofifo**,
**-from-gui**, **-slice**, **-async**, **-quiet**,
**-fake**, **-keepfiles**


Basic options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-keep-files**, **-keepfiles**
    Keep all intermediate/temporary files (helps with debugging)

**-ntsc**
    720x480 output, compatible with NTSC standard (default)

**-pal**
    720x576 output, compatible with PAL standard

**-submenus**
    Create a sub-menu with chapters for each video (default: no sub-menus)

**-ani-submenus**
    Create an animated sub-menu with chapters for each video (default: not
    animated)

**-no-menu | -nomenu**
    With this option todisc will just create a DVD file system, ready for
    burning, with NO MENU, just the supplied video files.  These do not need
    to be compliant, as non-compliant files will be encoded as usual.  Each
    video will be a chapter unless **-chapters** OPTION is passed.  The
    **-chapters** option is a number indicating the chapter interval in
    minutes, or a HH:MM:SS string indicating chapter points.  See **-chapters**


.. _menu-style:

Basic menu style options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-showcase** IMAGE|VIDEO
    If used without an argument, use showcase style without a central thumb.
    This is a different arrangement of images for the menu: small thumbnails
    go at left (and right) side of screen, with a larger image in the centre.
    Maximum of 10 videos.  If the provided argument is a video file, the
    central thumb will be animated.  Pick a file of correct aspect ratio:
    i.e. it should still look good when resized to 720x480 (PAL 720x576),
    then resized to proper aspect ratio.

**-textmenu**, **-text-menu** NUM
    If used without an argument, create a textmenu out of the supplied titles
    The optional argument specifies how many titles are in the 1st column,
    i.e. giving 4 titles and using **-textmenu 2** would make 2 columns of 2
    titles. The default is to put all titles up to 13 in the first column
    before starting a second column.  Maximum: 2 columns and 26 titles.
    Note that column 2 titles are aligned to the right.
    If no video files for either **-background** or **-showcase** are supplied,
    the menu will be static.

**-quick-menu**
    (Note: unfortunately ffmpeg's 'vhooks' have been removed, so this
    option may not be available for you depending on your ffmpeg version)
    This will make a very quick  menu by using ffmpeg instead of imagemagick.
    There are two choices: you can either use **-showcase IMAGE|VIDEO** or
    **-background VIDEO**.  There are no fancy effects like **-wave**
    or **-rotate** available for it, but it is extremely fast.  It will be a
    text-menu style of menu, with no video thumbs, and a central showcase
    IMAGE (static) | VIDEO (animated).  See **-bg-color** if you are not using
    a **-background** and want to change the default black.

    Specifying the IMAGE|VIDEO argument to **-showcase** is mandatory for this
    style of menu, unless used in conjunction with **-switched-menus**
    in which case the videos passed with **-files** automatically become the
    showcase videos.  If this is used in combination with **-switched-menus**
    it can really speed up an otherwise time consuming process.

    Example::

        -quick-menu -showcase /home/robert/showcase.mpg

    See **-switched-menus** for example of making switched menus with
    **-quick-menu**

**-bg-color** | **-bg-colour**
    The color to use for the menu background. (default: ntsc-safe black)
    Note: use a color a great deal darker than you want, as it appears quite
    a bit lighter in the video version.  You can use hexadecimal ('#ffac5f')
    or named colors notation.

**-submenu-bg-color** | **-submenu-bg-colour**
    The color to use as background for the  submenu(s).
    (default: ntsc-safe black)  See **-bg-color**

**-use-makemenu**
    This will use **tovid menu** to create a menu with the provided titles.

**-static**
    Main menu will just be static thumbs (not animated) (default: animated)

**-background** IMAGE|VIDEO
    Menu background.  This can be a image file or an video file.  If it is a
    video file the background will be animated.  Pick a file of correct aspect
    ratio: i.e. it should still look good when resized to 720x480 (PAL 720x576)

**-submenu-background** IMAGE
    Submenu background.  This can be only be an image file.  Pick a file of
    correct aspect ratio: i.e. it should still look good when resized to
    720x480 (PAL 720x576)

**-menu-title**
    Title for the root menu - may be longer than thumbnail labels
    Also if you use \n in the title, you can use multi line titles, but you
    would need to adjust **-menu-fontsize** to something smaller than default
    for example::

        $ tovid disc ... -menu-title "A\nMultilined\nTitle" -menu-fontsize 24

**-menu-font** FONT
    Font to use for titles, either by ImageMagick font name (ex., "Arial") or
    explicit pathname (ex., "/full/path/to/arial.ttf"). To see a complete
    list of acceptable ImageMagick font names, run **convert -list type**, and
    refer to the leftmost column

**-menu-fontsize**
    Font size for main menu - best to **-preview** if you use this

**-submenu-font**
    Font to use for the sub-menu main titles.  See **-menu-font**

**-submenu-fontsize**
    Font size for the sub-menu main titles

**-menu-fade** ['BACKGROUND DURATION']
    Fade the menu in and out The background will fade in first, then title (and
    mist if called for), then the menu thumbs.  The fadeout is in reverse
    order.  'BACKGROUND DURATION' is an integer denoting the amount of time the
    background will play before the menu begins to fade in.  This can allow you
    to do a 'transition' to the menu: if you supply a **-background VIDEO** it
    will play for the indicated time before the menu fades in.  Leave the
    optional argument empty (just **-menu-fade**) to get the default behavior
    of showing the background for 1 second before fading the menu in.  To
    disable the fadeout portion, use '**-loop** inf'.  See also:
    **-transition-to-menu** and **-loop**

**-transition-to-menu**
    This option goes with the **-menu-fade** option above, which must be
    enabled for it to have effect.  It is a convenience option for animated
    backgrounds: the background will become static at the exact point the
    thumbs finish fading in. This menu does not loop unless you pass
    **-loop VALUE**.  See also: **-loop**

**-bgaudio**, **-bg-audio** FILE
    An file containing audio for the main menu background.  For static menus
    the default is to use 20 seconds of audio.  You can change this using the
    **-menu-length** option.

**-submenu-audio** FILE(S)
    List of files for sub-menu audio backgrounds. If one file is given, then
    it will be used for all sub-menus.  Otherwise the number given must equal
    the number of submenus, though the keyword "none" in this list may be used for
    silence.  See also **-submenu-length**

**-titleset** . . . **-end-titleset**
    If you have more than one titleset, put options for each titleset between
    **-titleset** and **-end-titleset**.  A separate menu will be created that
    can be accessed from the main menu (VMGM).  You can create this main menu
    using the **-vmgm** **-end-vmgm** options.  See **-vmgm** below and
    :ref:`usage-titlesets` under the **Usage** section.

**-vmgm** . . . **-end-vmgm**
    The VMGM menu is the root menu when you use titlesets.
    Put your VMGM menu options between **-vmgm** and **-end-vmgm**.
    You only need **-titles** "Titleset One title"  "Titleset Two title"
    . . . , and not **-files**.
    Any other options can be used, but the  menu will be a textmenu style by
    default.  **Hint**: use **-showcase** IMAGE/VIDEO to create a fancier
    VMGM menu.

**-no-vmgm-menu** | **-no-vmgm**
    This will skip the creation of a VMGM ( root menu ) for titlesets. The DVD
    will start with the first titleset.  You can not use this option unless also
    using **-quick-nav** as you would not have a way to get to other titlesets.

**-skip-vmgm**
    Start DVD from the first titleset instead of the VMGM ( root ) menu.

**-switched-menus**
    This will make a "switched menu": there will be a central image where the
    showcase image would go, and text menu titles along the menu edge where
    textmenu titles go.  As you select a video title with the down or up arrow
    on your DVD remote, the image in the centre will change to the image or
    video made from that selected video. Do not use **-showcase** IMAGE/VIDEO
    with this option.

    This can be a time consuming process for making animated menus as you need
    to make a separate menu for each video provided with **-files**.  The
    process can be greatly sped up by using **-quick-menu** in conjunction with
    this, though you will lose fancy options like **-rotate** and **-wave**.

    Example for using with **-quick-menu**::

        -switched-menus -quick-menu


Thumbnail style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-thumb-shape** normal|oval|vignette|plectrum|arch|spiral|blob|star|flare
    Apply a shaped transparency mask to thumbnail videos.
    These "feathered" shapes look best against a plain background (or used
    in conjunction with **-thumb-mist** [COLOR]).  For this rectangular
    semi-transparent misted background for each thumb:  see **-thumb-mist**.
    Note: if you wish to make your own mask PNGS you can put them in
    $PREFIX/lib/tovid/masks/ or $HOME/.tovid/masks/ and use them on the
    command line using the filename minus the path and extension.
    (i.e ~/.tovid/masks/tux.png becomes **-thumb-shape tux**)
    No frame is used for shaped thumbs.

**-thumb-frame-size** INT
    The size (thickness) of the thumb frames in pixels.  This will also set the
    thickness of the raised "frame" of thumbs when you use **-3d-thumbs**.
    See also **-showcase-frame-size** and **-thumb-frame-color**

**-thumb-frame-color**, **-thumb-frame-colour** COLOR
    The color of frames for video thumbnails.  Use hexadecimal or named colors
    notation.  Remember to quote if using hexadecimal! ( '#ffac5f' ).

**-3d-thumbs**, **-3dthumbs**
    This will give an illusion of 3D to the thumbnails: dynamic lighting on
    rounded thumbs, and a raised effect on rectangular thumbs.  Try it !

**-titles-font** FONT
    Display thumbnail or textmenu titles in the given font

**-titles-fontsize** POINTS
    Font size to use for thumbnail or textmenu titles


Slideshows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-slides** IMAGES
    Use **-slides** IMAGES to pass in images for a slideshow.  The default is
    to make an animated menu of the slides, moving from one slide to the
    next. If you use **-static**, a 'polaroid stack' montage is created.  This
    composites the slides onto the background in 'random' locations with random
    rotations.  **-slides**  IMAGES can be used multiple times if you wish to
    make a menu with multiple slideshows.  You can also make a menu
    of mixed videos and slideshows by using **-slides** IMAGES, and **-files**
    VIDEOS multiple times.  For such a menu, the number of **-titles**
    needs to match the number of **-files** passed in plus the number of
    slideshows.  (Each time you use **-slides** counts as one title.)  To use
    a transition between the slides, use **-slide-transition**
    crossfade|fade.  See **-slide-transition** **-menu-slide-total**

**-menu-slide-total** INT
    Use INT number of the slides that were passed in with **-slides**
    to make the animated or static slide menu.  The length of the menu is
    determined by 1) **-menu-length** NUM if given,  and by 2) the length
    of the audio from **-bgaudio**.  For submenu slideshows, it is determined
    by 1) **-submenu-length** NUM if given,  and by 2) the length of the
    audio from **-submenu-audio** FILE(S).

**-submenu-slide-total** INT
    This option is the same as **-menu-slide-total** except that it is
    for submenu slideshows.

**-slide-transition** crossfade|fade [crossfade]
    The type of fade transition between slides in a animated slide menu.  Be
    sure the menu length is long enough to support the 1 second transitions
    between the slides.  The length is determined by 1) the length of the
    **-bgaudio AUDIO** and 2) the length given with **-menu-length NUM**.  For
    submenu slideshows, it is determined by 1) **-submenu-length NUM** if
    given, and by 2) the length of the audio from **-submenu-audio** FILE(S).

    See **-menu-slide-total** , **-bgaudio** , **-menu-length** ,
    **-submenu-length**, and **-submenu-audio**.

    The 'crossfade' transition fades from one slide to another.  The 'fade'
    transition fades in and out from and to black.  If you don't use this
    option, the default is to use a 'crossfade' transition.

**-slideshow-menu-thumbs** FILES
    Use the FILES instead of the 1st image in each slideshow as the
    thumb that shows on the menu.  This option is for multiple slideshows
    or mixed slideshow/video menus only.

**-slides-to-bin** FILES
    FILES will be resized to 640x480 using a 'box' filter - this
    is called 'binning'.  It will reduce the 'signal to noise' ratio for the
    image in the animated slide menu.  Use this if you get some unwanted
    effects for certain images, such as pixels shifting in what should be a
    static image.  See also **-slides-to-blur** and **-slide-border**

**-slides-to-blur** FILES
    FILES will be blurred a small amount - which will help on
    slides that still have noise even after 'binning' with -slides-to-bin.
    The default blur is 0x0.2 - you can increase this with
    -slide-blur ARG.  See also **-slides-to-bin** and **-slide-border**

**-slide-blur** VALUE or LIST of VALUES [0x0.2]
    The argument to use for blurring files.  It will be passed to
    imagemagick: convert -blur ARG.  The format of the arg is {radius}x{sigma}
    and the default is 0x0.2. Using values between 0x0.1 and 0x0.9 is probably
    the best range.  Use a single value for all, or a list to have a different
    blur for each file passed with **-slides-to-blur**.  You must pass in
    **-files-to-blur** FILES to use this option.  Blurring can help 'noise'
    problems in the video.  See also **-slides-to-bin** and **-slide-border**

**-slide-border** WIDTH [100]
    Pad the slides with a border for the animated slide menu.  The default
    without using an argument is 100.  Using this option can also solve some
    noise/ringing effects if used alone or in conjunction with 'binning'
    (**-slides-to-bin**) or blurring (**-slides-to-blur**).

**-slide-frame** WIDTH [12]
    Frame the slides for the animated slideshow menu.  The default width
    without using an  argument is 12.  See also **-slide-frame-color**

**-slide-frame-color** | **-slide-frame-colour**
    The color of the slide frame if passing **-slide-frame**.  The default if
    you don't use this option is a color-safe white: rgb(235,235,235).

**-showcase-slideshow**
    If doing multiple slideshows or mixed videos and slideshow(s), then use
    the animated slideshow as a showcase video.  It will be composed of slides
    from each slideshow in the menu.  The thumb for each slideshow button will
    be static.  If you used with a mixed menu of videos and slideshows, then
    the video thumbs WILL be animated, so you may wish to use -static or
    -textmenu with the option in that case.

**-background-slideshow**, **-bg-slideshow**
    If doing multiple slideshows or mixed videos and slideshow(s), then use
    the animated slideshow as a background video.  See **-showcase-slideshow**
    for additional details.

**-no-confirm-backup**
    Slideshows are an experimental (but well tested) feature.  Todisc is
    unlikely to overwrite your personal files, but you should take precautions
    and backup your images, as you would with any beta software.  Todisc
    will prompt you to backup your files normally.  If you have already backed
    up your images, use this option to disable the prompt.

**-use-dvd-slideshow** [FILE CONFIG]
    If you pass this option without an argument, tovid will use the
    dvd-slideshow program to create the animated slide menu, assuming you have
    this program installed.  The optional argument is the dvd-slideshow
    configuration file  - if you don't use this argument tovid will create it
    for you.  If you want to use the 'Ken Burns effect' - then the
    configuration file argument is required.  Note: the configuration file will
    override many of the above options for slideshows.


Advanced Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-menu-length**
    The desired animated main menu length in seconds

**-submenu-length**
    The desired submenu length.  This will also affect the length of submenu
    audio for static submenus.  (Assuming that -submenu-audio was passed in).
    The default is to use 10 seconds of audio for static menus.

**-submenu-stroke** COLOR
    The color for the sub-menu font outline (stroke)

**-submenu-title-color**, **-submenu-title-colour**
    The fill color used for sub-menu title fonts

**-submenu-titles**
    You can supple a list of titles here for sub-menus without the length
    restrictions found in thumb titles.  Must equal number of videos

**-chapters** [ NUM | CHAPTER POINTS in HH:MM:SS ]
    The number of chapters for each video (default: 6) OR
    the actual chapter points in HH:MM:SS format.
    Chapter points will be used for generating the submenu thumbs, and for
    seeking with your DVD player.  You can pass in just one value that will
    be used for all videos, or supply a list of values (number of chapters)
    or time code strings.

    If you just pass an integer for 'number of chapters', then tovid will
    make the chapter points for you by dividing the video length by the number
    you supply.  If using the **-no-menu** option, the INT passed in will be
    the chapter interval in minutes, rather than the above formula.

    If passing HH:MM:SS format you need to pass the string of chapter points for
    each video and each string should have comma separated values.
    Additionally, the first chapter should always start at 00:00:00 as
    dvdauthor will add that if it is not there already.

    To get your time codes, you can play your videos in mplayer and press 'o'
    to see them on-screen.  I have found these to be very accurate in my short
    tests.  For greater frame accuracy you could try loading the file in
    avidemux and find the time codes for the frames you want.

    If passing grouped chapters you need to join the chapters from all the
    videos in a group with a '+' separator.  If you want to skip creating
    chapters for a video in the group use '0' for its chapters.

    Note: chapters for grouped videos should probably be passed in using the
    above HH:MM:SS format. (Arbitrary chapters using just an INT for the # of
    chapters is not guaranteed to work reliably in all cases for grouped videos
    at the moment.)

    Example for passing just number of chapters ( 4 videos )::

        -chapters 5 2 4 8

    Example of passing chapter points ( 4 videos )::

        -chapters 00:00:00,00:05:34.41,00:12:54,00:20:45 \
        00:00:00,00:04:25.623,00:09:12,00:15:51 \
        00:00:00,00:05:10,00:13:41,00:18:13.033 \
        00:00:00,00:15:23.342,00:26:42.523

    Example of passing grouped chapters using the '+' separator::

        -chapters 00:00:00,00:05:34.41,00:12:54,00:20:45+00:04:23,00:09:35 \
        00:00:00... etc.

**-chapter-titles** LIST
    If you are using submenus, you can pass a list of titles for the
    chapters.  Each title must be quoted, and the number of titles given
    must equal the total number of chapters for all videos.  In other words
    if you use -chapters 4 6 8 , you must give 18 chapter titles, in the same
    order that the videos were passed in.

**-chapter-font** FONT
    Use FONT as the font for submenu chapters.

**-chapter-fontsize** SIZE
    Use SIZE as the pointsize for the chapters font.

**-chapter-color** COLOR
    The color for the chapters font.

**-chapter-stroke** COLOR
    The color for the chapters font outline (stroke)

**-seek** NUM | "NUM1 NUM2 NUM3 . . ."
    Seek to NUM seconds before generating thumbnails (default: 2.0 seconds)
    If a quoted string of values matching the number of videos is used, then
    each video can use a different seek value
    If using switched menus, the **-seek** value(s) will be used to generate
    the showcase image that displays on switching to another video choice with
    the up/down arrow keys.

**-showcase-seek** NUM
    Seek to NUM seconds before generating thumbnails for showcase video
    (default: 2.0 seconds)

**-bgvideo-seek**, **-bg-video-seek** NUM
    Seek to NUM seconds before generating images for background video
    (default: 2.0 seconds)

**-bgaudio-seek**, **-bg-audio-seek** NUM
    Seek to NUM seconds before generating audio for bgaudio
    (default: 2.0 seconds)

**-group** N VIDEO1 VIDEO2 . . .
    Allow grouping videos in dvdauthor.xml, so they will play sequentially as
    a group.  The videos passed in after the 'N' will be grouped with the 'Nth'
    video. Example::

        -group 2 2.mpg 3.mpg 4.mpg

    will group these 3 videos with the 2nd video given with **-files**, so that
    they will play sequentially as one title.  Only one thumbnail and/or title
    will appear on the menu for the group: it will be made from the 1st video
    in the group.  In the above example if you passed::

        -files foo.mpg bar.mpg baz.mpg -group 2 2.mpg 3.mpg 4.mpg

    then the group will consist of bar.mpg  2.mpg, 3.mpg and 4.mpg, and only the
    title and/or thumbnail for bar.mpg will appear in the menu.  You can use
    **-group** more than once for multiple groups.  Be  sure to quote video
    filenames if they contain  spaces.

**-jobs**
    By default, **tovid disc** starts a parallel job for each processor
    detected.  With this option you can manually set the number of jobs.  For
    example if you have a computer with 2 CPUs you can set **-jobs 1** to keep
    one processor free for other things.  At present this applies to the time
    consuming imagemagick loops: you will notice a substantial speedup now if
    you have a multi-cpu system.

**-no-ask**, **-noask**
    Skip all interactive questions.  No preview, automatic re-encoding with
    tovid if needed, no interactive option to use background video for bgaudio.

**-no-warn**, **-nowarn**
    Don't pause after outputting warning or info messages

**-grid**
    Show a second preview image with a grid and numbers that will help in finding
    coordinates for options that might use them, like **-text-start**


Menu Style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-menu-title-geo** north|south|east|west|center [south]
    The position of the menu title.  You may need to use **-align** as well if
    you don't want your title covering other parts of your menu.  See
    **-align**

**-menu-title-offset** OFFSET (+X+Y)
    Move menu title by this offset from its N|S|E|W|Center position.  You
    may need to use **-align** as well if you don't want your title covering other
    parts of your menu.  See **-align**

**-button-style** rect|text|line|text-rect
    The style of button that you will see when you play the DVD.  "rect" draws
    a rectangle around the thumb when you select it in the DVD player.  "text"
    highlights the video title text, "line" underlines the title, and
    "text-rect" draws a rectangle around the title text.

**-title-color**, **-title-colour** COLOR
    Color to use for the main menu title.  For list of supported colors do:
    **convert -list** color.  HTML notation may be used: "#ff0000". See:
    http://www.imagemagick.org/script/color.php

**-title-stroke** COLOR
    Outline color for the main menu's title font. Use "none" for transparent
    outline  (see title-color)

**-titles-stroke** COLOR
    Outline color for the thumb or textmenu video titles font. Use "none" for
    transparent outline  (see **-titles-color**).

**-highlight-color**, **-highlight-colour**
    Color to use for the menu buttons that your DVD remote uses to navigate.

**-select-color**, **-select-colour**
    Color to use for the menu buttons that your DVD remote uses to select.

**-text-mist**
    Put a semi-transparent misted background behind the text for the menu's
    title, just slightly larger than the text area.

**-text-mist-color**, **-text-mist-colour** COLOR
    Color of the mist behind the menu's title (see title-color).

**-text-mist-opacity**
    Opacity of the mist behind the menu's title - see **-opacity**

**-title-opacity**
    Opacity of the menu title text

**-titles-opacity**
    Opacity of the text for video titles

**-submenu-title-opacity**
    Opacity of the text for submenu menu titles

**-chapter-title-opacity**
    Opacity of the text for submenu chapter titles

**-menu-audio-fade**
    Number of sec to fade given menu audio in and out (default: 1.0 seconds)
    If you use **-menu-audio-fade** 0 then the audio will not be faded.

**-submenu-audio-fade**
    Number of secs to fade sub-menu audio in and out (default: 1.0 seconds).
    See **-menu-audio-fade**

**-intro** VIDEO
    Use a introductory video that will play before the main menu.
    At present it must be a DVD compatible video at the correct resolution etc.
    Only 4:3 aspect is supported: 16:9 will give unexpected results.


Showcase and textmenu
-------------------------------------------------------------------------------
The following menu style options are specific to showcase and textmenu arrangements:

**-text-start** N
    This option is for **-textmenu** menus.  The titles will start at the Nth
    pixel from the top of the menu ( Y axis ).

**-title-gap** N
    This option is for **-textmenu** menus.  The gap is the space between
    titles vertically ( Y axis ).

**-rotate** DEGREES
    Rotate the showcase image|video clockwise by DEGREES.
    (default: if used without options, the rotate will be 5 degrees).  Note:
    this will not turn a portait image into a landscape image!

**-showcase-geo** GEOMETRY
    The position of the showcase image.  ( XxY position )

**-wave** default|GEOMETRY
    Wave effect for showcase image|video.  Alters thumbs along a sine wave
    using GEOMETRY. (default: no wave) "default" will produce a wave arg of
    **-20x556**, which produces a gentle wave with a small amount of
    distortion.  See: http://www.imagemagick.org/Usage/distorts/#wave if you
    want to try other values.

**-showcase-shape**  egg|oval|plectrum|arch|spiral|galaxy|flat-tube|normal
    Apply a shaped transparency mask to showcase videos or images.
    Note: if you wish to make your own mask PNGS you can put them in
    $PREFIX/lib/tovid/masks/ or $HOME/.tovid/masks/ and use them on the
    command line using the filename minus the path and extension.
    No frame is used for shaped thumbs.

**-showcase-framestyle**  none|glass
    For **-showcase-** style template only
    "none" will use the default frame method, using "convert -frame . . ."
    "glass" will use mplayer to make frames, which gives an interesting
    animated effect to the frames, and can be much faster ( especially if you
    don't use **-rotate** or **-wave** as thumbs will not need to be processed
    again after mplayer spits them out.  Note: you need to be using either
    **-showcase** IMAGE or **-showcase** VIDEO for this "frame style" to work.

**-showcase-frame-size** PIXELS
    The size of the showcase frame.  This value will be used for both width and
    height for the 'thickness' of the frame.  This will also set the thickness
    of the raised "frame" of the showcase thumb when you use **-3d-showcase**.
    See also **-thumb-frame-size** and **-showcase-frame-color**

**-showcase-frame-color**, **-showcase-frame-colour** PIXELS
    The color of the showcase frame.  Use hexadecimal or named colors notation.
    Remember to quote! ( '#ffac5f' ).

**-3d-showcase**, **-3dshowcase**
    This will give an illusion of 3D to the showcase thumb: dynamic lighting on
    rounded thumbs, and a raised effect on rectangular thumbs.  Try it !


Thumbnail style
-------------------------------------------------------------------------------

**-opacity** [0-100] (default 100)
    Opacity of thumbnail videos as a percentage (no percent sign).
    Anything less than 100(%) is semi-transparent. Not recommended with dark
    backgrounds.

**-thumb-blur**, **-blur** NUM
    The amount of feather blur to apply to the thumb-shape.  The default is 1.0
    which will more or less keep the shape and produces transparency at the
    edges.  Choose float or integer values between 0.1 and 2.0. 3D thumbs are
    set to a tiny blur, so this option doesn't affect the **-3dthumbs** option.

**-showcase-blur** NUM
    The amount of 'feather' blur to apply to the showcase image/video.  Choose
    values between 0.1 and 2.0.  This option has no effect on **-3d-showcase**.
    See **-thumb-blur** for more info.

**-align** north|south
    This will align  thumbs/titles north or south.
    If **-align** south then menu title will align north, unless you manually
    set one or both of **-menu-title-geo** or **-menu-title-offset**.

**-thumb-mist** [COLOR]
    Use a mist behind thumbnails.  The optional argument is the color of the
    mist.  This option helps with contrast.  Be sure to set the font color
    to an appropriate color if using a colored mist, and/or use a bold font.

**-titles-color**, **-titles-colour** COLOR
    Color to use for the thumb or textmenu titles.  If your titles are not
    clear enough or look washed out, try using a **-titles-stroke** that
    is the same color as used with **-titles-color**  (see **-title-color**)

**-showcase-titles-align** west|east (default: center [centre])
    The default is to center the text above the thumbnails.  This option will
    align the titles either to the left (west) or right (east).  Aligning west
    gives more space to the titles.  Aligning east also does so, and as well
    will facilitate using \n in your titles to achieve multi line titles.

**-tile-3x1**, **-tile3x1**
    Use a montage tile of 3x1 instead of the usual 2x2 for 3 videos
    ie.::

        [movie1] [movie2] [movie3] instead of:

        [movie1] [movie2]

        [movie3]

    This option only comes into play if the number of videos supplied equals 3
    Otherwise it will be silently ignored. Not used for **-showcase-\*** style.

**-tile-4x1**, **-tile4x1**
    Same as **-tile-3x1** above, except use tile of 4x1. (one row of 4 videos)

**-thumb-columns** 3|4
    Same as **-tile-3x1** and **tile-4x1** above, except it accepts either '3'
    (1 row of 3 thumbs), or '4' (one row of 4 thumbs) as an argument.  This
    alternative was added to help compact the gui layout.

**-rotate-thumbs** DEGREE LIST ( list of degrees, one for each thumb )
    Rotate thumbs the given amount in degrees - can be positive or negative.
    There must be one value for each file given with **-files**.
    If the values are not the same distance from zero, the thumbs will be of
    different sizes as images are necessarily resized *after* rotating.  With
    the default montage template - this will also resize the titles; with the
    showcase template the titles will remain the same size. Example::

        -rotate-thumbs -10 10 -10 10 -10  (for 5 files)

    **Note**: this option will not turn a portrait image into a landscape image!


Dvdauthor options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-loop** PAUSE
    Pause in seconds at end of menu.  Use "inf" if you wish indefinite pause.
    Note: using "inf" with **-menu-fade** will disable the fadeout portion of
    the fade.  (default: "inf" for static menu, 10.0 seconds for animated.)

**-playall**
    This option will create a button on the main menu that will allow going
    right to the 1st title and playing all videos in succession before
    returning to the main menu.  If doing titlesets you can use this within
    the **-vmgm** ... **-end-vmgm** options to allow playing ALL titlesets.
    (If you want also to have a playall button in each titleset you could use
    this option between each **-titleset** ... **-end-titleset** option or put
    it outside of the vmgm and titlset options as a general option.

**-videos-are-chapters**
    A button will be made on the main menu for each video, which you can use as
    a chapter button.  Selecting any video will play them all in order
    starting with the selected one.

**-chain-videos** NUM | N1-NN
    Without options this will chain all videos together so they play
    sequentially without returning to the main menu, except for the last, which
    will return.  You can also specify which videos you want to behave this way
    by number or by a range. ( ie. **-chain-videos** 1 2 4-6 ).

**-subtitle-lang** "lang1 lang2 . . ."
    This allows selectable subtitles in the DVD, assuming you have optional
    subtitles muxed into your videos.  Use 2 character language codes.

**-audio-channel** "Video1_track Video2_track Video3_track . . ."
    "VideoN_track" is the track number to use in a multi-track (multi-language)
    mpeg: usually something like **-audio-channel** "1 0 1".  The 1st track is
    0, 2nd is 1 . . . etc.  If the tracks are 0. English 1.French, then the
    above would make French the audio language on Video1 and Video3, and
    English the audio language on Video2.  You can check the mpeg with
    "mplayer -v . . .".

**-audio-lang** LANGUAGE CODES
    Identify the audio tracks on the DVD.  These language codes are used for
    each video in the titleset.  When you use the audio button on your DVD
    remote the language name is displayed.  Example: **-audio-lang** en fr

**-aspect** 4:3|16:9
    This will output a <video aspect WIDTH:HEIGHT /> tag for the dvdauthor
    xml file.  It will affect all videos in the titleset.  Example::

        -aspect 16:9

**-widescreen** nopanscan|noletterbox [nopanscan]
    This will output a <video widescreen=nopanscan /> tag (for example)
    for the dvdauthor xml file.  It will affect all videos in the titleset. Use
    in conjunction with **-aspect** if your dvd player is cropping your videos.
    Example::

        -aspect 16:9 -widescreen

**-quick-nav**
    This option will allow navigation of a menu with more than one titleset by
    using the left and right arrow keys of your DVD remote.  When you press
    this key the highlight will go the next or previous title.  If you are at
    the end of a titleset the right key will go to the next titleset.  If you
    are at the beginning of a titleset, the left key will go to the previous
    titleset.  If no next or previous titleset it will cycle to the end or
    beginning of the titlesets.

**-outlinewidth**, **-outline-width** WIDTH
    For spumux outlinewidth variable.  If there is a large gap between words in
    a text button, this option may help.

**-video-pause** PAUSE (single value or list)
    The pause in seconds after playing a video title.  This is useful for
    slideshows: the 'slide' will remain on the screen for this length of time.
    If you have grouped videos you should probably not pause the videos that
    have a grouped title after it, but instead see **-grouped-video-pause**.
    Note: if you provide a list of values they must be one for each video.

**-group-video-pause** PAUSE (single value or list)
    The pause in seconds after a grouped video plays.  If you wish to pause
    after the whole group finishes, then only use a value greater than zero
    for the last video in the group.  If providing a list of values they must
    equal the number of grouped videos.


Burning the disc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-burn**
    Prompt to burn the DVD directory on completion.

**-device** DEVICE [/dev/dvdrw]
    Device to use for the burning program.

**-speed** N
    The speed to use for burning the disc.



.. _command-mpg:

Command:mpg
===============================================================================

**tovid mpg** converts arbitrary video files into (S)VCD/DVD-compliant
MPEG format, suitable for burning to CD/DVD-R for playback on a
standalone DVD player.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid mpg [OPTIONS] -in INFILE -out OUTPREFIX

Where *INFILE* is any multimedia video file, and *OUTPREFIX* is what
you want to call the output file, minus the file extension. *OPTIONS*
are additional customizations, described below.

By default, you will (hopefully) end up with an NTSC DVD-compliant
MPEG-2 video file; if you burn this file to a DVD-R, it should be
playable on most DVD players.

For example:

``tovid mpg -in foo.avi -out foo_encoded``
    Convert 'foo.avi' to NTSC DVD format, saving to 'foo_encoded.mpg'.

``tovid mpg -pal -vcd foo.avi -out foo_encoded``
    Convert 'foo.avi' to PAL VCD format, saving to 'foo_encoded.mpg'.

Basic options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-v**, **-version**
    Print tovid version number only, then exit.

**-quiet**
    Reduce output to the console.

**-fake**
    Do not actually encode; only print the commands (mplayer, mpeg2enc etc.)
    that would be executed. Useful in debugging; have tovid give you the
    commands, and run them manually.

**-ffmpeg**
    Use ffmpeg for video encoding, instead of mplayer/mpeg2enc. Try this if
    you have any problems with the default encoding method. Using this option,
    encoding will be considerably faster. Currently does not work with
    **-subtitles** or  **-filters**.

Television standards
-------------------------------------------------------------------------------

**-ntsc**
    NTSC format video (USA, Americas) (default)

**-ntscfilm**
    NTSC-film format video

**-pal**
    PAL format video (Europe and others)

Formats
-------------------------------------------------------------------------------

Standard formats, should be playable in most DVD players:

**-dvd**
    (720x480 NTSC, 720x576 PAL) DVD-compatible output (default)

**-half-dvd**
    (352x480 NTSC, 352x576 PAL) Half-D1-compatible output

**-svcd**
    (480x480 NTSC, 480x576 PAL) Super VideoCD-compatible output

**-dvd-vcd**
    (352x240 NTSC, 352x288 PAL) VCD-on-DVD output

**-vcd**
    (352x240 NTSC, 352x288 PAL) VideoCD-compatible output

Non-standard formats, playable in some DVD players:

**-kvcd**
    (352x240 NTSC, 352x288 PAL) KVCD-enhanced long-playing video CD

**-kdvd**
    (720x480 NTSC, 720x576 PAL) KVCD-enhanced long-playing DVD

**-kvcdx3**
    (528x480 NTSC, 520x576 PAL) KVCDx3 specification

**-kvcdx3a**
    (544x480 NTSC, 544x576 PAL) KVCDx3a specification (slightly wider)

**-bdvd**
    (720x480 NTSC, 720x576 PAL) BVCD-enhanced long-playing DVD

See kvcd.net (http://kvcd.net/) for details on the KVCD specification. Please
note that KVCD ("K Video Compression Dynamics") is the name of a compression
scheme that can be applied to any MPEG-1 or MPEG-2 video, and has little to
do with VCD ("Video Compact Disc"), which is the name of a standard video disc
format.

Advanced options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aspect ratios
-------------------------------------------------------------------------------

tovid automatically determines aspect ratio of the input video by playing it in
mplayer. If your video plays with correct aspect in mplayer, you should not
need to override the default tovid behavior.

If mplayer does not play your video with correct aspect, you may provide an
explicit aspect ratio in one of several ways:

**-aspect** *WIDTH*:*HEIGHT*
    Custom aspect, where *WIDTH* and *HEIGHT* are integers.

**-full**
    Same as **-aspect 4:3**

**-wide**
    Same as **-aspect 16:9**

**-panavision**
    Same as **-aspect 235:100**

The above are the intended INPUT aspect ratio. tovid chooses an optimal output
aspect ratio for the selected disc format (VCD, DVD, etc.) and does the
appropriate letterboxing or anamorphic scaling. Use **-widetv** to encode
for a widescreen monitor or TV.

Video stream options
-------------------------------------------------------------------------------

**-quality** *NUM* (default 6)
    Desired output quality, on a scale of 1 to 10, with 10 giving the best
    quality at the expense of a larger output file. Default is 6. Output size
    can vary by approximately a factor of 4 (that is, **-quality 1** output
    can be 1/4 the size of **-quality 10** output). Your results may vary.
    WARNING: With **-quality 10**, the output bitrate may be too high for
    your hardware DVD player to handle. Stick with 9 or lower unless you
    have phenomenally good eyesight.

    At present, this option affects both output bitrate and quantization (but
    may, in the future, affect other quality/size-related attributes). Use
    **-vbitrate** if you want to explicitly provide a maximum bitrate.

**-vbitrate** *NUM*
    Maximum bitrate to use for video (in kbits/sec). Must be within allowable
    limits for the given format. Overrides default values. Ignored for VCD,
    which must be constant bitrate.

**-interlaced**
    Do interlaced encoding of the input video (top fields first). Use this
    option if your video is  interlaced, and you want to preserve as much
    picture quality as possible. This option is ignored for VCD, which
    doesn't support it.

    You can tell your source video is interlaced by playing it, and pausing
    during a scene with horizontal motion; if you see a "comb" effect at the
    edges of objects in the scene, you have interlaced video. Use this option
    to encode it properly.

    If you would prefer to have output in progressive format, use
    **-progressive**. If you have a DV camera, use **-interlaced_bf** since
    DV footage is generally bottom fields first.

**-interlaced_bf**
    Do interlaced encoding of the input video (bottom fields first).

**-deinterlace** | **-progressive**
    Convert interlaced source video into progressive output video. Because
    deinterlacing works by averaging fields together, some picture quality is
    invariably lost. Uses an adaptive kernel deinterlacer (kerndeint), or,
    if that's not available, the libavcodec deinterlacer (lavcdeint).

**-mkvsub** *LANG* (EXPERIMENTAL)
    Attempt to encode an integrated subtitle stream (such as may be found in
    Matroska .mkv files) in the given language code (eng, jpn, etc.) May work
    for other formats.

**-autosubs**
    Automatically include subtitle files with the same name as the input video.

**-subtitles** *FILE*
    Get subtitles from *FILE* and encode them into the video.  WARNING: This
    hard-codes the subtitles into the video, and you cannot turn them off while
    viewing the video. By default, no subtitles are loaded. If your video is
    already compliant with the chosen output format, it will be re-encoded to
    include the subtitles.

**-type** {live|animation|bw}
    Optimize video encoding for different kinds of video. Use 'live' (default)
    for live-action video, use 'animation' for cartoons or anime, and 'bw' for
    black-and-white video.  This option currently only has an effect with
    KVCD/KSVCD output formats; other formats may support this in the future.

**-safe** *PERCENT*
    Fit the video within a safe area defined by *PERCENT*. For example,
    **-safe 90%** will scale the video to 90% of the width/height of the output
    resolution, and pad the edges with a black border. Use this if some of the
    picture is cut off when played on your TV.  The percent sign is optional.

**-filters** {none,denoise,deblock,contrast,all} (default none)
    Apply post-processing filters to enhance the video. If your input video is
    very high quality, use 'none'. If your input video is grainy, use 'denoise';
    if it looks washed out or faded, use 'contrast'. You can use multiple
    filters separated by commas. To apply all filters, use 'all'.

**-fps** *RATIO*
    Force input video to be interpreted as *RATIO* frames per second.  May be
    necessary for some ASF, MOV, or other videos. *RATIO* should be an
    integer ratio such as "24000:1001" (23.976fps), "30000:1001" (29.97fps), or
    "25:1" (25fps). This option is temporary, and may disappear in future
    releases. (Hint: To convert a decimal like 23.976 to an integer ratio, just
    multiply by 1000, i.e. 23976:1000)

**-crop** *WIDTH*:*HEIGHT*:*X*:*Y*
    Crop a portion of the video *WIDTH* by *HEIGHT* in size, with the
    top-left corner at *X*, *Y*.

**-widetv**
    Always encode to 16:9 widescreen (only supported by **-dvd**, **-kdvd**,
    **-bdvd**), for optimal viewing on a widescreen monitor or TV.

Audio stream options
-------------------------------------------------------------------------------

**-normalize**
    Analyze the audio stream and then normalize the volume of the audio.
    This is useful if the audio is too quiet or too loud, or you want to
    make volume consistent for a bunch of videos. Similar to running
    normalize without any parameters. The default is -12dB average level
    with 0dB gain.

**-amplitude** *NUM[dB]*
    In addition to analyzing and normalizing, apply the gain to the audio
    such that the 'average' (RMS) sound level is *NUM*. Valid values
    range 0.0 - 1.0, with 0.0 being silent and 1.0 being full scale. Use
    *NUMdB* for a decibel gain below full scale (the default without
    **-amplitude** is -12dB).

**-abitrate** *NUM*
    Encode audio at *NUM* kilobits per second.  Reasonable values include
    128, 224, and 384. The default is 224 kbits/sec, good enough for most
    encodings. The value must be within the allowable range for the chosen disc
    format; Ignored for VCD, which must be 224.

**-audiotrack** *NUM*
    Encode the given audio track, if the input video has multiple audio tracks.
    *NUM* is *1* for the first track, *2* for the second, etc. You may
    also provide a list of tracks, separated by spaces or commas, for example
    **-audiotrack 3,1,2**. Use **tovid id** on your source video to determine
    which audio tracks it contains.

**-downmix**
    Encode all audio tracks as stereo.  This can save space on your DVD if
    your player only does stereo.  The default behavior of tovid is to use
    the original number of channels in each track.  For aac audio, downmixing
    is not possible: tovid runs a quick 1 frame test to try to downmix the
    input track with the largest number of channels, and if it fails then it
    will revert to the default behavior of using the original channels.

**-async** *NUM*
    Adjust audio synchronization by *NUM* seconds.

Other options
-------------------------------------------------------------------------------

**-config** *FILE*
    Read configuration from *FILE*, containing 'tovid' alone on the first
    line, and free-formatted (whitespace-separated) tovid command-line options
    on remaining lines.

**-force**
    Force encoding of already-compliant video or audio streams.

**-overwrite**
    Overwrite any existing output files (with the same name as the given
    **-out** option).

**-priority** {low|medium|high}
    Sets the main encoding process to the given priority. With high priority,
    it may take other programs longer to load and respond. With lower priority,
    other programs will be more responsive, but encoding may take 30-40%
    longer.  The default is high priority.

**-discsize** *NUM*
    When encoding, tovid automatically splits the output file into several
    pieces if it exceeds the size of the target media. This option sets the
    desired target DVD/CD-R size to *NUM* mebibytes (MiB, 2^20). By default,
    splitting occurs at 700 for CD, 4300 for DVD. Use higher values at your
    own risk. Use 650 or lower if you plan to burn to smaller-capacity CDs.
    Doesn't work with the **-ffmpeg** option.

**-fit** *NUM*
    Fit the output file into *NUM* MiB. Rather than using default (or
    specified) video bitrates, tovid will calculate the correct video bitrate
    that will limit the final output size to *NUM* MiB. This is different
    than **-discsize**, which cuts the final file into *NUM* MiB pieces.
    **-fit** makes sure that the file never exceeds *NUM* MiB. This works
    with **-ffmpeg**, but not with **-vcd** since VCDs have a standardized
    constant bitrate.

**-parallel**
    Perform ripping, encoding, and multiplexing processes in parallel using
    named pipes. Maximizes CPU utilization and minimizes disk usage. Note that
    this option simply does more tasks simultaneously, in order to make better
    use of available CPU cycles; it's unrelated to multi-CPU processing (which
    is done automatically anyway). Has no effect when **-ffmpeg** is used.

**-update** *SECS*
    Print status updates at intervals of *SECS* seconds. This affects how
    regularly the progress-meter is updated. The default is once every five
    seconds.

**-mplayeropts** "**OPTIONS**"
    Append *OPTIONS* to the mplayer command run during video encoding.  Use
    this if you want to add specific video filters (documented in the mplayer
    manual page). Overriding some options will cause encoding to fail, so use
    this with caution!

**-nofifo** (EXPERIMENTAL)
    Do not use a FIFO pipe for video encoding. If you are getting "Broken pipe"
    errors with normal encoding, try this option.  WARNING: This uses lots of
    disk space (about 2 GB per minute of video).

**-keepfiles**
    Keep the intermediate files after encoding. Usually, this means the audio
    and video streams are kept (eg the .ac3 and .m2v files for an NTSC DVD).
    This doesn't work with **-parallel** because the intermediate files are named
    pipes, and not real files.

**-slice** *START*-*END*
    Encode a segment from *START* to *END* (in seconds). Only works with
    **-ffmpeg**.

**-from-gui**
    Put makempg into a fully non-interactive state, suitable for calling from
    a gui.

**-noask**
    Don't ask questions when choices need to be made. Assume reasonable
    answers.


.. _command-id:

Command:id
===============================================================================

**tovid id** identifies each multimedia video file in a
list, and reports its compliance with video disc standards such as VCD,
SVCD, and DVD.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid id [OPTIONS] VIDEO_FILE(s)

For example:

``tovid id foo.avi``
``tovid id -tabluar videos/*.mpg``

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-terse**
    Print raw video characteristics, no formatting. Helpful when
    calling from other scripts.

**-verbose**
    Print extra information from mplayer, tcprobe, and ffmpeg.

**-accurate**
    Do lengthy play-time estimation by scanning through the entire video file.
    Use this if the default behavior is giving you inaccurate play times.

**-fast**
    Skip lengthy play-time estimation, and go with what mplayer reports
    as being the video duration. Unlike pre-0.32 versions of tovid, this
    is now the default behavior, and the **-fast** option doesn't do anything.

**-tabular**
    Display output in a table format for easier comparison. Most useful
    when identifying multiple video files.

**-isformat** [pal-dvd|ntsc-dvd] (same syntax for vcd and svcd)
    Check *VIDEO_FILE* for compliance with the given disc format.
    If *VIDEO_FILE* matches the given format, then **tovid id** reports "true"
    and exits successfully. Otherwise, **tovid id** reports "false" and exits
    with status 1 (failure).  This checks and reports both vcd/svcd/dvd
    and pal/ntsc.

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tovid id -verbose homevideo.avi``
    Report everything mplayer, ffmpeg, and transcode can determine about
    homevideo.avi.

``tovid id -isformat dvd homevideo.mpg``
    Check to see if homevideo.mpg is compliant with the DVD standard.


.. _command-menu:

Command:menu
===============================================================================

**tovid menu** generates textual (S)VCD- or DVD-compliant MPEG videos for use
as navigational menus, given a list of text strings to use for title names. You
can customize the menu by providing an optional background image or audio clip,
or by using custom font and font color.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid menu [OPTIONS] TITLES -out OUT_PREFIX

For example:

``tovid menu "Season One" "Season Two" "Featurettes" -out MainMenu``

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-ntsc** (default)
    Generate an NTSC-format menu

**-ntscfilm**
    Generate an NTSC-format menu (24000/1001fps)

**-pal**
    Generate a PAL-format menu

**-dvd** (default)
    Generate a DVD-format menu, with highlighted text included
    as a multiplexed subtitle stream.

**-vcd** or **-svcd**
    Generate a VCD/SVCD menu; each menu option will have a
    number associated with it. You can have up to nine menu
    options per menu.

Menu background/audio options:

**-background** *IMAGE*
    Use *IMAGE* (in most any graphic format) as a background. If image is not
    the correct aspect ratio (4:3), it will be scaled and/or cropped,
    depending on the **-crop** and **-scale** options. If no background is
    supplied, a default background will be created.

**-crop** (default)
    If provided background image is not 4:3 aspect ratio, crop edges
    to make it so. Image will be scaled up if it is too small. Cropping
    keeps the center area of image. If you want to do cropping/scaling
    yourself in another program, provide an image of 768x576 pixels.

**-scale**
    If provided background image is not 4:3 aspect ratio, scale/stretch
    it to make it fit. May cause visible distortion!

**-audio** *AUDIOFILE*
    Use *AUDIOFILE* (in most any audio format) for background music. The
    menu will play for long enough to hear the whole audio clip. If
    one is not provided, 4 seconds of silence will be used.

**-length** *NUM*
    Make the menu *NUM* seconds long. Useful for menus with **-audio**:
    if you don't want the entire *AUDIOFILE* in the menu, then you can trim
    the length of the menu with **-length**.

Menu text options:

**-menu-title** "*MENU TITLE TEXT*"
    Add *MENU TITLE TEXT* as a title/header to the menu.

**-font** *FONTNAME* (default Helvetica)
    Use *FONTNAME* for the menu text. Run 'convert -list type' to see a
    list of the fonts that you can use; choose a font name from the
    leftmost column that is displayed. Or you can specify a ttf font file instead.
    E.g., **-font /path/to/myfont.ttf**.

**-fontsize** *NUM* (default 24)
    Sets the size for the font to *NUM* pixels.

**-menu-title-fontsize** *NUM* (default **-fontsize** + 8)
    Sets the size of the menu title.

**-fontdeco** '*FONTDECORATION*'
    Sets the font decoration method to *FONTDECORATION*. It is used by the
    'convert' ImageMagick command to draw the menu text. You can add colored
    text outlines, gradient fills, and many others. See **Usage notes**.

**-align** {left|center|middle|right}
    Align the text at the top left, top center, very middle, or top right
    side of the screen. You may also substitute any "gravity" keyword
    allowed by ImageMagick (north|south|east|west|northeast|southwest|...).

**-textcolor** {#RRGGBB|#RGB|COLORNAME}
    Use specified color for menu text. #RRGGBB and #RGB are
    hexadecimal triplets (e.g., #FF8035). COLORNAME may be any of
    several hundred named colors; run 'convert -list color' to see them.
    White (#FFF) is the default color.

DVD-only options:

**-button** *BUTTON* (default '>')
    Specify the button used for menu selection. Specify either a *single*
    character or one of the shortcuts:

    **play**
        Use a button shaped like 'Play' on many A/V electronics:
        a triangle pointing to the right. (uses the font Webdings)
    **movie**
        Use a button shaped like an old movie projector.
        (uses the font Webdings)
    **utf8**
        Use your own non-keyboard character as a button. Provide
        only the four hex digits: eg **-button utf8 00b7**. Beware that
        ImageMagick's utf8 characters aren't the same as those drawn in
        character browsers like gucharmap.

**-highlightcolor** {#RRGGBB|#RGB|COLORNAME}
    Use the specified color for button highlighting. Yellow (#FF0) is the
    default color.

**-selectcolor** {#RRGGBB|#RGB|COLORNAME}
    Use the specified color for button selections (when a menu item is played
    or activated). Red (#F00) is the default color.

**-button-outline** {#RRGGBB|#RGB|COLORNAME}
    Outline buttons with the specified color. 'none' is the default.

**-button-font** *FONTNAME*
    Specify a differnt font to use for the buttons. By default, the button
    font will be inherited from the title font (see **-font**). Use this
    option to use a different font for the buttons. The button font size is
    inherited from **-fontsize** and cannot be changed.

Other options:

**-debug**
    Print extra debugging information to the log file. Useful in
    diagnosing problems if they occur. This option also leaves
    the log file (with a .log extension) in the directory after
    encoding finishes as well as all the temporary files created.

**-nosafearea**
    Do not attempt to put text inside a TV-safe viewing area. Most
    television sets cut off about 10% of the image border, so the script
    automatically leaves a substantial margin. This option turns that
    behavior off, leaving only a tiny margin. Use at your own risk.

**-overwrite**
    Overwrite any existing output menu.

**-noask**
    Don't ask interactive questions, and assume answers that will
    continue making the menu until completion.

**-quiet**
    Limit output to essential messages.

If the word "**back**" is given as an episode title, a "back" button for
returning to a higher-level menu will be added at the end of the list
of titles. "**Back**" *must be the last title listed*.

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make an NTSC VCD menu with white Helvetica text containing three centered
selections: Episode 1, Episode 2, and Episode 3. The finished menu will be
called Season-1.mpg::

 $ tovid menu -ntsc -vcd \
    -align center -textcolor white -font "Helvetica" \
    "Episode 1" "Episode 2" "Episode 3" \
    -out "Season-1"

Make an NTSC DVD menu with white Kirsty text containing three lower-left
aligned selections: Episode 1, Episode 2, and Episode 3. Items under the cursor
will be highlighted a pale blue, and selected items will be a pale orange
(before going to the selected title). The finished menu will be called
Main-menu.mpg::

 $ tovid menu -ntsc -dvd \
    -align southwest \
    -textcolor white \
    -highlightcolor "#5f65ff" \
    -selectcolor "#ffac5f" \
    -font "Kirsty" \
    "Episode 1" "Episode 2" "Episode 3" \
    -out "Main_menu"

Usage notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The argument given to **-font** must be one of the fonts listed by the command
'convert -list type'. Please note that many of your installed fonts may not be
available; if you want to maximize the number of fonts available, download and
run Anthony Thyssen's (http://www.cit.gu.edu.au/~anthony/anthony.html)
imagick_type_gen.pl (http://www.cit.gu.edu.au/~anthony/software/imagick_type_gen.pl)
script and run it like this::

    imagick_type_gen.pl > ~/.magick/type.xml.

If that doesn't work, try::

    imagick_type_gen.pl > ~/.magick/type.mgk.

Or you can specify a ttf font file directly to the **-font** options if you
don't want to install fonts to ImageMagick.

The **-fontdeco** option is quite flexible and takes a lot of ImageMagick's
*convert* options. Please refer to the tovid wiki
(http://tovid.wikia.com/wiki/Making_a_DVD_with_text_menus)
and Anthony Thyssen's guide for further explanation and examples.


.. _command-xml:

Command:xml
===============================================================================

**tovid xml** generates XML output describing an (S)VCD
or DVD file structure and navigation hierarchy in the format expected by
dvdauthor (http://dvdauthor.sourceforge.net/) or
vcdxbuild (http://www.vcdimager.org/).

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid xml [OPTIONS] VIDEOS -out OUTFILE

For example::

 tovid xml -menu MainMenu.mpg \
   Season1.mpg Season2.mpg Featurettes.mpg \
   -out MyDisc

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-dvd** (default)
    Generate the XML for a DVD disc, to be used with dvdauthor or **tovid dvd**.

**-vcd**
    Generate the XML for a VCD disc, to be used with vcdxbuild or **tovid vcd**.

**-svcd**
    Generate the XML for an SVCD disc, to be used with vcdxbuild or **tovid vcd**.

**-overwrite**
    Overwrite any existing output files.

**-quiet**
    Limit output to essential messages.

*VIDEOS* may be any of the following:

*<file list>*
    List of one or more video files to include, separated by spaces. At
    minimum, a DVD must have one video file. You can use shell wildcards
    (i.e., "\*.mpg") to include multiple files easily. Put filenames in
    quotes if they have spaces in them.

**-menu** *VIDEO* *<file list>*
    Use video file *VIDEO* as a menu from which you can jump to each of
    the listed video files. If you have multiple menus, include a
    top menu so they are reachable.

**-slides** *<file list>*
    Create a slide-show of still images

DVD-only options

**-group** *<file list>* **-endgroup**
    (DVD only) List of video files to include as one single title. This is useful
    if you have split a movie into several video files.

**-topmenu** *VIDEO* [**-menu** *VIDEO* *<file list>*] [**-menu** *VIDEO* *<file list>*]...
    (DVD only) Use video file *VIDEO* for the top-level (VMGM) menu. The
    top menu will jump to each of the subsequent [-menu...] videos listed.
    Use this only if you have multiple sub-menus to jump to. You can only
    have one top menu.

**-titlesets**
    (DVD only) Forces the creation of a separate titleset per title. This
    is useful if the titles of a DVD have different video formats,
    e.g. PAL + NTSC or 4:3 + 16:9. If used with menus, there must be a
    **-topmenu** option that specifies a menu file with an entry for each of the
    titlesets.

**-chapters** *INTERVAL*
    (DVD only) Creates a chapter every *INTERVAL* minutes (default 5 minutes:
    without **-chapters**, each movie will be divided into 5-minute chapters).
    This option can be put at any position in a *<file list>* and is valid
    for all subsequent titles until a new **-chapters** option is encountered.
    Using this option may take some time, since the duration of the video is
    calculated.

**-nochapters**
    (DVD only) Don't create chapters for the videos.

*OUT_PREFIX* is the file that will receive the resulting XML.

Usage notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 'xml' command checks to make sure the video filenames you
give it exist, but it does not check whether they are valid for the
chosen disc format. MPEG videos of menus should have the specified
number of buttons for reaching each of the videos, and, if you're
using DVD, should be multiplexed with their corresponding subtitles
using spumux of the dvdauthor 0.6.0 package prior to
authoring using dvdauthor. If you use the 'tovid menu'
component to generate the menu, this should all be handled for you.

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tovid xml -dvd title-1.mpg title-2.mpg title-3.mpg -out My_DVD``
    Make a DVD without a menu. Title 1, 2, and 3 will play in sequence.

``tovid xml -dvd -group chapter-1.mpg chapter-2.mpg chapter-3.mpg -endgroup -out My_DVD``
    Group the file chapter-1|2|3.mpg into one title and make a DVD without a menu.

``tovid xml -dvd -menu main_menu.mpg -chapters 3 movie-1.mpg -chapters 10 movie-2.mpg -out My_DVD``
    Make a DVD with a main menu that points to two movies, with movie-1.mpg
    divided into 3-minute chapters, and movie-2.mpg into 10-minute chapters.


.. _command-dvd:

Command:dvd
===============================================================================

**tovid dvd** takes a dvdauthor XML file (as generated by the **tovid xml**
command) and authors a DVD filesytem. This command can also burn a DVD disc
from either the XML file or from an existing DVD file-system.

To ensure that this script successfully executes, please run it from a
directory with plenty of free space. "Plenty" would be 10 GB for single-layer
discs, and 20 GB for dual-layer discs.  Running this program may slow down your
other applications, due to intense disk activity.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid dvd [OPTIONS] FILE.xml
 tovid dvd [OPTIONS] DVD_DIR

For example:

``tovid dvd -burn MyDisc.xml``
``tovid dvd -burn /path/to/DVD/directory``

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-author**
    Author the DVD described by *FILE.xml*. Overwrites an existing
    directory containing the dvdauthor output if already present.

**-burn**
    Burn a DVD file-system in *DVD_DIR* (must contain a VIDEO_TS folder).

**-device** *DEVICE* (default /dev/dvdrw)
    Burn the disc image to *DEVICE*, the Linux device file-system
    name of your DVD-recorder. Common examples might be /dev/dvdrw,
    /dev/scd1, and /dev/hdc. You can also use a bus/id/lun triple
    such as ATAPI:0,1,0

**-speed** *NUM* (default 1)
    Burn disc at speed *NUM*.

**-label** *DISC_LABEL*
    Uses *DISC_LABEL* as the volume ID. This appears as the mount
    name of the disc on some computer platforms. Must be <=32
    alphanumeric digits without spaces.

**-quiet**
    Limit output to essential messages.

**-noask**
    Don't ask interactive questions and assume answers that will continue
    execution.

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tovid dvd -burn -device /dev/dvdrw foo.xml``
    Author the dvd file-system and burn to /dev/dvdrw. This will
    automatically call dvdauthor to make the file-system. **-author**
    is not explicitly needed. If there's an existing file-system, it
    will be burned.

``tovid dvd -author foo.xml``
    Author the DVD file-system and exit without burning. If the output
    directory given in foo.xml already exists, then the contents are
    removed before authoring. At this point, the DVD can be previewed
    by calling ``xine dvd:/path/to/output/directory``.


.. _command-vcd:

Command:vcd
===============================================================================

**tovid vcd** takes an XML file (which may be generated by **tovid xml**) and
creates a cue/bin (S)VCD image. It can also burn (S)VCD discs.

To ensure that this script successfully executes, please run it from a directory
with plenty of free space. "Plenty" would be about 1 GB. Running this program
may slow down your other applications, due to intense disk activity.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid vcd [OPTIONS] VCDIMAGER.xml

For example:

``tovid vcd -burn MyDisc.xml``

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-overwrite** (default off -- nothing is overwritten)
    Overwrite any existing cue/bin files matching *VCDIMAGER.xml*. Useful
    if you modified the xml file and wish to re-image or burn the new (S)VCD.

**-burn** (default off -- no images are burned)
    Burn the (S)VCD described by *VCDIMAGER.xml*.

**-device** *DEVICE* (default /dev/cdrw)
    Burn the disc image to *DEVICE*, the Linux device file-system
    name of your CD-recorder. Common examples might be /dev/cdrw,
    /dev/scd1, and /dev/hdc.

**-speed** *NUM* (default 12)
    Burn the disc at speed *NUM*.

**-quiet**
    Limit output to essential messages.

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tovid vcd -burn -device /dev/cdrw foo.xml``
    Create the (S)VCD image and burn it to /dev/cdrw. This will
    automatically call vcdxbuild to make the image. If there is an existing
    image, it will be burned.

``tovid vcd -overwrite foo.xml``
    Create the (S)VCD image and exit without burning. If the image
    already exists, then it is removed before re-imaging.


.. _command-postproc:

Command:postproc
===============================================================================

**tovid postproc** is designed to do simple post-processing on MPEG video files, such
as those generated by tovid. It can adjust audio/video sync, and re-quantize
(shrink) without re-encoding.

Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 tovid postproc [OPTIONS] IN_FILE OUT_FILE

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**-audiodelay** *NUM*
    Delay the audio stream by *NUM* milliseconds. Use this if
    your final output has audio that is not synced with the
    video. For example, if the audio comes 2 seconds sooner than
    the video, use **-audiodelay 2000**. Use a negative number for
    audio that comes later than the video.

**-normalize**
    Analyze the audio stream and then normalize the volume of the audio.
    This is useful if the audio is too quiet or too loud, or you want to
    make volume consistent for a bunch of videos. Similar to running
    normalize without any parameters. The default is -12dB average level
    with 0dB gain.

**-amplitude** *NUM[dB]*
    In addition to analyzing and normalizing, apply the gain to the audio
    such that the 'average' (RMS) sound level is *NUM*. Valid values
    range 0.0 - 1.0, with 0.0 being silent and 1.0 being full scale. Use
    *NUMdB[dB]* for a decibel gain below full scale (the default without
    -amplitude is -12dB).

**-shrink** *NUM*
    Shrink the video stream by a factor of *NUM*. May be a decimal
    value. A value of 1.0 means the video will be the same size;
    larger values cause more reduction in size. Beyond 2.0, the
    returns are diminishing.

**-parallel**
    Run all processes in parallel and pipe into multiplexer, should
    increase speed significantly.

**-debug**
    Save output in a temporary file, for later viewing if
    something goes wrong.

Contact
===============================================================================

For further assistance, contact information, forum and IRC links,
please refer to the tovid homepage (http://tovid.wikia.com/).
