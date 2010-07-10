#!/usr/bin/env python

import time
import shlex
import commands
import re
from Tkinter import *
from subprocess import Popen, PIPE, STDOUT
from sys import argv
from os import path, mkfifo, devnull
from tempfile import mkdtemp

##############################################################################
#                              functions                                     #
##############################################################################
def send(text):
    """send command to mplayer's slave fifo"""
    if is_running.get():
        commands.getstatusoutput('echo -e "%s"  > %s' %(text, cmd_pipe))

def seek(event=None):
    """seek in video according to value set by slider"""
    send('seek %s 3\n' %seek_scale.get())

def pause():
    """send pause to mplayer via slave and set button var to opposite value"""
    # mplayer's 'pause' pauses if playing and plays if paused
    # pauseplay ==play in pause mode, and ==pause in play mode (button text)
    if is_running.get():
        if pauseplay.get() == 'pause':
            pauseplay.set('play')
        else:
            pauseplay.set('pause')
        send('pause\n')
    else:
        # start the video for the 1st time
        cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
        is_running.set(True)
        poll()
        # show osd time and remaining time
        send('osd 3\n')
        pauseplay.set('pause')

def forward():
    """seek forward 10 seconds and make sure button var is set to 'pause'"""
    send('seek 10\n')
    pauseplay.set('pause')

def back():
    """seek backward 10 seconds and make sure button var is set to 'pause'"""
    send('seek -10\n')
    pauseplay.set('pause')

def framestep():
    """step frame by frame forward and set button var to 'play'"""
    send('pausing frame_step\n')
    pauseplay.set('play')

def confirm_exit():
    """on exit, make sure that mplayer is not running before quit"""
    if is_running.get():
        send("osd_show_text 'press exit before quitting program' 4000 3\n")
    else:
        sys.stdout.write(get_chapters())
        quit()

def exit_mplayer():
    """close mplayer, then get chapters from the editlist"""
    # unpause so mplayer doesn't hang
    if is_running.get():
        if pauseplay.get() == 'play':
            send('mute 1\n')
            send('pause\n')
        send('quit\n')
        is_running.set(False)
    time.sleep(0.3)
    confirm_exit()


def set_chapter():
    """send chapter mark (via slave) twice so mplayer writes the data.
       we only take the 1st mark on each line
    """
    for i in range(2):
        send('edl_mark\n')
    send("osd_show_text 'chapter point saved' 2000 3\n")

def get_chapters():
    # need a sleep to make sure mplayer gives up its data
    if not path.exists(editlist):
        return '00:00:00'
    time.sleep(0.5)
    f = open(editlist)
    c = f.readlines()
    f.close()
    # if chapter_var has value, editlist has been reset.  Append value, if any.
    # only 1st value on each line is taken (2nd is to make mplayer write out)
    s = [ i.split()[0]  for i  in chapter_var.get().splitlines() if i]
    c.extend(s)
    times = [ float(shlex.split(i)[0]) for i in c ]
    chapters = ['00:00:00']
    for t in sorted(times):
        fraction = '.' + str(t).split('.')[1]
        chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)) + fraction)
    return '%s' %','.join(chapters)

def poll():
    if not is_running.get():
        return
    tail = 'tail -n 1 %s' %log
    log_output = commands.getoutput(tail)
    # restart mplayer with same commands if it exits without user intervention
    if '(End of file)' in log_output:
        # save editlist, as mplayer overwrites it on restart
        o = open(editlist, 'r')
        chapter_var.set(chapter_var.get() + o.read())
        o.close()
        cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
        send('osd 3\n')
    root.after(200, poll)

def identify(file):
    output = commands.getoutput('mplayer -vo null -ao null -frames 30 \
      -channels 6 -identify %s' %file)
    return output

##############################################################################
#              start Tk instance and set tk variables
##############################################################################

if len(sys.argv) < 2:
    print("Usage: set_chapters.py video")
    exit()
