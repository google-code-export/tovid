#! /bin/sh
ME="[tovid]:"
. tovid-init

# tovid
# Part of the tovid suite
# =======================
# Convert any video/audio stream that mplayer can play
# into VCD, SVCD, or DVD-compatible Mpeg output file.
# Run this script without any options to see usage information.
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

# ******************************************************************************
# ******************************************************************************
#
#
# DEFAULTS AND GLOBALS
#
#
# ******************************************************************************
# ******************************************************************************

# Script name and usage notes


#CV: Usage information blocks, program version block
SCRIPT_NAME=`cat << EOF
--------------------------------
tovid 
DVD and (S)VCD video conversion script
Version $TOVID_VERSION
$BUILD_OPTIONS
$TOVID_HOME_PAGE
--------------------------------
EOF`

USAGE=`cat << EOF
Usage: tovid [OPTIONS] -in {input file} -out {output prefix}

Common options:

    -dvd | -half-dvd | -dvd-vcd         Encode to standard DVD format
    -vcd | -svcd                        Encode to (S)VCD format
    -kvcd | -kvcdx3 | -kdvd | -bdvd     Encode to non-standard MPEG-2 format
    -pal | -ntsc | -ntscfilm            Set TV standard

Example:

    tovid -in foo.avi -out foo_encoded
        Convert 'foo.avi' with default options (NTSC DVD), putting the
        encoded video in 'foo_encoded.mpg'.

See the tovid manual page ('man tovid') for additional documentation.

EOF`

# All other defaults

SEPARATOR="========================================================="

#CV: Default values for everything
# Not currently reading in config file
READING_CONFIG=false

# Video defaults

# Don't use ffmpeg
USE_FFMPEG=false

# NTSC DVD full-screen by default
TGT_RES="DVD"
TVSYS="NTSC"
BASETVSYS="NTSC"
ASPECT_RATIO=""
V_ASPECT_WIDTH=""
# 100% safe area
SAFE_AREA=100
# Don't use yuvdenoise
YUVDENOISE=""
# No vidfilter yet
VID_FILTER=""
# High priority encoding
PRIORITY="nice -n 0"
# Don't do deinterlacing
DEINTERLACE=false
# Don't do interlaced encoding
INTERLACED=false
YUV4MPEG_ILACE=""
FF_ILACE=""
# Don't do any filtering by default
DO_DENOISE=false
DO_CONTRAST=false
DO_DEBLOCK=false
# Use fifo for video encoding?
USE_FIFO=:

# Audio defaults
AUD_SUF="ac3"
VID_SUF="m2v"
# Audio .wav output filename
AUDIO_WAV="audiodump.wav"
# Audio bitrate (for ac3 or mp2)
AUD_BITRATE="224"
# Don't generate an empty audio stream
GENERATE_AUDIO=false
# Amplitude used when adjusting audio (-amplitude)
AUDIO_AMPLITUDE=""


# Assume audio and video need to be re-encoded
AUDIO_OK=false
VIDEO_OK=false


# Do not overwrite existing files
OVERWRITE=false
# Print minimal debugging info
VERBOSE="-v 0"
DEBUG=false

# File to use for saving video statistics
STAT_DIR=$HOME/.tovid
STAT_FILE="$STAT_DIR/stats.tovid"
LOG_FILE=""
SCRATCH_FILE=""

# Do not force encoding of compliant video
FORCE_ENCODING=false
FORCE_FPS=false
FORCE_FPSRATIO=""
# No parallel by default
PARALLEL=false
ENCODING_MODE="serial"
# List of PIDS to kill on exit
PIDS=""
# Live video
VIDEO_TYPE="live"
# Do not normalize audio
DO_NORM=false
# Compact disc size (unset by default)
DISC_SIZE=""
# Nonvideo bitrate
NONVIDEO_BITRATE=""
# Default progress-meter update interval
SLEEP_TIME="5s"
# Don't use subtitles unless user requests it
DO_SUBS=false
SUBTITLES="-noautosub"
# Input file and type
IN_FILE=""
IN_FILE_TYPE="file"
# Output prefix
OUT_PREFIX=""
OUT_FILENAME=""
# Resolution, FPS, and length are unknown
ID_VIDEO_WIDTH="0"
ID_VIDEO_HEIGHT="0"
ID_VIDEO_FPS="0.000"
V_DURATION="0"
# mplayer executable to use
MPLAYER="mplayer"
# No custom mplayer opts
MPLAYER_OPTS=""
MUX_OPTS=""
# Don't do fast encoding
FAST_ENCODING=false
# Don't fake it
FAKE=false
QUIET=false
# Keep the intermediate files (.wav|.mp2|.ac3|.m2v|.m1v)
KEEPFILES=false

# Make note of when encoding starts, to determine total time later.
SCRIPT_START_TIME=$(date +%s)


# ******************************************************************************
# ******************************************************************************
#
#
# FUNCTION DEFINITIONS
#
#
# ******************************************************************************
# ******************************************************************************


# ******************************************************************************
# Y-echo: echo to two places at once (stdout and logfile)
# Output is preceded by the script name that produced it
# Args: $@ == any text string
# If no args are given, echo a separator bar
# Why echo when you can yecho?
# ******************************************************************************

#CV: Functions needed for several things. We might not need everything
##CV: yecho()
yecho()
{
    if test $# -eq 0; then
        printf "\n%s\n\n" "$SEPARATOR"
        # If logfile exists, copy output to it (with pretty formatting)
        test -e "$LOG_FILE" && \
            printf "%s\n%s %s\n%s\n" "$ME" "$ME" "$SEPARATOR" "$ME" >> "$LOG_FILE"
    else
        echo "$@"
        test -e "$LOG_FILE" && \
            printf "%s %s\n" "$ME" "$@" >> "$LOG_FILE"
    fi
}

# ******************************************************************************
# Print usage notes and optional error message, then exit.
# Args: $@ == text string containing error message 
# ******************************************************************************
##CV: usage_error()
usage_error()
{
    printf "%s\n" "$USAGE"
    printf "%s\n" "$SEPARATOR"
    printf "*** Usage error: %s\n" "$@"
    exit 1
}

# ******************************************************************************
# Print out a runtime error specified as an argument, and exit
# ******************************************************************************
##CV: runtime_error()
runtime_error()
{
    killsubprocs
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    yecho "tovid encountered an error during encoding:"
    yecho "    $@"
    echo "Check the contents of $LOG_FILE to see what went wrong."
    if $DEBUG; then :; else
        echo "Run tovid again with the -debug option to produce more verbose"
        echo "output, if the log file doesn't give you enough information."
    fi
    echo " "
    echo "See the tovid website ($TOVID_HOME_PAGE) for what to do next."
    echo "Sorry for the inconvenience!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
}


# ******************************************************************************
# Execute the given command-line string, with appropriate stream redirection
# Args: $@ == text string containing complete command-line
# ******************************************************************************
##CV: cmd_exec(), with some PID retreival func.
cmd_exec()
{
    if $FAKE; then
        yecho
        yecho "    [Fake mode is on; command would be executed here]"
        yecho
        return
    elif $DEBUG; then
        eval "$@" 2>&1 | tee -a "$LOG_FILE" &
    else
        eval "$@" >> "$LOG_FILE" 2>&1 &
    fi
    PIDS="$PIDS $!"
}


# ******************************************************************************
# Kill child processes
# ******************************************************************************
##CV: killsubprocs(), kills everything started with cmd_exec()
killsubprocs()
{
    yecho "Encode stopped, killing all sub processes"
    test -n "$PIDS" && kill $PIDS
}    


