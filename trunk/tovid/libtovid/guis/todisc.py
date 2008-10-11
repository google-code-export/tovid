#! /usr/bin/env python
# todisc.py

"""A GUI for the todisc command-line program.
"""

# Get supporting classes from libtovid.metagui
from libtovid.metagui import *
from libtovid import filetypes
import os

# Define a few supporting functions
def to_title(filename):
    basename = os.path.basename(filename)
    firstdot = basename.find('.')
    return basename[0:firstdot]

def strip_all(filename):
    return ''


# List of file-type selections for Filename controls
image_filetypes = [filetypes.all_files]
image_filetypes.append(filetypes.image_files)
image_filetypes.extend(filetypes.match_types('image'))


### --------------------------------------------------------------------
### Main todisc options
### --------------------------------------------------------------------
"""Since todisc has a large number of options, it helps to store each
one in a variable, named after the corresponding command-line option.

Below are defined all the todisc options that will appear in the GUI.
The actual GUI layout comes afterwards...
"""

_menu_title = Text('Menu title', '-menu-title', 'My video collection',
    'Title text displayed on the main menu. Use \\n for a new line '
     'in a multi-line title.')

_files = List('Video files', '-files', None,
    'List of video files to include on the disc',
    Filename())
_titles = List('Video titles', '-titles', None,
    'Titles to display in the main menu, one for each video file on the disc',
    Text())

_group = List('Grouped videos', '-group', None,
    'Video files to group together. Select the video in the list ' \
    'on the left, and add files to group with it by using the file ' \
    'selector on the right',
    Filename())

_dvd = Flag("DVD", '-dvd', True)
_svcd = Flag("SVCD", '-svcd', False)
_ntsc = Flag("NTSC", '-ntsc', True)
_pal = Flag("PAL", '-pal', False)
_out = Filename('Output name', '-out', '',
    'Name to use for the output directory where the disc will be created.',
    'save', 'Choose an output name',
    required=True)

_non_showcase = Flag('Basic thumbnails', '', True,
    'Thumbnail menu links, centred, and as large as space restraints allow')
_showcase = FlagOpt('Showcase', '-showcase', False,
    "Arrange menu links along the outside edges, to leave room for"
    " an optional 'showcase' image or video.  The file entry box"
    " is for an optional image or video file to be showcased in a"
    " large central frame",
    Filename('', '', '', '', 'load', 'Select an image or video file.'),
    enables=['-showcase-seek', '-textmenu', '-quick-menu', '-switched-menus'])

_showcase_seek = Number('Video seek', '-showcase-seek', 2,
    'Play showcase video from the given seek time (seconds).  '
    'Note: switched menus uses the value(s) from "Seek time" '
    'option above, not this one',
    0, 3600, units='seconds')

_title_gap = Number('Space between titles', '-title-gap', 10,
    'Leave this much vertical gap between titles.  '
    'Default is 10 for line buttons, 15 for text-rect buttons.  '
    'This value is applied before the menu is scaled.',
    0, 400, 'spin', 'pixels')

_text_start = Number('Start titles at', '-text-start', 50,
    'Titles will start at this pixel in the vertical axis.  '
    'This value is applied before the menu is scaled.',
    0, 460, 'spin', 'pixels')

_textmenu = FlagOpt("Textmenu", '-textmenu', False,
    'Showcase style text only menu.  Optionally use a "showcase" '
    'image/video, or static/animated background.  Use the '
    '"columns" option to set the number of titles in '
    'column 1 (column 2 will use the remainder).  Note that '
    'column 2 titles are aligned right. '
    'See also quick-menu and switched menu.',
    Number('Columns', '', 13, '', 1, 50))

_quick_menu = Flag("Quick menu", '-quick-menu', False,
    'Ten times faster than normal showcase animation.  '
    'A showcase video is required unless doing switched '
    'menus.  No video thumbs are made.  Not compatible '
    'with wave or rotate options')

