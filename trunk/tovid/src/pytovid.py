# -* python -*

# pytovid
# Convert a video into an (S)VCD/DVD-compliant MPEG
# (to replace the 'tovid' shell script)

import sys, libtovid
from libtovid import Video
from libtovid.TDL import Parser

if __name__ == '__main__':
    """Create a Video element from the provided command-line options,
    and generate it using the Video module."""
    if len(sys.argv) < 5:
        print "Usage: pytovid [options] -in FILE -out OUTNAME"
        print "See the 'tovid' manual page for more details."
        sys.exit()

    # Create a TDL video element definition using the
    # provided command-line options

    # Insert a dummy element/name declaration
    sys.argv.insert(0, 'Video')
    sys.argv.insert(1, '"FOO VIDEO"')

    par = Parser()
    elems = par.parse_args(sys.argv)
    print "Parsed Video element:"
    print elems[0].tdl_string()
    print "Generating video..."
    Video.generate(elems[0])