# ******************************************************************************
# Estimate whether there is enough disk space to encode
# ******************************************************************************
##CV: check_disk_space() + estimations for different formats
check_disk_space()
{
    # Determine space available in current directory (in MB)
    AVAIL_SPACE=$(df -mP . | awk 'NR != 1 {print $4;}')
    # Rough estimates of KB/sec for different formats
    K_PER_SEC=200
    test "$TGT_RES" = "VCD" && K_PER_SEC=172
    test "$TGT_RES" = "DVD-VCD" && K_PER_SEC=200
    test "$TGT_RES" = "Half-DVD" && K_PER_SEC=300
    test "$TGT_RES" = "DVD" && K_PER_SEC=350
    test "$TGT_RES" = "SVCD" && K_PER_SEC=300

    # If video length is unknown, guess needed space
    # based on original file size
    if test "$V_DURATION" = "0"; then
        CUR_SIZE=$(du -c -k \"$IN_FILE\" | awk 'END{print $1}')
        NEED_SPACE=$(expr $CUR_SIZE \* 2)
        yecho  "The encoding process will require about"
    # Estimate space based as kbps * duration
    else
        NEED_SPACE=$(expr $V_DURATION \* $K_PER_SEC \/ 500)
        yecho "The encoding process is estimated to require $NEED_SPACE MB of disk space."
    fi

    yecho "You currently have $AVAIL_SPACE MB available in this directory."
}



# ******************************************************************************
# Read all command-line arguments, and read any arguments included in the
# default configuration file (if it exists)
# ******************************************************************************
##CV: get_args() + config file arguments
get_args()
{
    # Parse all arguments
    while test $# -gt 0; do
        case "$1" in
        
            # Use config file?
            "-config" )
                # Read in name of config file
                # (will be read in later)
                shift
                CONFIG_FILE="$1"
                ;;

            # PAL or NTSC
            "-pal" )
                TVSYS="PAL"
                BASETVSYS="PAL"
                ;;
            "-ntsc" )
                TVSYS="NTSC"
                BASETVSYS="NTSC"
                ;;
            "-ntscfilm" )
                TVSYS="NTSCFILM"
                BASETVSYS="NTSC"
                ;;

            # Target video resolution
            "-vcd" )      TGT_RES="VCD" ;;
            "-dvd-vcd" )  TGT_RES="DVD-VCD" ;;
            "-svcd" )     TGT_RES="SVCD" ;;
            "-dvd" )      TGT_RES="DVD" ;;
            "-half-dvd" ) TGT_RES="Half-DVD" ;;
            "-kvcd" )     TGT_RES="KVCD" ;;
            "-kvcdx3" )   TGT_RES="KVCDx3" ;;
            "-kvcdx3a" )  TGT_RES="KVCDx3a" ;;
            "-kdvd" )     TGT_RES="KDVD" ;;
            "-bdvd" )     TGT_RES="BDVD" ;;

            # Other options
            "-normalize" )  
                assert_dep normalize "'normalize' not found or installed! You cannot use -normalize."
                DO_NORM=:
                FORCE_ENCODING=:
                ;;
            "-amplitude" )
                shift 
                AUDIO_AMPLITUDE="--amplitude=$1"
                DO_NORM=:
                FORCE_ENCODING=:
                ;;
            "-overwrite" )
                OVERWRITE=:
                ;;
                
            # Aspect ratio
            "-aspect" )
                shift
                # Make sure aspect follows expected formatting (INT:INT)
                if expr match "$1" '[0-9][0-9]*:[0-9][0-9]*$'; then
                    ASPECT_RATIO="$1"
                else
                    usage_error "Please provide an integer ratio to -aspect (i.e. 235:100)"
                fi
                ;;
            "-wide" ) ASPECT_RATIO="16:9" ;;
            "-full" ) ASPECT_RATIO="4:3" ;;
            "-panavision" ) ASPECT_RATIO="235:100" ;;
            "-debug" )
                VERBOSE="-v 1"
                DEBUG=:
                ;;
            "-force" ) FORCE_ENCODING=: ;;
            "-fps" )
                shift
                # If user provided X:Y ratio, use it
                if expr match "$1" '[0-9][0-9]*:[0-9][0-9]*$'; then
                    FORCE_FPSRATIO="$1"
                # Otherwise, tack on a :1 denominator
                elif expr match "$1" '[0-9][0-9]*$'; then
                    FORCE_FPSRATIO="$1:1"
                else
                    usage_error "Please provide an integer number or X:Y ratio to the -fps option"
                fi
                FORCE_FPS=:
                ;;
            "-vbitrate" )
                shift
                VID_BITRATE="$1"
                ;;
            "-quality" )
                shift
                VID_QUALITY="$1"
                ;;
            "-safe" )
                shift
                SAFE_AREA=$(echo $1 | sed 's/%//g')
                ;;
            "-crop" )
                shift
                CROP="$1"
                ;;
            "-filters" )
                shift
                # Parse comma-separated values
                for FILTER in $(echo "$1" | sed 's/,/ /g'); do
                    case "$FILTER" in
                        "none" )
                            DO_DENOISE=false
                            DO_CONTRAST=false
                            DO_DEBLOCK=false
                            ;;
                        "all" )
                            DO_DENOISE=:
                            DO_CONTRAST=:
                            DO_DEBLOCK=:
                            ;;
                        "contrast" )
                            DO_CONTRAST=:
                            ;;
                        "denoise" )
                            DO_DENOISE=:
                            ;;
                        "deblock" )
                            DO_DEBLOCK=:
                            ;;
                    esac
                done
                ;;
            "-abitrate" )
                shift
                AUD_BITRATE=$1
                ;;
            "-priority" )
                shift
                if test "$1" = "low"; then
                    PRIORITY="nice -n 19"
                elif test "$1" = "medium"; then
                    PRIORITY="nice -n 10"
                fi
                ;;
            "-deinterlace" | "-progressive" )
                DEINTERLACE=:
                ;;
            "-interlaced" )
                # Do interlaced encoding
                INTERLACED=:
                ;;
            "-type" )
                shift
                VIDEO_TYPE="$1"
                ;;
            "-discsize" )
                shift
                DISC_SIZE="$1"
                ;;
            "-parallel" )
                PARALLEL=:
                ENCODING_MODE="parallel"
                ;;
            "-mkvsub" )
                shift
                SUBTITLES="-slang $1"
                DO_SUBS=:
                # Use gmplayer
                MPLAYER="gmplayer"
                # Force re-encoding of compliant video,
                # so subtitles can be added
                FORCE_ENCODING=:
                ;;
            "-autosubs" )
                SUBTITLES=""
                ;;
            "-subtitles" )
                shift
                if test -e "$1"; then
                    SUBTITLES="-sub \"$(abspath \"$1\")\""
                    DO_SUBS=:
                else
                    yecho "Cannot find subtitle file $1."
                fi
                FORCE_ENCODING=:
                ;;
            "-update" )
                # Set status update interval
                shift
                SLEEP_TIME="$1"
                ;;
            "-mplayeropts" )
                shift
                MPLAYER_OPTS="$1"
                ;;
            "-ffmpeg" )
                USE_FFMPEG=:
                ;;
            "-nofifo" )
                USE_FIFO=false
                ;;
            "-in" )
                shift
                # Get a full pathname for the infile
                IN_FILE=$(abspath "$1")
                ;;
            "-out" )
                shift
                OUT_PREFIX="$1"
                ;;

            # Null option; ignored.
            "-" )
                ;;
            # Quiet encoding (minimal output)
            "-quiet" )
                QUIET=:
                ;;

            # Fake encoding (print commands only)
            "-fake" )
                FAKE=:
                ;;
            
            # Keep encoded files
            "-keepfiles" )
                KEEPFILES=:
                ;;

            # Ignore unexpected options
            esac

        # Get next argument
        shift
    done

    # Read in the config file, but only if a config
    # file is not already being read (prevents recursion
    # if a config file calls itself).
    if $READING_CONFIG; then :
    else
        # check that a config file exists and is readable
        if test -r "$CONFIG_FILE"; then
            # Make sure file is a tovid config file
            CONFIG_TYPE=$(head -n 1 "$CONFIG_FILE")
            if test "$CONFIG_TYPE" != "tovid"; then
                yecho "$CONFIG_FILE is not a valid tovid configuration file."
                yecho "Skipping $CONFIG_FILE"
            else
                READING_CONFIG=:
                CONFIG_ARGS=$(grep '^-' $CONFIG_FILE | tr '\n' ' ')
                yecho "Using config file $CONFIG_FILE, containing the following options:"
                if test -n "$CONFIG_ARGS"; then
                    yecho "$CONFIG_ARGS"
                    get_args $CONFIG_ARGS
                else
                    yecho "(none)"
                fi
            fi
        fi

    fi # If READING_CONFIG

} # End get_args()