_switched_menus = Flag("Switched menus", '-switched-menus', False,
    'This makes a showcase style menu with text menu '
    'links.  The showcased VIDEO or IMAGE will be of each '
    'video "title", and will change as you press the '
    'up/down keys on your remote.  Do not select a '
    'showcase file for this option.  Use with '
    '"Quick menu" option for a huge speed up !')

_showcase_framestyle = Choice('Showcase frame style', '-showcase-framestyle', 'none',
    'This is a showcase style only option.  The "none" option will use '
    'the default frame method, using imagemagick. The "glass" option '
    'will use mplayer to make frames, giving an animated effect.  The ' 
    'glass style can be much faster - especially if used without '
    '-rotate and -wave options',
    'none|glass')

_showcase_geo = Text('Showcase image position (XxY)', '-showcase-geo', '',
    'This is a showcase style only option.  Enter the position of the '
    'top left corner of the showcase image: e.g. "200x80".  This '
    'value is applied to the video *before* is is scaled.')

_bg_color = Color('Menu background color', '-bg-color', 'white',
    'Color of the menu background.  ' 
    'Default if not enabled: ntsc color-safe black (#101010).  '
    'Note: the color turns out MUCH lighter than the one you choose, '
    'so pick a VERY dark version of the color you want.',
    toggles=True)

_background = Filename('Image or video', '-background', '',
    'Image or video displayed in the background of the main menu',
    'load', 'Select an image or video file',
    filetypes=image_filetypes)

_bgvideo_seek = Number('Video seek', '-bgvideo-seek', 2,
    'Play background video from the given seek time (seconds)',
    0, 3600)

_bgaudio = Filename('Audio', '-bgaudio', '',
    'Audio file to play while the main menu plays.  '
    'Static menus use default audio length of 20 seconds.  ' 
    'Change with "Menu length" on "Menu" tab.  '
    'Use almost any filetype containing audio.',
    'load', 'Select an audio file')

_bgaudio_seek = Number('Audio seek', '-bgaudio-seek', 2,
    'Play background audio from the given seek time (seconds)',
    0, 3600)

_menu_audio_fade = Number('Fade in audio', '-menu-audio-fade', 1,
    'Number  of  sec to fade given menu audio in and out '
    '(default: 1.0 seconds). Use a fade of "0" for no fade.',
    0, 10)

_menu_fade = FlagOpt('Fade in menu', '-menu-fade', False,
    'Fade the menu in and out. The background will fade in first, then '
    'the title (and mist if called for), then the menu thumbs and/or titles.  '
    'The fadeout is in reverse order.  The optional numerical argument '
    'is the length of time the background will play before the menu '
    'begins to fade in.',
    Number(default=0.0, min=0.0, max=60.0, units='seconds', style='scale')
)

_transition_to_menu = Flag('Transition to menu', '-transition-to-menu', False,
    'A convenience option for animated backgrounds: the background '
    'will become static at the exact point the thumbs finish '
    'fading in.  This menu does not loop '
    'unless you pass -loop VALUE (authoring tab).'),

_intro = Filename('Intro video', '-intro', '',
    'Video to play before showing the main menu.  At present this must '
    'be a DVD compatible video at the correct resolution etc.  Only 4:3 '
    'aspect is supported.',
    'load', 'Select a video file')

_static = Flag('Static menus', '-static', False,
    'Create still-image menus; takes less time. For duration of background '
    'audio for static menus, use "menu length" on the "Menu" tab')

_menu_length = Number('Menu length', '-menu-length', 20,
    'Duration of menu in seconds.  The length of the menu will also set '
    'the length of background audio for a static menu',
    0, 120, toggles=True)

_submenus = Flag('Submenus', '-submenus', False,
    'Create a submenu for each video title; takes more time.')

_submenu_length = Number('Submenu length', '-submenu-length', 14,
    'The length of the submenu. If doing static submenus and using audio '
    'for the submenu, this will be the length of the submenu audio',
    0, 80, toggles=True)

_ani_submenus = Flag('Animated submenus', '-ani-submenus', False,
    'Create an animated submenu for each video.  '
    'Submenu links lead to chapter points.')

