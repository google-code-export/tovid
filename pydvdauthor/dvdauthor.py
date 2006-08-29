#!/usr/bin/python
# -=- encoding: latin-1 -=-

"""Module that implements a set of classes which aid in creation of a valid
dvdauthor-formatted .xml file.

Object tree layout:

Disc
 |-- VMGM
 |    `-- Menu(s)
 |         `-- Button(s)
 `-- Titleset(s)
      |-- Menu(s)
      |    `-- Button(s)
      `-- Title(s)

Adding a Titleset in the Disc object, or adding a Button to a Menu is done
in a consistent manner across the different object types. For example:

    Disc.add_titleset(Titleset)

    Titleset.add_menu(Menu)

    Menu.add_button(Button)

etc.

Note that a VMGM menu is a subclass of a Titleset (more restricted), and a
Menu object is a subclass of a Title, extended only by the fact that it can have
buttons.

You must be aware of the inner restrictions of `commands` inside a Menu or a Title
object. These are restrictions imposed by the dvdauthor software itself. Read the
man pages for more details.

Cross-referencing is done with IDs. Each object, be it Titleset, Menu, Title or
VMGM, has it's own randomly-generated ID (stored in object.id). You must use these
in the commands to jump from a title to another, or when you call a menu. Ex:

  command = "jump titleset %s title %s" % (mytitleset.id, thistitle.id)

When rendering, the engine will replace the IDs with the actual number values of
the menus or titles you specified. This enables dynamic creation of DVD, without
the worry of falling in a "what's that number ?'" hell.
"""

import random


  
class Disc:
    """dvdauthor XML file generator.

    This is the highest level object in the tree. See module documentation."""
    def __init__(self, name=None):
        """Highest level object, which includes all others.

        name -- Just a name for you to remember. It will be inserted as a comment
                in the .XML file
        """
        self.id = _gen_id()
        self.titlesets = []
        self.jumppad = False
        self.vmgm = None
        self.name = name

    def add_titleset(self, titleset):
        """Add the Titleset"""
        self.titlesets.append(titleset)

    def render_xml(self, output_dir):
        """Return XML file as a string

        output_dir -- specifies where to output the project
        """
        pass

    def dvdauthor_execute(self, output_dir):
        """Writes the XML file to disk and run dvdauthor on it to produce the
        desired output.

        output_dir -- specifies where to output the project

        This function calls render_xml()
        """
        pass

    def set_jumppad(self, jumppad=True):
        """Set dvdauthor jumpad tag.

        jumppad -- bool.

        If you do not call this function with a True value, the jumppad is
        by default disabled.
        """
        self.jumppad = jumppad

    def set_vmgm(self, vmgm):
        """Set the VMGM menu for the disc.

        NOTE: we use the 'set_' prefix, as opposed to 'add_', because there
              is only one VMGM menu by disc.
        """
        self.vmgm = vmgm


class Titleset:
    """Represent a Titleset on the DVD.

    You can add Title(s), and Menu(s) (including buttons) to a Titleset.

    Note that this is just a container for menus and titles, and has not itself
    video files associated. It's the way the DVD structure works. Read on about
    official DVD specs to learn more.
  
    """

    def __init__(self, name=None):
        """Create a Titleset instance.

        name -- Just a name for you to remember. It will be inserted as a comment
                in the .XML file
        """
        self.id = _gen_id()
        self.name = name
        self.menus = []
        self.titles = []
        self.audio_langs = []
    
    def add_menu(self, menu):
        """Add a menu to the Titleset.

        You can only add menus that have no 'entry' field or where their 'entry'
        field is one of:

            root
            subtitle
            audio
            angle
            ptt
        """
        self.menus.append(menu)

    def add_title(self, title):
        """Add a title to the Titleset."""
        self.titles.append(title)

    def add_audio_lang(self, lang):
        """Set the language for the next audio track in the video files of the
        Title(s) you've added, or you're going to add.

        The language codes must be one in the list you'll find at:

            http://sunsite.berkeley.edu/amher/iso_639.html

        Validation is done in the function call to ensure you specify something
        that exists.
        """
        self.audio_langs.append(_verify_lang(lang))


class VMGM(Titleset):
    """Represent the VMGM menu structure on the DVD.

    Note that this is just a container for menus, and has not itself video files
    associated.

    Differences with the Titleset and the 'entry' fields in the Menus it includes
    that cannot have the same values.
    """
    
    def __init__(self, name=None):
        """Create the VMGM menu instance (top level menu) for the DVD.

        name -- Just a name for you to remember. It will be inserted as a comment
                in the .XML file
        """
        Titleset.__init__(self, name)
        # We don't need this for VMGM, since there are no titles in there, only
        # menus.
        del(self.titles)
        self.subpictures = []

    def add_menu(self, menu):
        """Add a menu to the VMGM top-level menu.
        
        You can only add menus that have no 'entry' field or where their 'entry'
        field is one of:

            title
        """
        pass

    def add_subpicture_lang(self, lang):
        """Add the language definitions for the subtitles in the videos.

        The language codes must be one in the list you'll find at:

            http://dvdauthor.sourceforge.net/doc/languages.html

        Validation is done in the function call to ensure you specify something
        that exists.
        """
        self.subpictures.append(_verify_lang(lang))