# ******************************************************************************
# Clean up temporary files
# ******************************************************************************
##CV: cleanup() temporary files
cleanup()
{
    cd "$WORKING_DIR"
    yecho "Cleaning up..."
    rm -fv "$YUV_STREAM"
    if $KEEPFILES; then
        yecho "Keeping temporary files in $TMP_DIR"
    else
        yecho "Removing temporary files..."
        rm -rfv "$TMP_DIR"
    fi
}


# ******************************************************************************
# Gather and write statistics on the encoded video
# ******************************************************************************
##CV: write_stats()
write_stats()
{
    # Get total size of all output files
    cd $(dirname "$OUT_FILENAME")
    FINAL_SIZE=$(du -c -k "$OUT_PREFIX"*.mpg | awk 'END{print $1}')
    test -z $FINAL_SIZE && FINAL_SIZE=0

    if $FAKE; then
        :
    else
        yecho "Output files:"
        for OUTFILE in $(ls -1 $OUT_PREFIX.mpg $OUT_PREFIX.[0-9].mpg 2>/dev/null);
        do
            echo "$OUTFILE"
            OUTSIZE=$(du -h "$OUTFILE" | awk 'END{print $1}')
            echo "    $OUTFILE ($OUTSIZE)"
        done
    fi

    # Create stats directory if it doesn't already exist.
    if test ! -d $STAT_DIR; then
        mkdir $STAT_DIR
    fi
    # If no stat file exists, create one with a header describing the stats
    if test ! -f "$STAT_FILE"; then
        STAT_FILE_HEADER=`cat << EOF
$SCRIPT_NAME

    This file contains statistics on videos encoded with 'tovid.'
    Each line shows the results of one encoded video. From left
    to right, the values are:
    
    ===================================================
    tovid version number (TOVID_VERSION)
    name of output file  (OUT_FILENAME)
    length of video, in seconds (V_DURATION)
    resolution of output (TGT_RES)
    TV system: PAL or NTSC (TVSYS)
    final output size in kilobytes (FINAL_SIZE)
    target video bitrate (VID_BITRATE)
    resulting average bitrate (AVG_BITRATE)
    resulting peak bitrate (PEAK_BITRATE)
    minimum GOP size (GOP_MINSIZE)
    maximum GOP size (GOP_MAXSIZE)
    time spent encoding, in seconds (SCRIPT_TOT_TIME)
    CPU model of host machine (CPU_MODEL)
    CPU speed in MHz (CPU_SPEED)
    Input file video codec (ID_VIDEO_FORMAT)
    Input file audio codec (ID_AUDIO_CODEC)
    serial or parallel encoding (ENCODING_MODE)
    MD5sum of the input file (IN_FILE_MD5)
    Width in pixels of input file (ID_VIDEO_WIDTH)
    Height in pixels of input file (ID_VIDEO_HEIGHT)
    Quantization level used (QUANT)
    Total kilobytes of output per minute of video (KB_PER_MIN)
    Ratio of encoding time to video length (ENC_TIME_RATIO)
    Encoding backend used (ffmpeg or mpeg2enc) (BACKEND)
    ===================================================

    Values are stored as comma-separated quoted strings, for ease of
    portability. To import these stats into a spreadsheet or database,
    simply remove these comments from the file.

"TOVID_VERSION", "OUT_FILENAME", "V_DURATION", "TGT_RES", "TVSYS", "FINAL_SIZE", "VID_BITRATE", "AVG_BITRATE", "PEAK_BITRATE", "GOP_MINSIZE", "GOP_MAXSIZE", "SCRIPT_TOT_TIME", "CPU_MODEL", "CPU_SPEED", "ID_VIDEO_FORMAT", "ID_AUDIO_CODEC", "ENCODING_MODE", "IN_FILE_MD5", "ID_VIDEO_WIDTH", "ID_VIDEO_HEIGHT", "QUANT", "KB_PER_MIN", "ENC_TIME_RATIO", "BACKEND"
EOF`


        $QUIET || printf "%s\n" "$STAT_FILE_HEADER" > "$STAT_FILE"
    fi

    # Gather some statistics...
    SCRIPT_END_TIME=$(date +%s)
    SCRIPT_TOT_TIME=$(expr $SCRIPT_END_TIME \- $SCRIPT_START_TIME)
    HHMMSS=$(format_time $SCRIPT_TOT_TIME)
    # Get average/peak bitrates from mplex
    AVG_BITRATE=$(grep 'Average bit-rate' "$LOG_FILE" | awk '{print $6}')
    PEAK_BITRATE=$(grep 'Peak bit-rate' "$LOG_FILE" | awk '{print $6}')
    # Convert to kbits/sec
    test -n $AVG_BITRATE && AVG_BITRATE=$(expr $AVG_BITRATE \/ 1000)
    test -n $PEAK_BITRATE && PEAK_BITRATE=$(expr $PEAK_BITRATE \/ 1000)
    KB_PER_MIN=$(expr $FINAL_SIZE \* 60 \/ $V_DURATION \+ 1)
    ENC_TIME_RATIO=$(echo "scale = 2; $SCRIPT_TOT_TIME / $V_DURATION" | bc)
    if $USE_FFMPEG; then
        BACKEND="ffmpeg"
    else
        BACKEND="mpeg2enc"
    fi

    # Final statistics string (pretty-printed)
    FINAL_STATS_PRETTY=`cat << EOF
    ----------------------------------------
    Final statistics
    ----------------
    tovid $TOVID_VERSION
    File: $OUT_FILENAME, $V_DURATION secs $TGT_RES $TVSYS
    Final size:      $FINAL_SIZE kilobytes
    Target bitrate:  $VID_BITRATE kbits/sec
    Average bitrate: $AVG_BITRATE kbits/sec
    Peak bitrate:    $PEAK_BITRATE kbits/sec
    Took $HHMMSS to encode on $CPU_MODEL $CPU_SPEED mhz
    -----------------------------------------
EOF`

    # Final statistics (comma-delimited quoted strings)
    FINAL_STATS_FORMATTED=`cat << EOF
"$TOVID_VERSION", "$OUT_FILENAME", "$V_DURATION", "$TGT_RES", "$TVSYS", "$FINAL_SIZE", "$VID_BITRATE", "$AVG_BITRATE", "$PEAK_BITRATE", "$GOP_MINSIZE", "$GOP_MAXSIZE", "$SCRIPT_TOT_TIME", "$CPU_MODEL", "$CPU_SPEED", "$ID_VIDEO_FORMAT", "$ID_AUDIO_CODEC", "$ENCODING_MODE", "$IN_FILE_MD5", "$ID_VIDEO_WIDTH", "$ID_VIDEO_HEIGHT", "$QUANT", "$KB_PER_MIN", "$ENC_TIME_RATIO", "$BACKEND"
EOF`

    $FAKE || printf "%s\n" "$FINAL_STATS_FORMATTED" >> "$STAT_FILE"

    yecho
    $QUIET || printf "%s\n" "$FINAL_STATS_PRETTY"
    yecho "Statistics written to $STAT_FILE"
}


# ******************************************************************************
# Print a completion message and exit
# ******************************************************************************
##CV: goodbye()
goodbye()
{
    yecho
    yecho "Done!"
    yecho
    yecho "Your encoded video should be in the file(s) $OUT_FILENAME."
    yecho "Thanks for using tovid!"
    yecho

    exit 0
}


# ******************************************************************************
# ******************************************************************************
#
#
# EXECUTION BEGINS HERE
#
#
# ******************************************************************************
# ******************************************************************************
#CV: Execution blocks
##CV: deal with --version
# Print version number only, if requested
if test "$1" = "-v" || test "$1" = "-version"; then
    echo "$TOVID_VERSION"
    exit 0
fi

##CV: print usage info, if necessary
# Print complete 'tovid' command-line that was used
if ! $QUIET; then
    printf "%s\n" "$SCRIPT_NAME"
    yecho "tovid command-line used:"
    yecho "$@"
fi
get_args "$@"