_submenu_audio_fade = Number('Audio fade', '-submenu-audio-fade', 1,
    'Number of seconds to fade given submenu audio in and out (default=1).',
    0, 10)

_submenu_audio = List('Audio', '-submenu-audio', None,
    'File(s) that will play as background audio for each submenu.  '
    'Use a single file for all submenus, or 1 file per submenu.  '
    'Any file containing audio can be used.',
    Filename())

_submenu_background = List('Image(s)', '-submenu-background', None,
    'Background image(s) for the submenus(s). Single value or list',
    Filename(filetypes=image_filetypes))

_submenu_titles = RelatedList('-files', 'one',
    List('Titles', '-submenu-titles', None,
        'Submenu titles for each video.  '
        'Use \\n for a new line in a multi-line title.'),
    filter=strip_all)

_chapter_titles = RelatedList('-files', 'many',
    List('Chapter titles', '-chapter-titles', None,
        'Chapter titles for each video.  Use \\n for a new line in '
        'a multi-line title.  Number of titles given must equal the '
        'number of capters given for that video.'))


_jobs = Number('Number of jobs to run simultaneously', '-jobs', 0,
    'Leave this value at 0 if you wish the default, which is to run '
    'as many jobs as processors found. Use this option if you wish '
    'to limit or increase this number.  ', 0, 32)
_keep_files = Flag('Keep intermediate files on exit', '-keep-files', False)
_no_ask = Flag('No prompts for questions', '-no-ask', False)
_no_warn = Flag('No pause at warnings', '-no-warn', False)
_grid = Flag('Grid preview', '-grid', False,
    'Show a second preview image with a grid and numbers that will help in '
    'finding coordinates for options that might use them')
_use_makemenu = Flag('Use makemenu', '-use-makemenu', False,
    'Create menus using the makemenu script instead of todisc')

_slides = List('Images for slideshow one', '-slides', None,
    "Image files for the slideshow",
    Filename(filetypes=image_filetypes))

_submenu_slide_total = SpacedText('Number of slides shown on submenu',
    '-submenu-slide-total', '',
    'Use this many slides for making the slideshow submenus. '
    'The default is to use all the slides given.  '
    'Use a single value for all or list one value per submenu.',
    toggles=True)

_slide_transition = Choice('Transition type', '-slide-transition', 'crossfade',
    'The type of fade transition between slides in an '
    'animated slideshow menu.  Be sure  the  menu  length '
    'is long enough to support the 1 second transitions '
    'between the slides.  The length is determined by  '
    '1)  the length  of  the -bgaudio AUDIO  2) the '
    'length given with -menu-length DURATION.  '
    '* See Menu tab for menu length option *.',
    'crossfade|fade')

_slide_border = Number('Slide border', '-slide-border', 100,
    'Use a border around animated slideshow slides (default: 100 pixels).',
    0, 200, toggles=True)

_slide_frame = Number('Slide frame', '-slide-frame', 12,
    'Use a frame around the animated slideshow slides (default: 12).',
    0, 20, toggles=True)

_no_confirm_backup = Flag('No reminder prompt for backing up files',
    '-no-confirm-backup', False, 'Todisc prompts you for a "yes" '
    ' to show you have taken backup precations.  This option '
    'disables that prompt.')


_background_slideshow = Flag("Background", '-background-slideshow', False,
    'This option is only for multiple slideshows, '
    '(or mixed video and slideshow menus). It uses the '
    'animated slideshow as the background video')

_showcase_slideshow = Flag("Showcase", '-showcase-slideshow', False,
    'This option is only for multiple slideshows, '
    '(or mixed video and slideshow menus).  It uses the '
    'animated slideshow as the showcase video')

_slideshow_menu_thumbs = List('Menu slide thumbs', '-slideshow-menu-thumbs', None,
    'Slides for the menu thumbnail.  For multiple slideshows or '
    'mixed slideshows/videos only.',
    Filename(filetypes=image_filetypes))

