# -* sh *-
ME="[makexml]:"
. tovid-init

# makexml
# Part of the tovid suite
# =======================
# This bash script generates XML output describing the structure of
# a VCD, SVCD, or DVD disc. The resulting output can be given as input
# to vcdxbuild or dvdauthor. Format, and a list of menus and
# video files in MPEG format, are specified on the command-line, and
# the resulting XML is written to the specified file. Currently
# supports an optional top-level menu, any number of optional sub-menus,
# and any number of videos reachable through those menus.
#
# Project homepage: http://www.tovid.org
#
#
# Copyright (C) 2005 tovid.org <http://www.tovid.org>
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA. Or see:
#
#           http://www.gnu.org/licenses/gpl.txt

SCRIPTNAME=`cat << EOF
--------------------------------
makexml
A script to generate XML for authoring a VCD, SVCD, or DVD.
$TOVID_HOME_PAGE
--------------------------------
EOF`

USAGE=`cat << 'EOF'
Usage:  makexml [OPTIONS] video1.mpg video2.mpg ... OUT_PREFIX

    -dvd | -vcd | -svcd       Specify the target disc format
    -overwrite                Overwrite any existing output files

Provide a list of .mpg video files, and they will be played back in
sequence. You may organize several lists of videos into menus by
providing the name of a menu .mpg:

    makexml -menu menu1.mpg \\
        video1.mpg video2.mpg video3.mpg \\
        mydisc
    makexml -topmenu topmenu.mpg \\
        -menu submenu1.mpg vid1.mpg vid2.mpg vid3.mpg \\
        -menu submenu2.mpg vid4.mpg vid5.mpg vid6.mpg \\
        mydisc2

See the makexml manual page ('man makexml') for additional documentation.

EOF`

SEPARATOR="=========================================="

# Print script name, usage notes, and optional error message, then exit.
# Args: $1 == text string containing error message
usage_error ()
{
  echo $"$USAGE"
  echo $SEPARATOR
  echo $"$@"
  exit 1
}

# Currently-numbered titleset (must have at least 1 titleset)
CUR_TS=1
# Currently-numbered video title under a titleset menu (0 for no titles)
CUR_TITLE=0
# Do we have a top menu yet?
HAVE_TOP_MENU=false
# Do we have any menus yet?
HAVE_MENU=false
# Do not overwrite by default
OVERWRITE=false
# Use dvdauthor XML for DVD authoring
XML_FORMAT="dvd"
# No un-found files yet
FILE_NOT_FOUND=false
# Not doing still titles
STILL_TITLES=false
FIRST_TITLE=:
# Avoid some unbound variables
TOP_MENU_XML=""
TOP_MENU_BUTTONS=""
MENU_BUTTONS=""
TS_TITLES=""
ALL_MENU_XML=""
SEGMENT_ITEMS_XML=""
SEQUENCE_ITEMS_XML=""
PBC_XML=""
PLAYLIST_XML=""

MAKE_GROUP=false
MAKE_CHAPTERS=false
FORCE_TITLESETS=false
CUR_VIDEO=0
declare -i CHAPTER_INTERVAL

# ==========================================================
# Check for the existence of a file and print an error if it
# does not exist in the current directory
# Args: $1 = file to look for
checkExistence ()
{
    if [[ ! -e $1 ]]; then
        echo "The file "$1" was not found."
        FILE_NOT_FOUND=:
    fi
}