# ******************************************************************************
#
#CV: Sanity checks
#
# ******************************************************************************
##CV: check if -subtitles is specified with -ffmpeg, in that case exit()
# Can't do -subtitles with -ffmpeg; if both were used, print error and exit
# TODO: Support subtitles in ffmpeg!
if $USE_FFMPEG && $DO_SUBS; then
    usage_error "Sorry, -subtitles is not currently supported with -ffmpeg."
fi


##CV: make sure -in is provided
# Make sure '-in FILE' was provided on the command-line
if test -z "$IN_FILE"; then
    usage_error "Please provide an input filename with the -in option."
fi


##CV: determine if it's a file, or an URI
# Determine whether input is a normal file or a URI of some sort
# (if input name contains "://", it's assumed to be a URI)
if expr "$IN_FILE" : ".*:\/\/" >/dev/null; then
    IN_FILE_TYPE="uri"
else
    IN_FILE_TYPE="file"
fi


##CV: Make sure infile exists
# Make sure infile exists
if test "$IN_FILE_TYPE" = "file"; then
    if test -e "$IN_FILE"; then
        :
    else
        exit_with_error "Could not find input file $IN_FILE. Exiting."
    fi
fi

##CV: Make sure output file exists
if test -z "$OUT_PREFIX"; then
    usage_error "Please provide an output name with the -out option."
fi

##CV: check that outfile is not a directory
if test -d "$OUT_PREFIX"; then
    exit_with_error "Error: The specified output file is a directory.  A filename must be specified."
# If output prefix is a base name only, put output in OUTPUT_DIR
elif test "$OUT_PREFIX" = "$(basename "$OUT_PREFIX")"; then
    OUT_PREFIX="$OUTPUT_DIR/$OUT_PREFIX"
# Otherwise, use the full qualified pathname
else
    OUT_PREFIX=$(abspath "$OUT_PREFIX")
fi

##CV: If output file(s) exist, prompt for overwrite (ask for -overwrite flag)
if test -e "$OUT_FILENAME"; then
    yecho "Output file already exists: $OUT_FILENAME"
    if $OVERWRITE; then
        yecho "Overwriting existing file..."
        rm -fv "$OUT_FILENAME"
    else
        exit_with_error "If you would like to overwrite the existing files, please re-run the script with the 'overwrite' option."
    fi
fi


# ******************************************************************************
#
#CV: Execution setup; change to work directory, create tempdir and log file(s)
#
# ******************************************************************************
$QUIET || echo "Changing to working directory: $WORKING_DIR"
cd "$WORKING_DIR"

##CV: Create a unique temporary directory, named after the given -out name
OUTNAME=$(basename "$OUT_PREFIX")
TMP_DIR=$(tempdir "$WORKING_DIR/$OUTNAME")
# Files to use for temporarily storing video info and encoding progress
SCRATCH_FILE="$TMP_DIR/tovid.scratch"
LOG_FILE="$TMP_DIR/tovid.log"

# Remove temp and log files if they exist
rm -f "$SCRATCH_FILE" "$LOG_FILE"
# Print current command-line to log
echo "$ME $0 $@" >> "$LOG_FILE"
echo "$ME Version $TOVID_VERSION" >> "$LOG_FILE"

##CV: Set full pathnames for A/V streams and output file
AUDIO_WAV="$TMP_DIR/audio.wav"
AUDIO_STREAM="$TMP_DIR/audio.$AUD_SUF"
YUV_STREAM="$TMP_DIR/video.yuv"
VIDEO_STREAM="$TMP_DIR/video.$VID_SUF"
OUT_FILENAME="$OUT_PREFIX.mpg"



# ******************************************************************************
#
#CV: Resolution setup - get standards values out of parameters
#
# Set encoding command-line options (later passed to mpeg2enc, mplayer,
# and mplex) according to the specified TV system and output format.
#
# ******************************************************************************
##CV: 
case "$TVSYS" in
    "PAL" )
        VID_NORM="--video-norm p"
        VID_FPS="--frame-rate 3"
        TGT_FPS="25.000"
        TGT_FPSRATIO="25:1"
        ;;
    "NTSC" )
        VID_NORM="--video-norm n"
        VID_FPS="--frame-rate 4"
        TGT_FPS="29.970"
        TGT_FPSRATIO="30000:1001"
        ;;
    "NTSCFILM" )
        VID_NORM="--video-norm n"
        # VCD can't use 3:2 pulldown; all others can
        if test "$TGT_RES" = "VCD"; then
            VID_FPS="--frame-rate 2"
        else
            VID_FPS="--frame-rate 4 --3-2-pulldown"
        fi
        TGT_FPS="23.976"
        TGT_FPSRATIO="24000:1001"
        ;;
esac

##CV: Set GOP min/max sizes depending on video type and TV system.
# NOTE: These most likely need to be tweaked. If you
# would be interested in doing comparative studies
# of videos encoded with different GOP sizes, please
# let the tovid development team know!
case "$VIDEO_TYPE" in
    "bw" )
        GOP_MINSIZE=6
        case "$TVSYS" in
            "PAL" ) GOP_MAXSIZE=12 ;;
            "NTSC" ) GOP_MAXSIZE=15 ;;
            "NTSCFILM" ) GOP_MAXSIZE=10 ;;
        esac
        ;;
    "animation" )
        GOP_MINSIZE=8
        # Animation uses highest GOP size allowed
        case "$TVSYS" in
            "PAL" ) GOP_MAXSIZE=15 ;;
            "NTSC" ) GOP_MAXSIZE=18 ;;
            "NTSCFILM" ) GOP_MAXSIZE=12 ;;
        esac
        ;;
    "live" )
        GOP_MINSIZE=4
        case "$TVSYS" in
            "PAL" ) GOP_MAXSIZE=9 ;;
            "NTSC" ) GOP_MAXSIZE=11 ;;
            "NTSCFILM" ) GOP_MAXSIZE=9 ;;
        esac
        ;;
esac

##CV: Set disc size in mebibytes (2^20) and audio sampling rate
if echo $TGT_RES | grep -q 'DVD'; then
    : ${DISC_SIZE:=4300}
    SAMPRATE=48000
else
    : ${DISC_SIZE:=700}
    SAMPRATE=44100
fi

##CV: Set anamorph value. DVD, KDVD, and BDVD can do anamorphic widescreen
if test $TGT_RES = "DVD" || test $TGT_RES = "KDVD" || test $TGT_RES = "BDVD"; then
    ANAMORPH=:
else
    ANAMORPH=false
fi

##CV: Default quality 8, if not set by user
: ${VID_QUALITY:=8}