_use_dvd_slideshow = FlagOpt('Use dvd-slideshow program', '-use-dvd-slideshow', False,
    'Use the "dvd-slideshow" program to make the animated '
    'slideshow. You need of course to have installed this program '
    'to use this. You only need this for special effects like the '
    '"Ken Burns effect" otherwise todisc can do the job well '
    'and fast on its own. The optional file is the dvd-slideshow '
    'file you would need for non-todisc options, otherwise '
    'todisc will make the file for you. Using this option will '
    'void many todisc slideshow options.',
    Filename(action='load', help='Select the dvd-author configuration file.'))

_slides_to_bin = List('Slides to "bin"', '-slides-to-bin', None,
    '"Binning" resizes the image to 640x480 using a "box" '
    'filter, which reduces "signal to noise ratio"'
    'Use in conjuction with the next option for burring, '
    'to achieve stronger denoising',
    Filename(filetypes=image_filetypes))

_slides_to_blur = List('Slides to blur', '-slides-to-blur', None,
    'Blurring the image can reduce noise such as "ringing" '
    'effects.  Use values between 0x0.1 and 0x0.9 for best '
    'results.  Enter a single value or 1 value for each slide '
    'to be blurred.',
    Filename(filetypes=image_filetypes))

_slide_blur = List('Slide blur amount', '-slide-blur', '',
    'How much to blur each slide given with "Slides to blur".  '
    'Use a single value, or a list with one value per slide given'
    'The format is {radius}x{sigma} and the default is 0x0.2.  Using '
    'values between 0x0.1 and 0x0.9 is probably the best range.',
    Filename())

_thumb_shape = Choice('Thumb shape', '-thumb-shape', 'normal',
    'Apply a shaped transparency mask to thumbnail videos. '
    'Note: to disable the "mist" background '
    'behind each thumb, use see "Thumb mist" section below.',
    'normal|oval|plectrum|egg')

_opacity = Number('Thumbnail opacity', '-opacity', 100,
    'Opacity  of thumbnail videos as a percentage '
    '(no percent sign).  Less than 100(%) '
    'is semi-transparent.  Not recommended with dark backgrounds.',
    1, 100, 'spin', toggles=True)

_blur = Number('Blur', '-blur', 4,
    'The amount of feather blur to apply to the thumb-shape.  '
    'Default is 4.0 which will more or less keep the shape, '
    'creating transparency at the edges.  Choose float or '
    'integer values between 0.1 and 5.0',
    1, 5, 'spin')

_3dthumbs = Flag('Create 3D thumbs', '-3dthumbs', False,
    'This will give an illusion of 3D to the thumbnails: '
    'dynamic lighting on rounded thumbs, and a  raised '
    ' effect on rectangular thumbs')

_rotate_thumbs = SpacedText('Rotate Thumbs (list)', '-rotate-thumbs', '',
    'Rotate  thumbs  the  given amount in degrees - can be positive '
    'or negative.  There must be one value for each file given with '
    'files.  If the values are not the same distance from zero, the '
    'thumbs will be of  different sizes as images are necessarily '
    'resized *after* rotating.')

_wave = Flag('Wave effect for showcase thumb', '-wave', False,
    'Wave effect for showcase image|video.  Alters thumbs along a sine '
    'wave.  This will pass a wave arg of -20x556, producing a gentle '
    'wave with a small amount of distortion.  To use other values you '
    'will need to use the "tovidopts" box on the first panel.  '
    'See man todisc for details.')

_rotate = Number('Rotate Showcase thumb', '-rotate', 0,
    'Rotate the showcase image|video clockwise by this number of degrees.',
    -30, 30, 'spin')

_thumb_mist_color = FlagOpt("No thumb mist", '-thumb-mist-color', False,
    'Do not use mist behind thumbs (not a showcase option).  Warning: '
    'might cause contrast problems (use a large bold font)',
    Color('Thumb mist color', '', 'white',
        'Color of mist behind thumbnails (not a showcase option). ' 
        'Default if not enabled: white')
)

_tile3x1 = Flag('1 row of 3 thumbs', '-tile3x1', False,
    'Use a montage tile of 3x1 instead of the usual 2x2 '
    '(3 videos only).  Not a showcase option.')