class Title:
    """Represent a Title on the DVD. This includes one or more .vob (or .mpg)
    files.
    """

    def __init__(self, name=None, pause=None):
        """Create a Title instance.

        name -- Just a name for you to remember. It will be inserted as a comment
                in the .XML file
        pause -- = None, if you don't want the video to pause after having played
                   all the .vob (or .mpg) files in the Title
                 = 1 to 254, in seconds, if you want to pause for that number
                   of seconds after the Title
                 = 'inf', if you want to pause indefinitely, or until someone
                   presses the 'Next' button on the DVD remote control.
        """
        self.id = _gen_id()
        self.name = name
        self.pause = pause
        self.videofiles = []
        self.cells = []
        self.pre_cmds = None
        self.post_cmds = None

    def add_video_file(self, file, chapters=None, pause=None):
        """Add a .vob (or .mpg) file to the Title.
        """
        self.videofiles.append({'file': file, 'chapters': chapters,
                                'pause': pause})

    def add_cell(self, start_stamp, end_stamp, chapter=False, program=False,
                 pause=None):
        """Add a cell definition.

        start_stamp -- see dvdauthor documentation (quite undocumented)
        end_stamp -- idem.
        chapter -- bool (see docs?)
        program -- bool (see docs?)
        pause -- see Title.__init__() for documentation
        """
        self.cells.append({'start': start_stamp, 'end': end_stamp,
                           'chapter': chapter, 'program': program,
                           'pause': pause})
    
    def set_pre_commands(self, commands):
        """Set the commands executed before the Title plays.

        See dvdauthor's man page for a detailed explanation of the language
        used herein.

        commands -- this should be an array 
        """
        self.pre_cmds = commands

    def set_post_commands(self, commands):
        """Set the commands executed after the Title has played.

        commands -- see Title.set_pre_commands() for documentation
        """
        self.post_cmds = commands



class Menu(Title):
    """Represent a Menu on the DVD. This includes one or more .vob (or .mpg)
    files.
    """

    def __init__(self, name=None, entry=None, pause=None):
        """Create a Menu instance.

        name -- Just a name for you to remember. It will be inserted as a comment
                in the .XML file
        entry -- one of:
                      root, subtitle, audio, angle, ptt
                 if you intent to add it to a Titleset object, or one of:
                      title
                 if you intent to add it to a VMGM object.
        pause -- See the Title.__init__() documentation
        """
        Title.__init__(self, name, pause)
        # TODO: deal with entry only here, because Title doesn't have anything
        #       to do with entry points.
        self.entry = entry
        self.buttons = []
    
    def set_button_commands(self, commands, button=None):
        """Set the commands executed when a button is pressed in the menu.

        commands -- see Title.set_pre_commands() for documentation
        button -- leave to None for automatic numbering. Otherwise, specify
                  a string which must have the same reference in the video
                  files you're going to add to the menu.

        If you specify the button name, then you can overwrite it's value in
        the course of your program. If you do not specify it's value, you
        cannot modify what was previously entered (unless you dive into the
        dvdauthor module code :).
        """
        if button == None:
            self.buttons.append([None, commands])
        else:
            # Go set the right button's value
            nowset = False
            for x in self.buttons:
                if (x[0] == button):
                    x[1] = commands
                    nowset = True
            if not nowset:
                self.buttons.append([button, commands])


###
### Helper functions
###



def _gen_id():
    """Generates a random ID, which will be used in the commands strings
    for 'jump' and 'call' cross-referencing.
    """
    return "ID:%08x" % random.randint(0, 65535*65535)


def _verify_lang(lang):
    nlang = lang.upper()
    if not language_codes.has_key(nlang):
        raise KeyError, "Language codes must be one in the list found at: "\
              "http://sunsite.berkeley.edu/amher/iso_639.html"

    return (lang.lower(), language_codes[nlang])