##CV: Set resolution and frame rate according to format and TV system
##CV: Set also the parameters for each format, encoder options, mplex opts, etc.
case "$TGT_RES" in
    # VCD
    "VCD" )
        TGT_WIDTH="352"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="288"
        else
            TGT_HEIGHT="240"
        fi
        AUD_SUF="mp2"
        # Explicitly set audio/video bitrates
        AUD_BITRATE="224"
        VID_BITRATE="1150"
        MPEG2_FMT="-f 1 -K hi-res"
        MUX_OPTS="-f 1"
        VID_SUF="m1v"
        ;;

    # KVCD: VCD resolution, but using MPEG-2 and with KVCD quantization
    "KVCD" )
        TGT_WIDTH="352"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="288"
        else
            TGT_HEIGHT="240"
        fi
        AUD_SUF="mp2"
        # -quality gives bitrates from 400-4000 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 4000 \/ 10)
        : ${VID_BITRATE:=$DEFAULT_BR}
        MPEG2_FMT="-f 2 -b $VID_BITRATE -V 230 -K kvcd -g $GOP_MINSIZE -G $GOP_MAXSIZE -D 8 -d"
        MUX_OPTS="-V -f 5 -b 350 -r 10800"
        VID_SUF="m2v"
        ;;
        
        
    # VCD-on-DVD
    "DVD-VCD" )
        TGT_WIDTH="352"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="288"
        else
            TGT_HEIGHT="240"
        fi
        AUD_SUF="ac3"
        # -quality gives bitrates from 400-4000 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 4000 \/ 10)
        # Use default bitrate if none specified
        : ${VID_BITRATE:=$DEFAULT_BR}
        MPEG2_FMT="-f 8 -b $VID_BITRATE -g $GOP_MINSIZE -G $GOP_MAXSIZE -K hi-res"
        MUX_OPTS="-V -f 8"
        VID_SUF="m2v"
        ;;

    # SVCD
    "SVCD" )
        TGT_WIDTH="480"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="576"
        else
            TGT_HEIGHT="480"
        fi
        AUD_SUF="mp2"
        # -quality gives bitrates from 260-2600 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 2600 \/ 10)
        # Use default bitrate if none specified
        : ${VID_BITRATE:=$DEFAULT_BR}
        MPEG2_FMT="-f 4 -b $VID_BITRATE -K hi-res"
        MUX_OPTS="-V -f 4"
        VID_SUF="m2v"

        ;;

    # Half-D1 DVD
    "Half-DVD" )
        TGT_WIDTH="352"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="576"
        else
            TGT_HEIGHT="480"
        fi
        AUD_SUF="ac3"
        # -quality gives bitrates from 600-6000 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 6000 \/ 10)
        # Use default bitrate if none specified
        : ${VID_BITRATE:=$DEFAULT_BR}
        MPEG2_FMT="-f 8 -b $VID_BITRATE -g $GOP_MINSIZE -G $GOP_MAXSIZE -K hi-res"
        MUX_OPTS="-V -f 8"
        VID_SUF="m2v"
        ;;

    # KVCDx3(a) long-playing, high-resolution MPEG for (S)VCD
    "KVCDx3" | "KVCDx3a" )
        # KVCD, x3, or x3a?
        if test "$TGT_RES" = "KVCDx3"; then
            TGT_WIDTH="528"
        else
            TGT_WIDTH="544"
        fi

        # PAL or NTSC
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="576"
        else
            TGT_HEIGHT="480"
        fi
        AUD_SUF="mp2"
        # -quality gives bitrates from 400-4000 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 4000 \/ 10)
        # Use default bitrate if none specified
        : ${VID_BITRATE:=$DEFAULT_BR}

        # Use optimal (non-standard!) GOP size for live video
        if test "$VIDEO_TYPE" = "live"; then
            GOP_MAXSIZE="24"
        fi
        # KVCDx3(a) is treated as SVCD, since the standard doesn't specify
        # mpeg2enc 1.6.2 seems to want bitrate and buffer size (-b and -V)
        # to be explicit.
        MPEG2_FMT="-f 5 -b $VID_BITRATE -V 230 -K kvcd -g $GOP_MINSIZE -G $GOP_MAXSIZE -D 8 -d"
        MUX_OPTS="-V -f 5 -b 350 -r 10800"
        VID_SUF="m2v"
        ;;

    # DVD (and KDVD/BDVD)
    "DVD" | "KDVD" | "BDVD" )
        TGT_WIDTH="720"
        if test "$TVSYS" = "PAL"; then
            TGT_HEIGHT="576"
        else
            TGT_HEIGHT="480"
        fi
        AUD_SUF="ac3"
        # -quality gives bitrates from 980-9800 kbps
        DEFAULT_BR=$(expr $VID_QUALITY \* 9800 \/ 10)
        # Use default bitrate if none specified
        : ${VID_BITRATE:=$DEFAULT_BR}
        MPEG2_FMT="-f 8 -b $VID_BITRATE -g $GOP_MINSIZE -G $GOP_MAXSIZE -D 10"
        # For KDVD, use KVCD "Notch" quantization
        case "$TGT_RES" in
            "KDVD" )
                MPEG2_FMT="$MPEG2_FMT -K kvcd"
                ;;
            "BDVD" )
                # BVCD "Under" quantization matrix (www.bvcd.com.br)
                # (Intra/Non Intra)
                echo -e \
                "16,18,20,22,26,28,32,39" \
                "\n18,20,22,24,28,32,39,44" \
                "\n20,22,26,28,32,39,44,48" \
                "\n22,22,26,32,39,44,48,54" \
                "\n22,26,32,39,44,48,54,64" \
                "\n26,32,39,44,48,54,64,74" \
                "\n32,39,44,48,54,64,74,84" \
                "\n39,44,48,54,64,74,84,94" \
                "\n20,24,26,28,38,42,46,53" \
                "\n24,26,28,38,42,46,53,58" \
                "\n26,28,38,42,46,53,58,62" \
                "\n28,38,42,46,53,58,62,68" \
                "\n38,42,46,53,58,62,68,78" \
                "\n42,46,53,58,62,68,78,88" \
                "\n46,53,58,62,68,78,88,99" \
                "\n53,58,62,68,78,88,99,99" > "$TMP_DIR/bvcd.matrix" 
                MPEG2_FMT="$MPEG2_FMT -K file=\"$TMP_DIR/bvcd.matrix\"" 
                ;; 
            * )
                MPEG2_FMT="$MPEG2_FMT -K hi-res"
                ;;
        esac
        MUX_OPTS="-V -f 8"
        VID_SUF="m2v"
        ;;

esac # End resolution


# ******************************************************************************
#
#CV: Set nonvideo bitrate, deinterlacing and quality options
#
# ******************************************************************************

yecho

##CV: Find out nonvideo bitrate
# Formula: Sum of all nonvideo bitrates + 1% of total bitrate
NONVIDEO_BITRATE=$(expr \( 101 \* $AUD_BITRATE \+ $VID_BITRATE \) \/ 100)

# Put available mplayer -vf filters into temp file
mplayer -vf help > "$SCRATCH_FILE" 2>&1

##CV: Find out if mplayer's 'pp' option is available.
if grep -q "^ *pp " "$SCRATCH_FILE"; then
    PP_AVAIL=:
elif grep -q "^ *spp " "$SCRATCH_FILE"; then
    SPP_AVAIL=:
else
    PP_AVAIL=false
    SPP_AVAIL=false
fi

##CV: Crop, if requested (add mplayer/mencoder filters)
if test -n "$CROP"; then
    VID_FILTER="$VID_FILTER,crop=$CROP"
fi

##CV: Set up deinterlacing, if requested. (see bash script for ref.)
### - Use the best deinterlacer available, and fall
###   back to others if not available in the user's
###   version of mplayer.
if $DEINTERLACE; then
    # If PP is available, use median deinterlacing
    # NOT ENABLED: pp=md possibly unstable
    # if $PP_AVAIL; then
        #VID_FILTER="-vf pp=md"
    # See if adaptive kernel deinterlacer is available
    if grep -q "^ *kerndeint " "$SCRATCH_FILE"; then
        VID_FILTER="$VID_FILTER,kerndeint"
    # Finally, try lavcdeint
    elif grep -q "^ *lavcdeint " "$SCRATCH_FILE"; then
        VID_FILTER="$VID_FILTER,lavcdeint"
    # Nothing available - print a warning
    else
        yecho "I can't find any deinterlacing options to use. No deinterlacing"
        yecho "will be done on this video (but encoding will continue)."
        yecho "Encoding will resume in 5 seconds..."
        sleep 5s
    fi
    # Deinterlacing for ffmpeg
    FF_ILACE="-deinterlace"
fi

##CV: Default quantization
QUANT=$(expr 13 \- $VID_QUALITY)

##CV: mpeg2enc encoding quality options
# Don't use -q for VCD (since -q implies variable bitrate)
if test "$TGT_RES" = "VCD"; then
    MPEG2_QUALITY="--reduction-4x4 2 --reduction-2x2 1"
    FF_QUANT=""
else
    MPEG2_QUALITY="--reduction-4x4 2 --reduction-2x2 1 -q $QUANT"
    # Use lower qscale
    QUANT=$(expr $QUANT - 2)
    FF_QUANT="-qscale $QUANT"
fi

##CV: Apply requested postprocessing filters, or fall back to the best alternative.
#####CV: CONTINUE FROM HERE.
if $DO_DENOISE; then
    # If high-quality 3D denoising is available, use it
    if grep -q "^ *hqdn3d " "$SCRATCH_FILE"; then
        VID_FILTER="$VID_FILTER,hqdn3d"
    # Otherwise, use normal 3D denoising
    elif grep -q "^ *denoise3d " "$SCRATCH_FILE"; then
        VID_FILTER="$VID_FILTER,denoise3d"
    # If all else fails, use yuvdenoise (if available)
    elif type -p yuvdenoise; then
        YUVDENOISE="yuvdenoise |"
    else
        yecho "Unable to find a suitable denoising filter. Skipping."
    fi