_tile4x1 = Flag('1 row of 4 thumbs', '-tile4x1', False,
    'Use a montage tile of 4x1 instead of the usual 2x2 '
    '(4 videos only).  Not a showcase option.')

_align = Choice('Montage alignment', '-align', 'north',
    'Controls positioning of the thumbnails and their titles.  '
    'With some arrangements this will have limited effects however.',
    'north|south|east|west|center')

_seek = SpacedText('Thumbnail seek', '-seek', '',
    'Play thumbnail videos from the given seek time (seconds).  '
    'A single value or space separated list, 1 value per video.  '
    'Also used for seeking in switched menus.')


_menu_font = Font('Font', '-menu-font', 'Helvetica',
    'The font to use for the menu title', toggles=True)
_menu_fontsize = Number('Font size', '-menu-fontsize', 30,
    'The font size to use for the menu title',
    0, 80, toggles=True)
_title_color = Color('Font color', '-title-color', '#CDC0B0',
    'The font color to use for the menu title', toggles=True)
_title_stroke = Color('Stroke color', '-title-stroke', 'gray',
    'Outline color for the main menu font.', toggles=True,
    initialcolor="gray")

_menu_title_geo = Choice('Title position', '-menu-title-geo', 'south',
    'The position of the menu title',
    'north|south|west|east|center')
_menu_title_offset = Text('Title offset', '-menu-title-offset', '+0+50',
    'Menu title position as an offset (in pixels) from '
    'the N/S/E/W "Title position".  Use +X+Y syntax.  This '
    'value is applied to the video *before* is is scaled.',
    toggles=True)
_text_mist = Flag('Text mist', '-text-mist', False,
    'Use "mist" behind the menu title (helps with contrast).')
_text_mist_color = Color('Text mist color', '-text-mist-color', 'white',
    'Color of the mist behind the menu title.', toggles=True)
_text_mist_opacity = Number('Text mist opacity', '-text-mist-opacity', 60,
    'The opacity of the mist behind the menu title.',
    1, 100, 'spin', toggles=True)
_title_opacity = Number('Title opacity', '-title-opacity', 100,
    'The opacity of the menu title.',
    0, 100, toggles=True)
_titles_font = Font('Font', '-titles-font', 'Helvetica',
    'The font to use for the video titles', toggles=True)
_titles_fontsize = Number('Font size', '-titles-fontsize', 12,
    'The font size to use for the video titles.  '
    'Default size varies depending on options chosen.',
    0, 80, toggles=True)
_titles_color = Color('Font color', '-titles-color', '#CDC0B0',
    'The font color to use for the video titles', toggles=True)
_titles_stroke = Color('Stroke Color', '-titles-stroke', '#CDC0B0',
    'The color to use for the video titles font outline (stroke)',
    toggles=True)
_showcase_titles_align = Choice('Video(s) title alignment',
    '-showcase-titles-align', 'none',
    'This is a showcase style only option.  Default is to center '
    'the text above the thumbnails.  This option will align the '
    'titles either to the left (west), right (east), or center.  '
    'Leave at "none" to let todisc sort it out for you.',
    'west|east|center|none')
_titles_opacity = Number('Titles opacity', '-titles-opacity', 100,
    'The opacity of the video titles.',
    0, 100, toggles=True)
_submenu_font = Font('Font', '-submenu-font', 'Helvetica',
    'The font to use for the Submenu menu titles', toggles=True)
_submenu_fontsize = Number('Font size', '-submenu-fontsize', 30,
    'The font size to use for the submenu title',
     0, 80, toggles=True)
_submenu_title_color = Color('Font color', '-submenu-title-color', '#CDC0B0',
    'The font color to use for submenu title(s)', toggles=True)
_submenu_stroke = Color('Stroke color', '-submenu-stroke', '#101010',
    'The color for the submenu font outline (stroke).', toggles=True)
_submenu_title_opacity = Number('Submenu title opacity',
    '-submenu-title-opacity', 100,
    'The opacity of the submenu title.',
    0, 100, toggles=True)