# ==========================================================
# Add a top-level VMGM menu to the DVD
# Args: $1 = video file to use for top menu
addTopMenu ()
{
  HAVE_TOP_MENU=:
  echo "Adding top-level menu using file: $1"

  # --------------------------
  # For DVD
  if [[ $XML_FORMAT == "dvd" ]]; then

    # Generate XML for the top menu, with a placeholder for
    # the titleset menu buttons (to be replaced later by sed)
    TOP_MENU_XML=`cat << EOF
  <menus>
  <video />
  <pgc entry="title">
  <vob file="$1" />
__TOP_MENU_BUTTONS__
  </pgc>
  </menus>
EOF`

  # --------------------------
  # For (S)VCD
  else

    # Generate XML for the segment-item
    SEGMENT_ITEMS_XML=`cat << EOF
$SEGMENT_ITEMS_XML
  <segment-item src="$1" id="seg-top-menu"/>
EOF`

    # Generate XML for the selection to go in pbc
    TOP_MENU_XML=`cat << EOF
  <selection id="select-top-menu">
    <bsn>1</bsn>
    <loop jump-timing="immediate">0</loop>
    <play-item ref="seg-top-menu"/>
__TOP_MENU_BUTTONS__
  </selection>
EOF`

  fi
}

# ==========================================================
# Add a menu to the disc.
# Args: $1 = video file to use for the menu
addMenu ()
{
  # --------------------------
  # For DVD
  if [[ $XML_FORMAT == "dvd" ]]; then
    echo "Adding a titleset-level menu using file: $1"

    # Generate XML for the button linking to this titleset menu from the top menu
    TOP_MENU_BUTTONS=`cat << EOF
  $TOP_MENU_BUTTONS\
    <button>jump titleset $CUR_TS menu;<\/button>
EOF`

    # Generate XML for the menu header, with a placeholder for
    # the video segment buttons (to be replaced later by sed)
    MENU_XML=`cat << EOF
  <menus>
    <video />
    <pgc entry="root">
      <vob file="$1" />
__MENU_BUTTONS__
    </pgc>
  </menus>
EOF`

  # --------------------------
  # For (S)VCD
  else
    echo "Adding a menu using file: $1"

    # Generate XML for the button linking to this menu from the top menu
    TOP_MENU_BUTTONS=`cat << EOF
$TOP_MENU_BUTTONS\
    <select ref="select-menu-$CUR_TS"\/>
EOF`

    # Generate XML for the segment item
    SEGMENT_ITEMS_XML=`cat << EOF
$SEGMENT_ITEMS_XML
  <segment-item src="$1" id="seg-menu-$CUR_TS"/>
EOF`

    # Generate XML for the selection to go in pbc
    # If there's a top menu, "return" goes back to it.
    # Otherwise, don't use a "return" command.
    if $HAVE_TOP_MENU; then
      RETURN_CMD="<return ref=\"select-top-menu\"/>"
    else
      RETURN_CMD=""
    fi
    SELECTION_XML=`cat << EOF
  <selection id="select-menu-$CUR_TS">
    <bsn>1</bsn>
    $RETURN_CMD
    <loop jump-timing="immediate">0</loop>
    <play-item ref="seg-menu-$CUR_TS"/>
__MENU_BUTTONS__
  </selection>
EOF`

  fi
}