fi
if $DO_CONTRAST; then
    if $PP_AVAIL; then
        VID_FILTER="$VID_FILTER,pp=al:f"
    else
        yecho "Unable to find a suitable contrast-enhancement filter. Skipping."
    fi
fi
if $DO_DEBLOCK; then
    if $PP_AVAIL; then
        VID_FILTER="$VID_FILTER,pp=hb/vb"
    elif $SPP_AVAIL; then
        VID_FILTER="$VID_FILTER,spp"
    else
        yecho "Unable to find a suitable deblocking filter. Skipping."
    fi
fi

# Do fast encoding if requested. Sacrifice quality for encoding speed.
# NOT IMPLEMENTED IN COMMAND-LINE YET!
if $FAST_ENCODING; then
    QUANT=$(expr $QUANT \+ 4)
    MPEG2_QUALITY="-4 4 -2 4 -q $QUANT"
fi

# ******************************************************************************
#
# Probe input file; check for compliance with selected output format.
#
# ******************************************************************************

yecho "Converting $IN_FILE to compliant $TVSYS $TGT_RES format"
yecho "Saving to $OUT_FILENAME"
yecho "Storing log and temporary files in $TMP_DIR"
$DEBUG && yecho "Run 'tail -f $LOG_FILE' in another terminal to monitor the log"

# If multiple CPUs are available, do multithreading in mpeg2enc
if $MULTIPLE_CPUS; then
    yecho "Multiple CPUs detected; mpeg2enc will use multithreading."
    MTHREAD="--multi-thread 2"
else
    MTHREAD=""
fi

yecho


# Probe for width, height, frame rate, and duration
# (only for locally-accessible infiles, not URI-addressed infiles)
if test "$IN_FILE_TYPE" = "file"; then

    yecho "Probing video for information. This may take several minutes..."

    # Get an MD5sum of the input file for statistics
    IN_FILE_MD5=$(md5sum "$IN_FILE" | awk '{print $1}')

    # Assume nothing is compliant unless idvid says so
    # (these will be overridden by idvid for compliant A/V)
    A_VCD1_OK=false
    A_VCD2_OK=false
    A_SVCD_OK=false
    A_DVD_OK=false
    A_NOAUDIO=false
    V_VCD_OK=false
    V_SVCD_OK=false
    V_DVD_OK=false
    V_RES=""
    
    # Override the above A_ and V_ variables by 'eval'ing the output of
    # 'idvid -terse' on the infile. Exit on failure.
    # (Yes, I know eval==evil. Deal.)
    if eval $(idvid -terse "$IN_FILE"); then :; else
        runtime_error "Could not identify source video: $IN_FILE"
    fi

    # Check for available space and prompt if it's not enough
    check_disk_space
    if test "$AVAIL_SPACE" -lt "$NEED_SPACE"; then
        yecho "Available: $AVAIL_SPACE, needed: $NEED_SPACE"
        echo "It doesn't look like you have enough space to encode this video."
        echo "Of course, I could be wrong. Do you want to proceed anyway? (y/n)"
        read PROCEED
        if test "$PROCEED" != "y"; then
            cleanup
            exit 0
        fi
    fi

    # Check for compliance in existing video
    if test "$TGT_RES" = "VCD"; then
        $A_VCD1_OK || $A_VCD2_OK && AUDIO_OK=:
        $V_VCD_OK && test "$V_RES" = "${BASETVSYS}_VCD" && VIDEO_OK=:
        
    elif test "$TGT_RES" = "SVCD"; then
        $A_SVCD_OK && AUDIO_OK=:
        $V_SVCD_OK && test "$V_RES" = "${BASETVSYS}_SVCD" && VIDEO_OK=:

    else # Any DVD format
        $A_DVD_OK && AUDIO_OK=:
        if $V_DVD_OK; then
            if test "$TGT_RES" = "DVD-VCD"; then
                test "$V_RES" = "${BASETVSYS}_VCD" && VIDEO_OK=:
            elif test "$TGT_RES" = "Half-DVD"; then
                test "$V_RES" = "${BASETVSYS}_HALF" && VIDEO_OK=:
            elif test "$TGT_RES" = "DVD"; then
                test "$V_RES" = "${BASETVSYS}_DVD" && VIDEO_OK=:
            fi
        fi
    fi

    yecho "Analysis of file $IN_FILE:"
    yecho "  $ID_VIDEO_WIDTH x $ID_VIDEO_HEIGHT pixels, $ID_VIDEO_FPS fps"
    yecho "  Duration (best guess): $(format_time $V_DURATION) (HH:MM:SS)"
    yecho "  $ID_VIDEO_FORMAT video with $ID_AUDIO_CODEC audio"

    # If no audio stream present, need to generate one later
    if $A_NOAUDIO; then
        AUDIO_OK=false
        GENERATE_AUDIO=:
    fi

    # If both audio and video are OK, stop now - there's no need to convert.
    if ! $FORCE_ENCODING && $AUDIO_OK && $VIDEO_OK; then
        # Create a symbolic link in place of the output file
        $OVERWRITE && rm -f "$OUT_FILENAME"
        ln -s "$IN_FILE" "$OUT_FILENAME"
        yecho
        yecho "Audio and video streams appear to already be compliant with the"
        yecho "selected output format. If you want to force encoding (for instance,"
        yecho "to change the bitrate or take advantage of denoising), run tovid"
        yecho "again with the '-force' option. A symbolic link has been created"
        yecho "in place of the output file:"
        yecho "    $OUT_FILENAME --> $IN_FILE"
        yecho
        yecho "Done!"
        cleanup
        exit 0
    fi
    if ! $FORCE_ENCODING && $VIDEO_OK; then
        yecho
        yecho "Video stream is already compliant with $TVSYS $TGT_RES."
        yecho "No re-encoding is necessary. To force encoding, use -force"
        yecho
    fi
    if ! $FORCE_ENCODING && $AUDIO_OK; then
        yecho
        yecho "Audio stream is already compliant with $TVSYS $TGT_RES."
        yecho "No re-encoding is necessary. To force encoding, use -force"
        yecho
    fi

else # If $IN_FILE_TYPE != "file"
    yecho "Input video is not a locally-accessible file. The input video"
    yecho "will NOT be probed for resolution, length, or compliance."
fi

yecho "Target format:"
yecho "  $TGT_WIDTH x $TGT_HEIGHT pixels, $TGT_FPS fps"
yecho "  $VID_SUF video with $AUD_SUF audio"
yecho "  $VID_BITRATE kbits/sec video, $AUD_BITRATE kbits/sec audio"

# ******************************************************************************
#
# Set aspect ratio
#
# ******************************************************************************

# If user supplied an aspect ratio, use that; normalize the value with
# respect to 100 (i.e., 4:3 becomes normalized to 133:100, or simply 133)
# OVERRIDES AUTO-DETECTED ASPECT RATIO!
if test -n "$ASPECT_RATIO"; then
    yecho "Using explicitly provided aspect ratio of $ASPECT_RATIO"
    PLAY_WIDTH=$(echo $ASPECT_RATIO | awk -F ':' '{print $1}')
    PLAY_HEIGHT=$(echo $ASPECT_RATIO | awk -F ':' '{print $2}')
    V_ASPECT_WIDTH=$(expr $PLAY_WIDTH \* 100 \/ $PLAY_HEIGHT)
# Auto-detected aspect ratio
else
    ASPECT_RATIO="$V_ASPECT_WIDTH:100"
    yecho "Using auto-detected aspect ratio of $ASPECT_RATIO (override with -aspect)"
fi


# Use anamorphic widescreen if supported and suitable
if $ANAMORPH && test "$V_ASPECT_WIDTH" -ge 177; then
    TGT_ASPECT_WIDTH=177
    FF_ASPECT="-aspect 16:9"
    ASPECT_FMT="--aspect 3"
# For all others, overall aspect is 4:3 (133 / 100)
else
    TGT_ASPECT_WIDTH=133
    FF_ASPECT="-aspect 4:3"
    ASPECT_FMT="--aspect 2"