_chapter_font = Font('Font', '-chapter-font', 'Helvetica',
    'The font to use for the chapter titles', toggles=True)
_chapter_fontsize = Number('Font size', '-chapter-fontsize', 14,
    'The font size to use for the chapter titles',
    0, 80, toggles=True)
_chapter_color = Color('Font color', '-chapter-color', '#101010',
    'The color for the chapters font.', toggles=True)
_chapter_stroke = Color('Stroke color', '-chapter-stroke',
    '#101010', 'The color for the chapters font outline (stroke).',
    toggles=True)
_chapter_title_opacity = Number('Chapter titles opacity',
    '-chapter-title-opacity', 100,
    'The opacity of the chapter titles.',
    0, 100, toggles=True)

_widescreen = Choice('Widescreen', '-widescreen', 'none',
    'This will output a <video widescreen=nopanscan /> tag '
    '(for example) for the dvdauthor xml file.  It affects all '
    'videos in the titleset.  Use in conjunction with "Aspect ratio" '
    'if your dvd player is cropping your videos.  '
    'Leave this at "none" to not output a widescreen tag',
    'nopanscan|noletterbox|none')
_aspect = Choice('Aspect ratio', '-aspect', 'none',
    'This will output a <video aspect WIDTH:HEIGHT /> tag for the '
    'dvdauthor xml file.  It will affect all videos in the titleset.  '
    'Leave this at "none" to let dvdauthor figure it out for you',
    '4:3|16:9|none')
_audio_lang = SpacedText('Audio', '-audio-lang', '',
    'Single value or list of language codes for audio')
_subtitles = SpacedText('Subtitles', '-subtitles', '',
    'Single value or list')
_button_style = Choice('Style', '-button-style', 'none',
    'Style or shape of the buttons seen when playing the DVD '
    'menu.  "rect": rectangle around the thumbs, "text": uses '
    'the title text, "text-rect": rectangle around the title text, '
    '"line": line underneath title.  The "line" style is showcase only'
    ', and the "text" buttons can not be used with "showcase" menus.'
    'Leave at "none" to let todisc pick the most appropriate style. ',
    'rect|line|text|text-rect|none')

_highlight_color = Color('Highlight color', '-highlight-color', '#266CAE',
    'Color for the menu buttons the dvd remote uses to navigate.',
    toggles=True)
_select_color = Color('Selection color', '-select-color', '#DE7F7C',
    'Color for the menu buttons the dvd remote uses to select.',
    toggles=True)
_outlinewidth = Number('Outlinewidth for spumux', '-outlinewidth', 14,
    'For spumux outlinewidth variable.  This option helps if spumux '
    'fails because of a large gap between button words or characters.',
    0, 20, toggles=True)

_playall = Flag('"Play all" button', '-playall', False,
    'Create a "Play All" button that jumps to the 1st title and plays '
    'all the videos in succession before returning to the main menu.')
_videos_are_chapters = Flag('Each video is a chapter',
    '-videos-are-chapters', False,
    'A button will be made on the main menu for each video which You '
    'can use as a chapter button .  Selecting any video will play '
    'them all in order starting with the selected one.' )
_burn = Flag('Burn project on completion', '-burn', False)
_speed = Number('Burning speed', '-speed', 8,
    'Speed for burning',
    0, 30, toggles=True)
_device = Filename('Device to use for burning', '-device', '/dev/dvdrw',
    'Select or type your burning device (default: /dev/dvdrw)',
    'load', 'Select or type your burning device')


### ---------------------------------------------------------------------------
### Main GUI layout and panel construction
### ---------------------------------------------------------------------------
"""The todisc GUI is laid out using panels and tabs for logical grouping.
"""