# ==========================================================
# Add a video title to a titleset menu, or a still image to
# a slideshow
# Args: $1 = video file to use for the title
addTitle ()
{
  if $FORCE_TITLESETS && test $CUR_VIDEO -eq 0; then
    closeTitleset
  fi
  # Increment the current title number
  if ! $MAKE_GROUP; then
    (( CUR_TITLE++ ))
  else
    # Grouping several videos within one title 
    if [[ $CUR_VIDEO -eq 0 ]]; then
       (( CUR_TITLE++ ))
    fi
    (( CUR_VIDEO++ ))
  fi
  # --------------------------
  # For DVD
  if [[ $XML_FORMAT == "dvd" ]]; then
    if ! $MAKE_GROUP; then
      echo "Adding title: $1 as title number $CUR_TITLE of titleset $CUR_TS"
    else
      if [[ $CUR_VIDEO -eq 1 ]]; then
        echo "Adding title number $CUR_TITLE of titleset $CUR_TS"
      fi
      echo "Adding $1 as video $CUR_VIDEO of title $CUR_TITLE"
    fi
    # Generate XML for the button linking to this title from the titleset menu
    if ! $FORCE_TITLESETS; then
      if [[ $CUR_VIDEO -lt 2 ]]; then
        MENU_BUTTONS=`cat << EOF
$MENU_BUTTONS\
        <button>jump title $CUR_TITLE;<\/button>
EOF`
      fi
    else
      # Add a button for the current titleset to the top menu 
      if [[ $CUR_VIDEO -le 1 ]]; then
        TOP_MENU_BUTTONS=`cat << EOF
$TOP_MENU_BUTTONS\
        <button>jump titleset $CUR_TS menu;<\/button>
EOF`
      fi
    fi 

    # Generate the chapters tag
    CMD="idvid -terse \"$1\""
    echo "Calculating the duration of the video using the following command:"
    echo $CMD
    echo "This may take a few minutes, so please be patient..."
    DURATION=`eval $CMD | grep DURATION | awk -F '=' '{print $2}'`
    echo $DURATION | awk '{hh=int($1/3600);mm=int(($1-hh*3600)/60);ss=$1-hh*3600-mm*60;\
        printf "The duration of the video is %02d:%02d:%02d\n",hh,mm,ss}'

    if ! $MAKE_CHAPTERS; then
      CHAPTER_INTERVAL="5"
    fi

    CHAPTERS=`echo $DURATION $CHAPTER_INTERVAL | \
       awk '{dur=$1;\
                iv=$2*60;\
                if (iv==0){\
                   printf "0";\
                   exit\
                }\
                cur=0;\
                i=0;\
                while(cur<dur){\
                   if(i>0){\
                      printf ","\
                   }\
                   i++;\
                   hh=int(cur/3600);\
                   mm=int((cur-hh*3600)/60);\
                   ss=cur-hh*3600-mm*60;\
                   printf "%02d:%02d:%02d",hh,mm,ss;
                   cur+=iv\
                }\
            }'`

    # Generate the XML for the title itself, appending to existing titles
    if $MAKE_GROUP; then
      if [[ $CUR_VIDEO -eq 1 ]]; then
        TS_TITLES=`cat << EOF
$TS_TITLES
    <pgc>
EOF`
      fi
      TS_TITLES=`cat << EOF
                 $TS_TITLES
      <vob file="$1" chapters="$CHAPTERS" />
EOF`
    else
      TS_TITLES=`cat << EOF
$TS_TITLES
    <pgc>
      <vob file="$1" chapters="$CHAPTERS" />
      __POST_CMD__
    </pgc>
EOF`
    fi

  # --------------------------
  # For (S)VCD
  else

    # If there's a menu, "return" goes back to it; if not,
    # do not generate a "return" command
    if $HAVE_MENU; then
      RETURN_CMD="<return ref=\"select-menu-$CUR_TS\"/>"
    else
      RETURN_CMD=""
    fi
    # If this is the first title or slide in a series
    if $FIRST_TITLE; then
      # For the first titles, PREV stays on the current title
      let "PREV_TITLE=$CUR_TITLE"
    # For all other titles
    else
      # PREV goes to the previous slide
      let "PREV_TITLE=$CUR_TITLE - 1"
    fi

    # Fill in the NEXT command for the previous slide, if there was one
    NEXT_TITLE="<next ref=\"play-title-$CUR_TITLE\"\/>"
    SELECTION_XML=$( echo "$SELECTION_XML" | sed -e "s/__NEXT_TITLE__/$NEXT_TITLE/g" )
    PLAYLIST_XML=$( echo "$PLAYLIST_XML" | sed -e "s/__NEXT_TITLE__/$NEXT_TITLE/g" )

    # --------------------------
    # If doing a still-image slideshow, use segment/selection
    if $STILL_TITLES; then
      echo "Adding title: $1 as number $CUR_TITLE in a slideshow"

      # Generate XML for the selection (menu) "buttons" that will
      # jump to this slideshow. Only the first slide gets a button.
      if $FIRST_TITLE; then
        MENU_BUTTONS=`cat << EOF
$MENU_BUTTONS\
    <select ref="play-title-$CUR_TITLE"\/>
EOF`
      fi

      # Generate XML for the segment item
      SEGMENT_ITEMS_XML=`cat << EOF
$SEGMENT_ITEMS_XML
  <segment-item src="$1" id="seg-slide-$CUR_TITLE"/>
EOF`

      # Generate XML for the selection to go in pbc
      # The slide will play indefinitely until NEXT, PREV,
      # or RETURN is pressed. __NEXT_TITLE__ is a placeholder
      # until we're sure there is a next slide; it will be
      # filled in on the next addition if there is.
      SELECTION_XML=`cat << EOF
$SELECTION_XML
  <playlist id="play-title-$CUR_TITLE">
    <prev ref="play-title-$PREV_TITLE"/>
    __NEXT_TITLE__
    $RETURN_CMD
    <wait>-1</wait>
    <play-item ref="seg-slide-$CUR_TITLE"/>
  </playlist>
EOF`

    # --------------------------
    # If doing normal video titles, use select/playlist
    else

      echo "Adding title: $1 as title number $CUR_TITLE"

      # Generate XML for the selection (menu) "buttons" that will
      # jump to this playlist (title)
      MENU_BUTTONS=`cat << EOF
$MENU_BUTTONS\
    <select ref="play-title-$CUR_TITLE"\/>
EOF`

      # Generate XML for the sequence item
      SEQUENCE_ITEMS_XML=`cat << EOF
$SEQUENCE_ITEMS_XML
  <sequence-item src="$1" id="seq-title-$CUR_TITLE"/>
EOF`

      # Generate XML for the playlist for this title
      PLAYLIST_XML=`cat << EOF
$PLAYLIST_XML
  <playlist id="play-title-$CUR_TITLE">
    <prev ref="play-title-$PREV_TITLE"/>
    __NEXT_TITLE__
    $RETURN_CMD
    <wait>0</wait>
    <play-item ref="seq-title-$CUR_TITLE"/>
  </playlist>
EOF`

    fi # (S)VCD slides or normal titles

  fi # DVD or (S)VCD

  FIRST_TITLE=false
}