fi

# If cropping, crop values override input video resolution for the
# purposes of knowing when scaling is needed
if test -n "$CROP"; then
    yecho "Cropping with (W:H:X:Y): $CROP"
    ID_VIDEO_WIDTH=$(echo $CROP | awk -F ':' '{print $1}')
    ID_VIDEO_HEIGHT=$(echo $CROP | awk -F ':' '{print $2}')
fi

# Determine width/height to scale to, maintaining aspect
# If aspect is OK, leave it alone
if test "$V_ASPECT_WIDTH" -eq "$TGT_ASPECT_WIDTH"; then
    yecho "No letterboxing necessary"
    INNER_WIDTH=$TGT_WIDTH
    INNER_HEIGHT=$TGT_HEIGHT
# If needed aspect is greater than target format's aspect,
# use full width, and letterbox vertically
elif test "$V_ASPECT_WIDTH" -gt "$TGT_ASPECT_WIDTH"; then
    yecho "Letterboxing vertically"
    INNER_WIDTH=$TGT_WIDTH
    INNER_HEIGHT=$(expr $TGT_HEIGHT \* $TGT_ASPECT_WIDTH \/ $V_ASPECT_WIDTH)
# Otherwise, use full height, and letterbox horizontally
else
    yecho "Letterboxing horizontally"
    INNER_WIDTH=$(expr $TGT_WIDTH \* $V_ASPECT_WIDTH \/ $TGT_ASPECT_WIDTH)
    INNER_HEIGHT=$TGT_HEIGHT
fi

if test $SAFE_AREA -lt 100; then
    yecho "Using a safe area of ${SAFE_AREA}%"
    # Reduce inner size to fit within safe area
    INNER_WIDTH=$(expr $INNER_WIDTH \* $SAFE_AREA \/ 100)
    INNER_HEIGHT=$(expr $INNER_HEIGHT \* $SAFE_AREA \/ 100)
fi

# Round down inner width and height to nearest multiple of 16
# for optimal encoding
INNER_WIDTH=$(expr $INNER_WIDTH \- \( $INNER_WIDTH \% 16 \))
INNER_HEIGHT=$(expr $INNER_HEIGHT \- \( $INNER_HEIGHT \% 16 \))

# Round height back up if possible. Gives slightly more picture space.
if test $(expr $INNER_HEIGHT \+ 16) -le $TGT_HEIGHT; then
    INNER_HEIGHT=$(expr $INNER_HEIGHT \+ 16)
fi

# ******************************************************************************
#
# Set FPS and rescaling options
#
# ******************************************************************************

# Correct wmv 1000fps videos
if $FORCE_FPS; then :
elif test "$ID_VIDEO_FPS" = "1000.000"; then
    FORCE_FPS=:
    FORCE_FPSRATIO=$TGT_FPSRATIO
    yecho "Found 1000fps (wmv) source, setting input to $TGT_FPS fps."
    yecho "Use -fps to force a different input fps (see 'man tovid')"
    # TODO: Instead, use a two-pass encoding (since mencoder can
    # do -ofps)
    # mencoder -ovc copy -oac copy -ofps $TGT_FPSRATIO $INFILE -o twopass
    # then do normal encoding on twopass
fi

# If forced FPS was used, apply it
if $FORCE_FPS; then
    yecho "Forcing input to be treated as $FORCE_FPSRATIO fps."
    ADJUST_FPS="yuvfps -s $FORCE_FPSRATIO -r $TGT_FPSRATIO $VERBOSE |"
# If FPS is already at the target rate, leave it alone
elif test "$ID_VIDEO_FPS" = "$TGT_FPS"; then
    yecho "Input is already $TGT_FPS fps. Framerate will not be altered."
    ADJUST_FPS=""
else
    yecho "Input is not $TGT_FPS fps. Framerate will be adjusted."
    ADJUST_FPS="yuvfps -r $TGT_FPSRATIO $VERBOSE |"
fi

# Scale to the target inner size
if test $ID_VIDEO_WIDTH != $INNER_WIDTH || test $ID_VIDEO_HEIGHT != $INNER_HEIGHT; then
    yecho "Scaling picture to $INNER_WIDTH x $INNER_HEIGHT"
    VID_FILTER="$VID_FILTER,scale=$INNER_WIDTH:$INNER_HEIGHT"
fi

# Do interlaced encoding for everything but VCD (which doesn't support it)
if $INTERLACED && test "$TGT_RES" != "VCD"; then
    # Unneeded, and possibly harmful?
    # MPEG2_FMT="$MPEG2_FMT --interlace-mode 1"

    # Apply deinterleave/reinterleave filters, if needed
    if test -n "$VID_FILTER"; then
        VID_FILTER="il=d:d,$VID_FILTER,il=i:i"
    fi
    YUV4MPEG_ILACE=":interlaced"
    # Add the ilpack video filter
    #VF_POST="$VF_POST -vf-add ilpack"
    # Interlacing for ffmpeg
    FF_ILACE="-interlace"
fi

# Expand to the target outer size
if test $INNER_WIDTH != $TGT_WIDTH || test $INNER_HEIGHT != $TGT_HEIGHT; then
    yecho "Centering picture against a $TGT_WIDTH x $TGT_HEIGHT black background"
    VID_FILTER="$VID_FILTER,expand=$TGT_WIDTH:$TGT_HEIGHT"
fi

# Remove extraneous commas from filter command
if test -n "$VID_FILTER"; then
    VID_FILTER="-vf $(echo "$VID_FILTER" | sed -e 's/,,/,/g' -e 's/^,//')"
fi


# ******************************************************************************
#
# If using ffmpeg, encode and exit
#
# ******************************************************************************

if $USE_FFMPEG; then
    yecho
    yecho "Using ffmpeg to encode audio and video."

    FF_SIZE="-s ${INNER_WIDTH}x${INNER_HEIGHT}"
    FF_FPS="-r $TGT_FPS"
    FF_BITRATE="-maxrate $VID_BITRATE -ab $AUD_BITRATE"
    FF_SAMPRATE="-ar $SAMPRATE"

    # Padding, for any letterboxing to be done
    FF_VPAD=""
    FF_HPAD=""
    FF_VPIX=$(expr \( $TGT_HEIGHT \- $INNER_HEIGHT \) \/ 2)
    FF_HPIX=$(expr \( $TGT_WIDTH \- $INNER_WIDTH \) \/ 2)
    test "$FF_VPIX" -ne 0 && FF_VPAD="-padtop $FF_VPIX -padbottom $FF_VPIX"
    test "$FF_HPIX" -ne 0 && FF_HPAD="-padleft $FF_HPIX -padright $FF_HPIX"

    # Target TV system
    test "$TVSYS" = "PAL" && FF_TARGET="-target pal"
    test "$TVSYS" = "NTSC" && FF_TARGET="-target ntsc"
    test "$TVSYS" = "NTSCFILM" && FF_TARGET="-target film"

    # Target format
    case "$TGT_RES" in
        "VCD" )
            FF_TARGET="$FF_TARGET-vcd"
            ;;
        "SVCD" )
            FF_TARGET="$FF_TARGET-svcd"
            ;;
        * )
            FF_TARGET="$FF_TARGET-dvd"
            ;;
    esac
    
    FF_ENC_CMD="$PRIORITY ffmpeg -i \"$IN_FILE\" \
        $FF_QUANT $FF_BITRATE $FF_TARGET $FF_FPS $FF_ILACE \
        $FF_SIZE $FF_VPAD $FF_HPAD $FF_ASPECT"
    $OVERWRITE && FF_ENC_CMD="$FF_ENC_CMD -y "
    FF_ENC_CMD="$FF_ENC_CMD \"$OUT_FILENAME\""
    yecho "Encoding video and audio with the following command:"
    yecho "$FF_ENC_CMD"


    cmd_exec "$FF_ENC_CMD"
    

    if $FAKE; then
        :
    else
        file_output_progress "$OUT_FILENAME" "Encoding with ffmpeg"
        wait
    fi
    yecho
    $FAKE || write_stats
    cleanup
    goodbye
fi


