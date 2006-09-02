#! /usr/bin/env python
# -=- encoding: latin-1 -=-

import unittest
import dvdauthor

class TestDvdauthor(unittest.TestCase):
    """Test the pydvdauthor module"""
    
    def setUp(self):
        """Create a new Disc object, brand new and empty"""
        self.disc = dvdauthor.Disc()

    def tearDown(self):
        pass

    ###################
    ### Begin tests ###
    ###################

    def test_vmgm(self):
        # Create VMGM menu structure
        vmgm = dvdauthor.VMGM('The first top-level menu')
        # Add it to the disc
        self.disc.set_vmgm(vmgm)

        # Create a men
        menu1 = dvdauthor.Menu('Main menu example')
        vmgm.add_menu(menu1)

    def test_vmgm_badmenu(self):
        vmgm = dvdauthor.VMGM('top-level')
        titleset = dvdauthor.Titleset('titleset')
        
        # Bad entry point for a VMGM menu.
        menu_root = dvdauthor.Menu('This menu', 'root')
        menu_title = dvdauthor.Menu('Title menu', 'title')

        # Check invalid values
        # VMGM: title only
        self.assertRaises(AttributeError, vmgm.add_menu, menu_root)
        # Titleset: root|subtitle|audio|angle|ptt
        self.assertRaises(AttributeError, titleset.add_menu, menu_title)

        # Check valid values
        vmgm.add_menu(menu_title)
        titleset.add_menu(menu_root)

    def test_vmgm_add_title(self):
        vmgm = dvdauthor.VMGM('top-level')
        title = dvdauthor.Title('this title')
        self.assertRaises(NotImplementedError, vmgm.add_title, title)


    def test_ids(self):
        """Make sure everything sets an ID"""
        assert self.disc.id

        menu = dvdauthor.Menu('this is my menu')
        title = dvdauthor.Title('this is my title')
        vmgm = dvdauthor.VMGM('This is my official VMGM')
        titleset = dvdauthor.Titleset('this is my own Titleset')
        self.assert_(menu.id)
        self.assert_(title.id)
        self.assert_(vmgm.id)
        self.assert_(titleset.id)

    def test_add_titleset(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        x = len(self.disc.titlesets)
        self.disc.add_titleset(titleset)
        y = len(self.disc.titlesets)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Disc.add_titleset() should add "\
                     "the Titleset to self.titlesets")

    def test_add_title(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        title = dvdauthor.Title('This is my own Title')

        x = len(titleset.titles)
        titleset.add_title(title)
        y = len(titleset.titles)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_title() should add "\
                     "the Title to self.titles")

    def test_add_menu(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        menu = dvdauthor.Menu('This is my own Menu')

        x = len(titleset.menus)
        titleset.add_menu(menu)
        y = len(titleset.menus)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_menu() should add "\
                     "the Menu to self.menus")


    def test_add_audiolang(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')

        x = len(titleset.audio_langs)
        titleset.add_audio_lang('fr')
        y = len(titleset.audio_langs)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_audio_lang() should add "\
                     "the audio_lang to self.audio_langs")


    def test_add_subpictures(self):
        vmgm = dvdauthor.VMGM('This is my new VMGM')

        x = len(vmgm.subpictures)
        vmgm.add_subpicture_lang('fr')
        y = len(vmgm.subpictures)

        # Make sure it's really added.
        self.assert_(y == (x+1), "VMGM.add_subpicture_lang() should add "\
                     "the audio_lang to self.subpictures")

    def test_add_videofile(self):
        title = dvdauthor.Title('This is my Title')

        x = len(title.videofiles)
        title.add_video_file('thisfile.mpg')
        y = len(title.videofiles)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Title.add_video_file() should add "\
                     "the file,chapters,pause to self.videofiles")

    def test_add_cell(self):
        title = dvdauthor.Title('This is my Title')

        x = len(title.cells)
        title.add_cell('0:10', '10:10')
        y = len(title.cells)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Title.add_cell() should add "\
                     "the start,end,chapter,program,pause to self.cells")

    def test_set_prepost_cmds(self):
        """Make sure the pre/post_commands are set properly"""
        menu = dvdauthor.Menu('This is my menu')
        
        cmd = 'jump %s' % menu.id
        menu.set_pre_commands(cmd)
        self.assert_(cmd == menu.pre_cmds)
        
        cmd = 'jump cell 1'
        menu.set_pre_commands(cmd)
        self.assert_(cmd == menu.pre_cmds)
        
    def test_button_set(self):
        """Make sure the commands are set for the good button, even
        if we overwrite it's value"""
        menu = dvdauthor.Menu('this is a Menu')
        cmd1 = 'jump cell 1'
        menu.set_button_commands(cmd1, None)
        cmd2 = 'jump cell 2<'
        menu.set_button_commands(cmd2, None)
        cmd3 = 'jump cell 3'
        menu.set_button_commands(cmd3, 'MyButton')
        cmd4 = 'jump cell 4'
        menu.set_button_commands(cmd4, 'MyButton')

        self.assert_(menu.buttons[0][1] == cmd1)
        self.assert_(menu.buttons[1][1] == cmd2)
        # the value was overwritte by cmd4, if everything works
        self.assert_(menu.buttons[2][1] == cmd4)
        

    def test_set_vmgm(self):
        vmgm = dvdauthor.VMGM('This is my VMGM menu')

        self.assert_(self.disc.vmgm == None)
        
        self.disc.set_vmgm(vmgm)

        self.assert_(self.disc.vmgm != None)

    def test_xmlentities(self):
        text = 'hello>'
        newtext = dvdauthor._xmlentities(text)
        self.assert_(text != newtext, "dvdauthor._xmlentities() should replace > and other characters")

    def test_menu_entry(self):
        self.assertRaises(KeyError, dvdauthor.Menu, 'create this menu', 'bad_entry_point')

    def _test_childobj_xml(self):
        title = dvdauthor.Title('This is my title')
        title.add_video_file('/tmp/ahuh.mpg', '0:50', 'inf')
        title.add_video_file('/tmp/ahuh1.mpg', None, '14')
        title.add_video_file('/tmp/gogo.mpg')
        print "XML output:"
        print title._xml()

        menu = dvdauthor.Menu('This is a Menu', 'root')
        menu.add_video_file('/tmp/ahuh.mpg', '0:50', 'inf')
        menu.set_button_commands('jump cell 1')
        menu.set_button_commands('jump cell 2', 'bigbutton')
        print "XML output:"
        print menu._xml()

        titleset = dvdauthor.Titleset('This is a Titleset')
        titleset.add_menu(menu)
        titleset.add_title(title)
        print "XML output:"
        print titleset._xml()

    def test_unused_menu(self):
        disc = dvdauthor.Disc('This is Disc')
        vmgm = dvdauthor.VMGM('Menu')
        disc.set_vmgm(vmgm)

        menu1 = dvdauthor.Menu('My menu')
        menu2 = dvdauthor.Menu('Unused')
        
        vmgm.add_menu(menu1)

        menu1.set_post_commands('jump f:%s' % menu2.id)

        # Check for 'not having video files added'
        self.assertRaises(ValueError, disc.xml, '/tmp/output')

        menu1.add_video_file('/tmp/menu.mpg')
        menu2.add_video_file('/tmp/menu2.mpg')

        # Check for not having cleared references
        self.assertRaises(ReferenceError, disc.xml, '/tmp/output-dir')

        # Cleared references
        vmgm.add_menu(menu2)
        disc.xml('/tmp/output-dir')

    def test_full_layout(self):
        # Big blocks
        
        disc = dvdauthor.Disc('This is my whole DISC!')
        
        vmgm = dvdauthor.VMGM('This is a VMGM menu')

        titleset1 = dvdauthor.Titleset('This is my first Titleset')
        titleset2 = dvdauthor.Titleset('This is my second Titleset')

        disc.set_vmgm(vmgm)
        disc.add_titleset(titleset1)
        disc.add_titleset(titleset2)

        title1 = dvdauthor.Title('This is a title')
        title2 = dvdauthor.Title('This is a second title')
        title3 = dvdauthor.Title('This is my third title')

        menu1 = dvdauthor.Menu('This is a first menu')
        menu2 = dvdauthor.Menu('This is a second menu')
        menu3 = dvdauthor.Menu('This is a third menu, in fact the VMGM one')
        menu4 = dvdauthor.Menu('This is an unused menu')

        titleset1.add_menu(menu1) 
        titleset1.add_title(title1)
        titleset2.add_menu(menu2)
        titleset2.add_title(title2)
        titleset2.add_title(title3)

        vmgm.add_menu(menu3)

        menu2.set_post_commands('jump titleset %s title %s' % (titleset2.id,
                                                               title2.id))
        title1.add_video_file('/tmp/title1_video1.mpg')
        title2.add_video_file('/tmp/title2_video1.mpg')
        title3.add_video_file('/tmp/title3_video1.mpg')

        # Test add video files after adding the menu to the Titleset
        menu1.add_video_file('/tmp/menu1_video1.mpg')
        menu2.add_video_file('/tmp/menu2_video1.mpg')
        menu1.add_video_file('/tmp/menu1_video2.mpg')
        menu3.add_video_file('/tmp/menu3_video1.mpg')

        menu3.set_button_commands('jump f:%s' % title2.id)
        menu3.set_button_commands('jump f:%s' % menu4.id,
                                  'mybutton') # Unused menu that will break

        self.assert_(len(titleset1.menus[0].videofiles) == 2)

        self.assertRaises(ReferenceError, disc.xml, '/tmp-output-dir')

        # Resolv unused menu
        menu3.set_button_commands('jump f:%s' % title1.id,
                                  'mybutton')

        print "XML output:"
        print disc.xml('/tmp/output-dir')
        

if __name__ == '__main__':
    unittest.main()