# ==========================================================
# Finalize the XML for a titleset, containing a menu and titles
closeTitleset ()
{
  # Proceed only if there are titles in this titleset
  if (( $CUR_TITLE > 0 )); then

  # --------------------------
  # For DVD
  if [[ $XML_FORMAT == "dvd" ]]; then
    echo "Closing titleset $CUR_TS with $CUR_TITLE title(s)."

    # Give each menu a button linking back to the top menu, if there is one
    if $HAVE_TOP_MENU; then
      MENU_BUTTONS=`cat << EOF
$MENU_BUTTONS\
      <button>jump vmgm menu;<\/button>

EOF`
    fi

    # Fill in titleset menu buttons
    MENU_XML=$( echo "$MENU_XML" | sed -e "s/__MENU_BUTTONS__/$MENU_BUTTONS/g" )

    # Fill in the POST command. If there is a menu to jump back to, use that;
    # otherwise, do not insert a POST command.
    if $HAVE_MENU; then
      POST_CMD="<post>call menu;<\/post>"
    elif $FORCE_TITLESETS && $HAVE_TOP_MENU; then
      POST_CMD="<post>call vmgm menu;<\/post>"
    else
      POST_CMD=""
    fi
    TS_TITLES=$( echo "$TS_TITLES" | sed -e "s/__POST_CMD__/$POST_CMD/g" )

    # Append titleset info to ALL_MENU_XML
    if ! $FORCE_TITLESETS || ! $HAVE_TOP_MENU; then
      ALL_MENU_XML=`cat << EOF
$ALL_MENU_XML
<titleset>
$MENU_XML
  <titles>
$TS_TITLES
  </titles>
</titleset>
EOF`
    else
      # One titleset for each title -> add a dummy menu to the titleset
      ALL_MENU_XML=`cat << EOF
$ALL_MENU_XML
<titleset>
  <menus>
    <pgc>
      <post>
        jump title 1;
      </post>
    </pgc>
  </menus>
  <titles>
$TS_TITLES
  </titles>
</titleset>
EOF`
    fi
    # Clear existing XML to prepare for next titleset
    MENU_XML=""
    TS_TITLES=""
    CUR_TITLE=0
    MENU_BUTTONS=""
  
  # --------------------------
  # For (S)VCD
  else

    # Fill in menu title selections ("buttons")
    # and remove any remaining __NEXT_TITLE__s
    SELECTION_XML=$( echo "$SELECTION_XML" | sed -e "s/__MENU_BUTTONS__/$MENU_BUTTONS/g" \
      -e "s/__NEXT_TITLE__//g" )
    PLAYLIST_XML=$( echo "$PLAYLIST_XML" | sed -e "s/__NEXT_TITLE__//g" )

    # Append new PBC menus/playlists to PBC_XML
    PBC_XML=`cat << EOF
$PBC_XML
$SELECTION_XML
$PLAYLIST_XML

EOF`

    # Clear existing XML to prepare for next menu/titles
    SELECTION_XML=""
    PLAYLIST_XML=""
    MENU_BUTTONS=""
    # Go back to doing normal video titles
    STILL_TITLES=false
  fi

  # Increment the current titleset number
  (( CUR_TS++ ))

  fi # End if there are titles
}