###
### Language codes definitions, from:
### http://sunsite.berkeley.edu/amher/iso_639.html
###
language_codes = {'AA': 'AFAR',
                  'AB': 'ABKHAZIAN',
                  'AF': 'AFRIKAANS',
                  'AM': 'AMHARIC',
                  'AR': 'ARABIC',
                  'AS': 'ASSAMESE',
                  'AY': 'AYMARA',
                  'AZ': 'AZERBAIJANI',
                  'BA': 'BASHKIR',
                  'BE': 'BYELORUSSIAN',
                  'BG': 'BULGARIAN',
                  'BH': 'BIHARI',
                  'BI': 'BISLAMA',
                  'BN': 'BENGALI;BANGLA',
                  'BO': 'TIBETAN',
                  'BR': 'BRETON',
                  'CA': 'CATALAN',
                  'CO': 'CORSICAN',
                  'CS': 'CZECH',
                  'CY': 'WELSH',
                  'DA': 'DANISH',
                  'DE': 'GERMAN',
                  'DZ': 'BHUTANI',
                  'EL': 'GREEK',
                  'EN': 'ENGLISH',
                  'EO': 'ESPERANTO',
                  'ES': 'SPANISH',
                  'ET': 'ESTONIAN',
                  'EU': 'BASQUE',
                  'FA': 'PERSIAN (farsi)',
                  'FI': 'FINNISH',
                  'FJ': 'FIJI',
                  'FO': 'FAROESE',
                  'FR': 'FRENCH',
                  'FY': 'FRISIAN',
                  'GA': 'IRISH',
                  'GD': 'SCOTS GAELIC',
                  'GL': 'GALICIAN',
                  'GN': 'GUARANI',
                  'GU': 'GUJARATI',
                  'HA': 'HAUSA',
                  'HI': 'HINDI',
                  'HR': 'CROATIAN',
                  'HU': 'HUNGARIAN',
                  'HY': 'ARMENIAN',
                  'IA': 'INTERLINGUA',
                  'IE': 'INTERLINGUE',
                  'IK': 'INUPIAK',
                  'IN': 'INDONESIAN',
                  'IS': 'ICELANDIC',
                  'IT': 'ITALIAN',
                  'IW': 'HEBREW',
                  'JA': 'JAPANESE',
                  'JI': 'YIDDISH',
                  'JV': 'JAVANESE',
                  'KA': 'GEORGIAN',
                  'KK': 'KAZAKH',
                  'KL': 'GREENLANDIC',
                  'KM': 'CAMBODIAN',
                  'KN': 'KANNADA',
                  'KO': 'KOREAN',
                  'KS': 'KASHMIRI',
                  'KU': 'KURDISH',
                  'KY': 'KIRGHIZ',
                  'LA': 'LATIN',
                  'LN': 'LINGALA',
                  'LO': 'LAOTHIAN',
                  'LT': 'LITHUANIAN',
                  'LV': 'LATVIAN;LETTISH',
                  'MG': 'MALAGASY',
                  'MI': 'MAORI',
                  'MK': 'MACEDONIAN',
                  'ML': 'MALAYALAM',
                  'MN': 'MONGOLIAN',
                  'MO': 'MOLDAVIAN',
                  'MR': 'MARATHI',
                  'MS': 'MALAY',
                  'MT': 'MALTESE',
                  'MY': 'BURMESE',
                  'NA': 'NAURU',
                  'NE': 'NEPALI',
                  'NL': 'DUTCH',
                  'NO': 'NORWEGIAN',
                  'OC': 'OCCITAN',
                  'OM': 'AFAN (OROMO',
                  'OR': 'ORIYA',
                  'PA': 'PUNJABI',
                  'PL': 'POLISH',
                  'PS': 'PASHTO;PUSHTO',
                  'PT': 'PORTUGUESE',
                  'QU': 'QUECHUA',
                  'RM': 'RHAETO-ROMANCE',
                  'RN': 'KURUNDI',
                  'RO': 'ROMANIAN',
                  'RU': 'RUSSIAN',
                  'RW': 'KINYARWANDA',
                  'SA': 'SANSKRIT',
                  'SD': 'SINDHI',
                  'SG': 'SANGHO',
                  'SH': 'SERBO-CROATIAN',
                  'SI': 'SINGHALESE',
                  'SK': 'SLOVAK',
                  'SL': 'SLOVENIAN',
                  'SM': 'SAMOAN',
                  'SN': 'SHONA',
                  'SO': 'SOMALI',
                  'SQ': 'ALBANIAN',
                  'SR': 'SERBIAN',
                  'SS': 'SISWATI',
                  'ST': 'SESOTHO',
                  'SU': 'SUNDANESE',
                  'SV': 'SWEDISH',
                  'SW': 'SWAHILI',
                  'TA': 'TAMIL',
                  'TE': 'TELUGU',
                  'TG': 'TAJIK',
                  'TH': 'THAI',
                  'TI': 'TIGRINYA',
                  'TK': 'TURKMEN',
                  'TL': 'TAGALOG',
                  'TN': 'SETSWANA',
                  'TO': 'TONGA',
                  'TR': 'TURKISH',
                  'TS': 'TSONGA',
                  'TT': 'TATAR',
                  'TW': 'TWI',
                  'UK': 'UKRAINIAN',
                  'UR': 'URDU',
                  'UZ': 'UZBEK',
                  'VI': 'VIETNAMESE',
                  'VO': 'VOLAPUK',
                  'WO': 'WOLOF',
                  'XH': 'XHOSA',
                  'YO': 'YORUBA',
                  'ZH': 'CHINESE',
                  'ZU': 'ZULU'}

