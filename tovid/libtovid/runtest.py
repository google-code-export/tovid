#! /usr/bin/env python
# runtest.py

"""libtovid test script

Execute this script to run tests on the modules in libtovid. These tests
consist of executing each libtovid module standalone; it is presumed that
each module to be tested contains at least the following:

    import unittest
    if __name__ == '__main__':
        unittest.main()

which runs unit tests, or:

    import doctest
    if __name__ == '__main__':
        doctest.testmod(verbose=True)

which does an automated verification of the docstrings in each module.

NB -- You're going to get lots of output, so a >log.txt is advised.
"""

import os
import commands
from glob import glob

# Unit test modules
mod_test = glob('test/*.py')
# Library modules
# mod_libtovid = glob('*.py') ?
mod_libtovid = [\
    'cli.py',
    'deps.py',
    'layout.py',
    'media.py',
    'opts.py',
    'standard.py',
    'stats.py',
    'utils.py']
mod_author = glob('author/*.py')
mod_render = glob('render/*.py')
mod_transcode = glob('transcode/*.py')
modules = mod_libtovid + mod_render + mod_author + mod_transcode

for mod in modules:
    print "Testing: %s" % mod
    try:
        print commands.getoutput('python %s' % mod)
    except KeyboardInterrupt:
        print "Test interrupted."
        exit()