main = VPanel("Main",
    _menu_title,

    Tabs('Input files',
        RelatedList(_files, 'one', _titles, filter=to_title),
        RelatedList('-files', 'many', _group),
    ),

    HPanel('',
        FlagGroup('Menu options', 'normal', _static, _submenus, side='left'),
        FlagGroup('Format', 'exclusive', _dvd, _svcd, side='left'),
        FlagGroup('TV System', 'exclusive', _ntsc, _pal, side='left'),
    ),


    VPanel('Menu style',
        FlagGroup('', 'exclusive', _non_showcase, _showcase),
        HPanel('Showcase options', _textmenu, _quick_menu, _switched_menus)
    ),
    VPanel('Menu backgrounds',
        _background,
        _bgaudio,
    ),
    _out
)


showcase_options = VPanel('Showcase options',
    _showcase_seek,
    _showcase_framestyle,
    _showcase_geo,
    _showcase_titles_align,
    _title_gap,
    _text_start,
)


main_menu_backgrounds = VPanel('Backgrounds',
    _bg_color,
    _bgvideo_seek,
    _bgaudio_seek,
    _menu_audio_fade,
)


menus = Tabs('Menus',
    VPanel('Main menu',

        _menu_length,

        Tabs('Extra',
            showcase_options,
            main_menu_backgrounds,
            VPanel("Effects", _menu_fade, _intro)
            ),
    ),

    VPanel('Submenus',
        _submenu_length,
        _ani_submenus,
        _submenu_audio_fade,

        Tabs('Extra',
            HPanel('Backgrounds',
                _submenu_audio,
                _submenu_background,
            ),
            _submenu_titles,
            _chapter_titles,
        ),
    ),
)



tab_list = []
slideshow_panel = Tabs('Slideshow',
    VPanel('General options',
        Text('Title', '-titles', '', 'Title for this slideshow.'),
        _slides,
        FlagGroup("", 'exclusive',
            Flag('Animated with transitions', '', True,
                'This is the default if you are not doing a static '
                'menu.  The slides transition one to the next, using '
                'the type of transition selected in "Transition type"'),
            Flag('Static with "Polaroid stack" menu', '-static', False,
                'This puts the  slides  onto  the  background in '
                '"random" locations with random rotations, making it '
                'look like a scattered stack of photos. This is the '
                'same as setting -static on the Main tab.'),
        ),
        Number('Number of slides shown on menu', '-menu-slide-total', 0,
            'Use this many slides for making the slideshow menu. '
            'The default is to use all the slides given.',
            0, 100, toggles=True),
        _submenu_slide_total,
        VPanel('Animated slideshow options',
            HPanel('',
                _slide_transition,
                HPanel('', _slide_border, _slide_frame),
            ),
        ),
        _no_confirm_backup,
    ),
    VPanel('Advanced options',
        FlagGroup('Use slideshow as background or showcase video ',
            'exclusive',
            _background_slideshow, _showcase_slideshow
        ),
        _slideshow_menu_thumbs,
        _use_dvd_slideshow,
    ),
    VPanel('Denoising options', _slides_to_bin, _slides_to_blur, _slide_blur),
)

tab_list.append(slideshow_panel)

for num in range(2,  13):
    title_str = 'Images for slideshow ' + str(num)
    next_panel = VPanel(str(num),
        Text('Title', '-titles', '',
            'Title for this slideshow. Leave empty if doing a single slideshow.'),
        List(title_str, '-slides', None,
            'Image files for the slideshow.',
            Filename()),
        )
    tab_list.append(next_panel)

slideshows = Tabs('Slideshows', *tab_list)


thumbnails = VPanel("Thumbnails",
    _thumb_shape,
    _opacity,
    _blur,
    _3dthumbs,
    _rotate_thumbs,
    _wave,
    _rotate,
    _thumb_mist_color,
    FlagGroup('Special thumb arrangements', 'exclusive', _tile3x1, _tile4x1),
    _align,
    _seek,
)
from libtovid.guis import tovid

behavior = VPanel("Behavior",
    HPanel('',
        VPanel('', _jobs, _keep_files, _no_ask),
        VPanel('', _no_warn, _grid, _use_makemenu),
    ),
    SpacedText('Custom todisc options', '', '',
         'Space-separated list of custom options to pass to todisc.'),
    SpacedText('Custom tovid options', '', '',
         'Space-separated list of custom options to pass to tovid.'),
    Tabs('tovid options',
        tovid.BASIC_OPTS,
        tovid.VIDEO,
        tovid.AUDIO,
        tovid.BEHAVIOR,
    )
)