root = Tk()
root.minsize(660, 600)
chapter_var = StringVar()
is_running = BooleanVar()
is_running.set(False)
pauseplay = StringVar() 
pauseplay.set('play')
# bindings for exit
root.protocol("WM_DELETE_WINDOW", confirm_exit)
root.bind('<Control-q>', confirm_exit)
root.title('Set chapters')

##############################################################################
#                                   widgets                                  #
##############################################################################

# frame to hold mplayer container
root_frame = Frame(root)
root_frame.pack(side='top', fill='both', expand=1, pady=40)
holder_frame = Frame(root_frame, bg='black')
holder_frame.pack()
# label to display chapters after mplayer exit
info_label = Label(root, wraplength=500, justify='left')
info_label.pack(side='bottom', fill='both', expand=1)
frame = Frame(holder_frame, container=1, bg='', colormap='new')
frame.pack()
# button frame and buttons
button_frame = Frame(root_frame)
button_frame.pack(side='bottom', fill='x', expand=1)
control_frame = Frame(button_frame, borderwidth=1, relief='groove')
control_frame.pack()
exit_button = Button(control_frame, command=exit_mplayer, text='done !')
mark_button = Button(control_frame, command=set_chapter,text='set chapter')
pause_button = Button(control_frame, command=pause,
                  width=12, textvariable=pauseplay)
framestep_button = Button(control_frame, text='step >', command=framestep)
forward_button = Button(control_frame, text='seek >', command=forward)
back_button = Button(control_frame, text='< seek', command=back)
# seek frame and scale widget
seek_frame = Frame(root_frame)
seek_frame.pack(side='left', fill='x', expand=1, padx=30)
seek_scale = Scale(seek_frame, from_=0, to=100, tickinterval=10,
orient='horizontal', label='Use slider to seek to point in file (%)')
seek_scale.bind('<ButtonRelease-1>', seek)
# pack the buttons and scale in their frames
mark_button.pack(side='bottom', fill='both', expand=1)
seek_scale.pack(side='left', fill='x', expand=1)
exit_button.pack(side='left')
back_button.pack(side='left')
pause_button.pack(side='left')
framestep_button.pack(side='left')
forward_button.pack(side='left')
# X11 identifier for the container frame
xid = root.tk.call('winfo', 'id', frame)
# temporary directory for fifo, edit list and log
dir = mkdtemp(prefix='tovid-')
cmd_pipe = path.join(dir, 'slave.fifo')
mkfifo(cmd_pipe)
editlist = path.join(dir, 'editlist')
log = path.join(dir, 'mplayer.log')
media_file = sys.argv[1]

##############################################################################
#  get aspect ratio and set dimensions of video container, get video length  #
##############################################################################
v_width = 600
media_info = identify(media_file)
asr = re.findall('ID_VIDEO_ASPECT=.*', media_info)
# get last occurence as the first is 0.0 with mplayer
if asr:
    asr = sorted(asr, reverse=True)[0].split('=')[1]
try:
    asr = float(asr)
except ValueError:
    asr = 0.0
# get largest value as mplayer prints it out before playing file
if asr and asr > 0.0:
    v_height = int(v_width/asr)
else:
    # default to 4:3 if identify fails
    v_height = int(v_width/1.333)
frame.configure(width=v_width, height=v_height)
# unused
vid_len = re.findall('ID_LENGTH=.*', media_info)
if vid_len:
    video_length = vid_len[0].split('=')[1]

###############################################################################
#            mplayer command.  It will be run by the "play" button.           #
###############################################################################

mplayer_cmd =  'mplayer -wid %s -nomouseinput -slave \
  -input nodefault-bindings:conf=/dev/null:file=%s \
  -edlout %s %s' %(xid, cmd_pipe, editlist, media_file)
mplayer_cmd = shlex.split(mplayer_cmd)

##############################################################################
#                                 run it                                     #
##############################################################################
if __name__ == '__main__':
    root.mainloop()