# ******************************************************************************
#
# Encode and normalize audio
#
# ******************************************************************************

yecho

if $PARALLEL && $DO_NORM; then
    yecho "Cannot normalize audio in parallel mode! Turning off -parallel."
    PARALLEL=false
fi

if $PARALLEL; then
    rm -f "$AUDIO_STREAM"
    mkfifo "$AUDIO_STREAM"
fi


# If audio is already in the chosen output format, do not re-encode.
if ! $FORCE_ENCODING && $AUDIO_OK; then
    yecho "Found compliant audio and dumping the stream."
    precho "This sometimes causes errors when multiplexing; add '-force' to the tovid command line to re-encode if multiplexing fails."
    yecho "Copying the existing audio stream with the following command:"
    AUDIO_CMD="$PRIORITY mplayer $MPLAYER_OPTS \"$IN_FILE\" -dumpaudio -dumpfile \"$AUDIO_STREAM\""
    yecho "$AUDIO_CMD"
    cmd_exec "$AUDIO_CMD"

    if ! $FAKE && ! $PARALLEL; then
        file_output_progress "$AUDIO_STREAM" "Copying compliant audio stream"
        wait
    fi

# Re-encode audio
else

    AUDIO_IN_FILE=$IN_FILE

    # When normalizing, we need a wave file.
    if $DO_NORM; then
        rm -f "$AUDIO_WAV"
        AUDIO_IN_FILE="$AUDIO_WAV"

        AUDIO_CMD="$PRIORITY mplayer $MPLAYER_OPTS -quiet -vc null -vo null -ao pcm:waveheader:file=\"$AUDIO_WAV\" \"$IN_FILE\""

        # Generate or dump audio
        yecho "Normalizing the audio stream."
        yecho "Creating WAV of audio stream with the following command:"
        yecho "$AUDIO_CMD"

        cmd_exec "$AUDIO_CMD"

        if ! $FAKE; then
            file_output_progress "$AUDIO_WAV" "Creating wav of audio stream"
            wait

            # Make sure the audio stream exists before proceeding
            if test ! -f "$AUDIO_WAV"; then
                    runtime_error "Could not extract audio from original video"
            fi
        fi

        # Normalize the wave file.
        $FAKE || normalize $AUDIO_AMPLITUDE "$AUDIO_WAV"
    fi

    AUDIO_ENC="$PRIORITY ffmpeg"

    if $GENERATE_AUDIO; then
        # Read input from /dev/zero to generate a silent audio file
        AUDIO_ENC="$AUDIO_ENC -f s16le -i /dev/zero -t $V_DURATION"
        yecho "Generating a silent audio stream with the following command:"
    else
        # Encode audio stream directly from the input file
        AUDIO_ENC="$AUDIO_ENC -i \"$AUDIO_IN_FILE\""
        yecho "Encoding audio stream to $AUD_SUF with the following command:"
    fi
    AUDIO_ENC="$AUDIO_ENC -vn -ab $AUD_BITRATE -ar $SAMPRATE -ac 2"
    AUDIO_ENC="$AUDIO_ENC -acodec $AUD_SUF -y \"$AUDIO_STREAM\""
    yecho "$AUDIO_ENC"
    cmd_exec "$AUDIO_ENC"

    # For parallel, nothing else to do right now
    if $FAKE || $PARALLEL; then
        :
    # If not in parallel mode, show output progress
    # and wait for successful completion
    else
        file_output_progress "$AUDIO_STREAM" "Encoding audio to $AUD_SUF"
        wait

        if test -f "$AUDIO_STREAM"; then
            yecho "Audio encoding finished successfully."
        else
            runtime_error "There was a problem with encoding the audio to $AUD_SUF format."
        fi
    fi # If ! $PARALLEL

fi # encode audio


# ******************************************************************************
#
# Encode video
#
# ******************************************************************************

yecho

# Remove yuv stream
rm -f "$YUV_STREAM"
if $PARALLEL; then
    rm -f "$VIDEO_STREAM"
    mkfifo "$VIDEO_STREAM"
fi

# If existing video is OK, skip video encoding and just copy the stream
if ! $FORCE_ENCODING && $VIDEO_OK; then
    yecho "Copying existing video stream with the following command:"
    VID_COPY_CMD="mencoder -of rawvideo -nosound -ovc copy \"$IN_FILE\" -o \"$VIDEO_STREAM\""
    yecho "$VID_COPY_CMD"


    # Copy the video stream
    cmd_exec "$VID_COPY_CMD"


    if $FAKE || $PARALLEL; then
        :
    else
        file_output_progress "$VIDEO_STREAM" "Copying existing video stream"
        wait
    fi
else
    yecho "Encoding video stream with the following commands:"

    # Normal one-pass encoding, with mplayer piped into the mjpegtools
    if $USE_FIFO; then
        mkfifo "$YUV_STREAM"
    fi
    VID_PLAY_CMD="$PRIORITY $MPLAYER -benchmark -nosound -noframedrop $SUBTITLES -vo yuv4mpeg:file=\"$YUV_STREAM\"${YUV4MPEG_ILACE} $VID_FILTER $MPLAYER_OPTS \"$IN_FILE\""
    VID_ENC_CMD="cat \"$YUV_STREAM\" | $YUVDENOISE $ADJUST_FPS $PRIORITY mpeg2enc --sequence-length $DISC_SIZE --nonvideo-bitrate $NONVIDEO_BITRATE $MTHREAD $ASPECT_FMT $MPEG2_FMT $VID_FPS $VERBOSE $VID_NORM $MPEG2_QUALITY -o \"$VIDEO_STREAM\""
    yecho $VID_PLAY_CMD
    yecho $VID_ENC_CMD
    # Start encoding


    cmd_exec "$VID_PLAY_CMD"


    if $USE_FIFO; then
        file_output_progress "$YUV_STREAM" "Ripping raw uncompressed video stream"
    fi
    

    cmd_exec "$VID_ENC_CMD"


    # For parallel encoding, nothing further yet
    if $FAKE || $PARALLEL; then
        :
    # Show progress report while video is encoded
    else
        file_output_progress "$VIDEO_STREAM" "Encoding video stream"
        wait
        :
    fi
fi

yecho

# For non-parallel encoding/multiplexing,
# make sure the video and audio streams exist before proceeding
if $FAKE || $PARALLEL; then
    :
else
    test ! -f "$AUDIO_STREAM" && \
        runtime_error "The audio stream did not encode properly, and no output file exists."
    test ! -f "$VIDEO_STREAM" && \
        runtime_error "The video stream did not encode properly, and no output file exists."
fi


# ******************************************************************************
#
# Multiplex and finish up
#
# ******************************************************************************

if ! $FAKE; then
    AUDIO_SIZE=$(du -c -b "$AUDIO_STREAM" | awk 'END{print $1}')
    VIDEO_SIZE=$(du -c -b "$VIDEO_STREAM" | awk 'END{print $1}')
    # Total size of streams so far (in MBytes)
    STREAM_SIZE=$(expr \( $AUDIO_SIZE \+ $VIDEO_SIZE \) \/ 1000000)
    # If it exceeds disc size, add '%d' field to allow mplex to split output
    if test $STREAM_SIZE -gt $DISC_SIZE; then
        OUT_FILENAME=$(echo "$OUT_FILENAME" | sed -e 's/\.mpg$/.%d.mpg/')
    fi
fi


MPLEX_CMD="mplex $MUX_OPTS -o \"$OUT_FILENAME\" \"$VIDEO_STREAM\" \"$AUDIO_STREAM\""
yecho "Multiplexing audio and video together with the following command:"
yecho $MPLEX_CMD

cmd_exec "$MPLEX_CMD"

# Parallel encoding doesn't enter the progress
# loop until multiplexing begins.
if $PARALLEL; then
    # If video is being re-encoded
    if ! $VIDEO_OK || $FORCE_ENCODING; then
        file_output_progress "$OUT_FILENAME" "Encoding and multiplexing in parallel"
        wait
    fi
fi

wait
if test -n $?; then
    yecho "Multiplexing finished successfully"
else
    runtime_error "There was a problem multiplexing the audio and video together."
fi

$FAKE || write_stats
cleanup
goodbye