# ==========================================================
# EXECUTION BEGINS HERE
echo $"$SCRIPTNAME"

if [[ $# -lt 1 ]]; then
  usage_error "Please provide at least one video to author, and the name of an output file to use."
fi

while [[ $# -gt 1 ]]; do
  # Format and overwriting options
  if [[ $1 == "-dvd" ]]; then
    XML_FORMAT="dvd"
  elif [[ $1 == "-vcd" ]]; then
    XML_FORMAT="vcd" 
  elif [[ $1 == "-svcd" ]]; then
    XML_FORMAT="svcd"
  elif [[ $1 == "-overwrite" ]]; then
    OVERWRITE=:
  # Menus and video titles
  elif [[ $1 == "-topmenu" ]]; then
    shift
    if ! $HAVE_TOP_MENU; then
      checkExistence "$1"
      addTopMenu "$1"
    else
      usage_error "You can only have one top menu. Please specify only one -topmenu option. If you would like to have multiple menus, please use the -menu option."
    fi
  elif [[ $1 == "-menu" ]]; then
    if $FORCE_TITLESETS; then
      usage_error "You can not use -titlesets with -menu. Please use -topmenu instead."
    fi
    shift
    HAVE_MENU=:
    FIRST_TITLE=:
    checkExistence "$1"
    closeTitleset
    addMenu "$1"
  elif [[ $1 == "-slides" ]]; then
    STILL_TITLES=:
    FIRST_TITLE=:
  elif [[ $1 == "-group" ]]; then
    MAKE_GROUP=:
    CUR_VIDEO=0
  elif [[ $1 == "-endgroup" ]]; then
    if $MAKE_GROUP; then
      TS_TITLES=`cat << EOF
       $TS_TITLES
       __POST_CMD__
    </pgc>
EOF`
       MAKE_GROUP=false
    fi
    MAKE_GROUP=false
    CUR_VIDEO=0
  elif [[ $1 == "-chapters" ]]; then
    MAKE_CHAPTERS=:
    shift
    CHAPTER_INTERVAL=$1
    if [[ "$CHAPTER_INTERVAL" -lt "0" || "$CHAPTER_INTERVAL" -gt "9999" ]]
    then
       usage_error "Please use a -chapters interval between 0 and 9999."
    fi
  elif [[ $1 == "-nochapters" ]]; then
    MAKE_CHAPTERS=:
  elif [[ $1 == "-titlesets" ]]; then
    if $HAVE_MENU; then
      usage_error "You can not use -titlesets with -menu. Please use -topmenu instead."
    fi
    FORCE_TITLESETS=:
    echo "Creation of titlesets forced ..."
  else
    checkExistence "$1"
    addTitle "$1"
  fi

  # Get the next argument
  shift
done

# Last argument should be the name of the output file
if [[ $# -ne 1 ]]; then
  usage_error "Please provide a name for the output file (the .xml extension will be added)"
else
  OUT_PREFIX="$1"
fi

# Close current titleset
closeTitleset

# Fill in top menu buttons
TOP_MENU_XML=$( echo "$TOP_MENU_XML" | sed -e "s/__TOP_MENU_BUTTONS__/$TOP_MENU_BUTTONS/g" )

# If there is a top menu with no other menus, print an error and
# a suggestion that user specify -menu instead of -topmenu
if $HAVE_TOP_MENU && ! $HAVE_MENU && ! $FORCE_TITLESETS; then
  echo "You have specified a top menu without any other menus. If you only want to have one menu, please use the -menu option instead of -topmenu."
  echo "Exiting without writing XML file."
  exit 1
fi

# Assemble the final XML file

# dvdauthor format for a DVD
if [[ $XML_FORMAT == "dvd" ]]; then
FINAL_DISC_XML=`cat << EOF
<dvdauthor dest="$OUT_PREFIX">
<vmgm>
$TOP_MENU_XML
</vmgm>
$ALL_MENU_XML
</dvdauthor>
EOF`

# vcdxbuild (vcdimager) format for a VCD or SVCD
else
  # Determine what version number to use
  if [[ $XML_FORMAT == "vcd" ]]; then
    VCD_VERSION="2.0"
    OPTION_LINE=''
  # Use 1.0 for SVCD
  else
    VCD_VERSION="1.0"
    OPTION_LINE='<option name="update scan offsets" value="true" />'
  fi

  # Make sure there are segment-items and sequence-items
  if [[ -n $SEGMENT_ITEMS_XML ]]; then
    SEGMENT_ITEMS_XML=`cat << EOF
<segment-items>
$SEGMENT_ITEMS_XML
</segment-items>
EOF`
  fi
  if [[ -n $SEQUENCE_ITEMS_XML ]]; then
    SEQUENCE_ITEMS_XML=`cat << EOF
<sequence-items>
$SEQUENCE_ITEMS_XML
</sequence-items>
EOF`
  fi

FINAL_DISC_XML=`cat << EOF
<?xml version="1.0"?>
<!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
  "http://www.gnu.org/software/vcdimager/videocd.dtd">
<videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
  class="$XML_FORMAT" version="$VCD_VERSION">
$OPTION_LINE
<info>
  <album-id>VIDEO_DISC</album-id>
  <volume-count>1</volume-count>
  <volume-number>1</volume-number>
  <restriction>0</restriction>
</info>

<pvd>
  <volume-id>VIDEO_DISC</volume-id>
  <system-id>CD-RTOS CD-BRIDGE</system-id>
</pvd>

$SEGMENT_ITEMS_XML

$SEQUENCE_ITEMS_XML

<pbc>
$TOP_MENU_XML

$PBC_XML
</pbc>
</videocd>
EOF`
fi

# See if selected output file exists. If so, confirm for overwrite.
if [[ -e $OUT_PREFIX.xml ]]; then
  echo $SEPARATOR
  echo "The output file you specified: $OUT_PREFIX.xml already exists."
  if $OVERWRITE; then
    echo "Overwriting existing file."
  else
    echo "If you would like to overwrite, please re-run the script with the -overwrite option."
    exit 1
  fi
fi

# Remove blank lines and write final result to output file
echo "$FINAL_DISC_XML" | sed -e '/^ *$/d' > $OUT_PREFIX.xml

if $FILE_NOT_FOUND; then
  echo $SEPARATOR
  echo "Some of the video files you specified were not found."
  echo "The XML file was written anyway, but you might want to"
  echo "double-check to make sure you didn't make a typing mistake."
fi

echo $SEPARATOR

echo "Done. The resulting XML was written to $OUT_PREFIX.xml."
if [[ $XML_FORMAT == "dvd" ]]; then
    echo "You can now author, image and/or burn the disc by running:"
    echo "    makedvd $OUT_PREFIX.xml"
else
    echo "You can create the (S)VCD .bin and .cue files by running the command:"
    echo "  vcdxbuild $OUT_PREFIX.xml"
fi

echo "Thanks for using makexml!"

exit 0