text = VPanel('Text/Font',
    HPanel('',
        VPanel('Menu titles',
            _menu_font,
            _menu_fontsize,
            _title_color,
            _title_opacity,
            _title_stroke,
        ),
        VPanel('Video titles',
            _titles_font,
            _titles_fontsize,
            _titles_color,
            _titles_opacity,
            _titles_stroke,
        )
    ),
    _menu_title_geo,
    _menu_title_offset,
    VPanel("Mist", _text_mist, _text_mist_color, _text_mist_opacity),

    HPanel('',
        VPanel('Submenu titles',
            _submenu_font,
            _submenu_fontsize,
            _submenu_title_color,
            _submenu_title_opacity,
            _submenu_stroke,
        ),
        VPanel('Chapter titles',
            _chapter_font,
            _chapter_fontsize,
            _chapter_color,
            _chapter_title_opacity,
            _chapter_stroke,
        )
    ),
)


authoring = Tabs('Authoring',
    VPanel('General authoring options',
        VPanel('Play control',
            Number('Number of chapters', '-chapters', 6,
                'The number of chapters to use for all videos. If you  '
                'wish to use a different value for each video, or supply '
                'chapters in HH:MM:SS format, use the '
                '"Advanced chapter options" tab.  That is also where to '
                'configure grouped videos.',
                0, 60),
            FlagGroup('', 'exclusive',
                Flag('Chain all videos together', '-chain-videos', False,
                    'This option will "chain" videos so they play '
                    'sequentially until the last, which will return to '
                    'the menu.  You can also specify individual videos to '
                    'behave like this by using the text box at the right. '),
                FlagOpt('Chain selected videos together', '-chain-videos', False, 
                    'Enable this option and use the box at right to indicate the '
                    'number of the video you wish to "chain" to the next, so '
                    'they play sequentially before returning to the menu. '
                    'You can use single integers or indicate a range with a '
                    '"-" separator. Example of a range: "1-2 4-6" (no quotes). '
                    'This will play video 1 through video 3 before returning '
                    'to the menu, and the same for video 4 through video 6.',
                    Text(''),
                ),
            ),
            _playall,
            _videos_are_chapters,
            FlagGroup('', 'exclusive',
                FlagOpt('Pause', '', False, 'Pause in seconds at end of '
                    'menu.  Or leave this value at "10" and use the '
                    '"Indefinite pause item below.',
                    Number('', '-loop', 10, '', 0, 30),
                ),
                Flag('Indefinite pause', '-loop', False,
                'Pause indefinitely at the end of the menu.'),
            ),
        ),
        VPanel('Aspect', _widescreen, _aspect),
        HPanel('Language(s)', _audio_lang, _subtitles),
        VPanel('Buttons',
            _button_style,
            HPanel('', _highlight_color, _select_color, _outlinewidth),
        ),
    ),
    VPanel('Advanced chapter options',
        RelatedList('-files',
            'many',
            List('Chapters: use 1 line per video. Load files 1st !',
                '-chapters', None,
                'Number of chapters (integer) or HH:MM:SS string for each '
                'video.  For grouped videos, use a "+" separator for joining '
                'the chapter string of each grouped video.'
                ''
                '  An example chapter string using HH:MM:SS format: '
                '  00:00:00,00:05:00,00:10:00.  An example of 2 grouped videos: '
                '00:00:00,00:05:00+00:05:00,00:10:00.  '
                'When using HH:MM:SS format the 1st chapter MUST be 00:00:00.'),
            filter=strip_all
        )
    )
)

burning = VPanel("Burning", _burn, _speed, _device)


### --------------------------------------------------------------------

def run():
    app = Application('todisc',
        main, menus, behavior, thumbnails, text, slideshows, authoring, burning)
    gui = GUI("todiscgui", 640, 800, app)
    gui.run()

if __name__ == '__main__':
    run()
