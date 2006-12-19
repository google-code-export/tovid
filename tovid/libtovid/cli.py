#! /usr/bin/env python
# cli.py

"""This module provides an interface for running command-line applications.
Two primary classes are provided:

    Command:  For constructing and executing command-line commands
    Pipe:     For piping commands together
    
Commands are constructed by specifying a program to run, and each separate
argument to pass to that program. Arguments are used in a platform-independent
way, so there is no need to escape shell-specific characters or do any quoting
of arguments.

Commands may be executed in the foreground or background; they can print their
output on standard output, or capture it in a string variable.

For example:

    >>> echo = Command('echo', "Hello world")
    >>> echo.run()                                # doctest: +SKIP
    Hello world

Commands may be connected together with pipes:

    >>> sed = Command('sed', 's/world/nurse/')
    >>> pipe = Pipe(echo, sed)
    >>> pipe.run()                                # doctest: +SKIP
    Hello nurse

Command output may be captured and retrieved later with get_output():

    >>> echo.run(capture=True)
    >>> echo.get_output()
    'Hello world\\n'

"""
# Note: Some of the run() tests above will fail doctest.testmod(), since output
# from Command subprocesses is not seen as real output by doctest. The current
# workaround is to use the "doctest: +SKIP" directive (new in python 2.5).
# For other directives see http://www.python.org/doc/lib/doctest-options.html

__all__ = [\
    'Command',
    'Pipe']

import os
import sys
import doctest
import signal
from subprocess import Popen, PIPE
from libtovid import log

class Command:
    """A command-line statement, consisting of a program and its arguments,
    with support for various modes of execution.
    """
    def __init__(self, program, *args):
        """Create a Command to run a program with the given arguments.
        
            program: A string containing the name of a program to execute
            args:    Individual arguments to supply the command with
        
        For example:
        
            >>> cmd = Command('echo', 'Hello world')
            
        """
        self.program = program
        self.args = []
        for arg in args:
            self.add(arg)
        self.proc = None
        self.output = ''

    def add(self, *args):
        """Append one or more arguments to the command. Each argument passed
        to this function is converted to string form, and treated as a single
        argument in the command. No special quoting or escaping of argument
        contents is necessary.
        """
        for arg in args:
            self.args.append(str(arg))
    
    def run(self, capture=False, background=False):
        """Run the command and capture or display output.
        
            capture:    False to show command output on stdout,
                        True to capture output for retrieval by get_output()
            background: False to wait for command to finish running,
                        True to run process in the background
        
        By default, this function displays all command output, and waits
        for the program to finish running, which is usually what you'd want.
        Capture output if you don't want it printed immediately (and call
        get_output() later to retrieve it).

        This function does not allow special stream redirection. For that,
        use run_redir().
        """
        if capture:
            # For now, print standard error even when capturing
            self.run_redir(None, PIPE, stderr=None)
        else:
            self.run_redir(None, None, stderr=None)
        if not background:
            self.wait()

    def run_redir(self, stdin=None, stdout=None, stderr=None):
        """Execute the command using the given stream redirections.
        
            stdin:  Filename or File object to read input from
            stdout: Filename or File object to write output to
            stderr: Filename or File object to write errors to
        
        Use None for regular system stdin/stdout/stderr (default behavior).
        
        This function is used internally by run(); if you need to do stream
        redirection (ex. `spumux < menu.mpg > menu_subs.mpg`), use this
        function instead of run(), and call wait() afterwards if needed.
        """
        self.output = ''
        # Open files if string filenames were provided
        if type(stdin) == str:
            stdin = open(stdin, 'r')
        if type(stdout) == str:
            stdout = open(stdout, 'w')
        if type(stderr) == str:
            stderr = open(stderr, 'w')
        # Run the subprocess
        self.proc = Popen([self.program] + self.args,
                          stdin=stdin, stdout=stdout, stderr=stderr)

    def wait(self):
        """Wait for the command to finish running. If a KeyboardInterrupt
        occurs (user pressed Ctrl-C), kill the subprocess (and re-raise the
        KeyboardInterrupt exception).
        """
        if not isinstance(self.proc, Popen):
            print "**** Can't wait(): Command is not running"
            return
        try:
            self.proc.wait()
        except KeyboardInterrupt:
            os.kill(self.proc.pid, signal.SIGTERM)
            raise KeyboardInterrupt

    def get_output(self):
        """Wait for the command to finish running, and return a string
        containing the command's output. If this command is piped into another,
        return that command's output instead. Returns an empty string if the
        command has not been run yet.
        """
        if self.output is '' and isinstance(self.proc, Popen):
            self.output = self.proc.communicate()[0]
        return self.output

    def __str__(self):
        """Return a string representation of the Command, as it would look if
        run in a command-line shell.
        """
        ret = self.program
        for arg in self.args:
            ret += " %s" % _enc_arg(arg)
        return ret


class Pipe:
    """A series of Commands, each having its output piped into the next.
    """
    def __init__(self, *commands):
        """Create a new Pipe containing all the given Commands."""
        self.commands = []
        for cmd in commands:
            self.add(cmd)
        self.proc = None
    
    def add(self, *commands):
        """Append the given commands to the end of the pipeline."""
        for cmd in commands:
            self.commands.append(cmd)

    def run(self, capture=False, background=False):
        """Run all Commands in the pipeline, doing appropriate stream
        redirection for piping.
        
            capture:    False to show pipeline output on stdout,
                        True to capture output for retrieval by get_output()
        
        """
        self.output = ''
        prev_stdout = None
        # Run each command, piping to the next
        for cmd in self.commands:
            # If this is not the last command, pipe into the next one
            if cmd != self.commands[-1]:
                cmd.run_redir(prev_stdout, PIPE)
                prev_stdout = cmd.proc.stdout
            # Last command in pipeline; direct output appropriately
            else:
                if capture:
                    cmd.run_redir(prev_stdout, PIPE)
                else:
                    cmd.run_redir(prev_stdout, None)
        # Wait for last command to finish?
        if not background:
            cmd.wait()

    def get_output(self):
        """Wait for the pipeline to finish executing, and return a string
        containing the output from the last command in the pipeline.
        """
        return self.commands[-1].get_output()

    def __str__(self):
        """Return a string representation of the Pipe.
        """
        commands = [str(cmd) for cmd in self.commands]
        return ' | '.join(commands)


def _enc_arg(arg):
    """Quote an argument for proper handling of special shell characters.
    Don't quote unless necessary. For example:

        >>> print _enc_arg("spam")
        spam
        >>> print _enc_arg("spam & eggs")
        'spam & eggs'
        >>> print _enc_arg("['&&']")
        '['\\''&&'\\'']'
    
    This is used internally by Command; you'd only need this if you're running
    shell programs without using the Command class.
    """
    arg = str(arg)
    # At the first sign of any special character in the argument,
    # single-quote the whole thing and return it (escaping ' itself)
    for char in ' #"\'\\&|<>()[]!?*':
        if char in arg:
            return "'%s'" % arg.replace("'", "'\\''")
    # No special characters found; use literal string
    return arg


# An idea to test...
FAKE = False
def fake(true_or_false):
    """Module-level switch to turn on/off fake execution. Any Commands or
    Pipes run while FAKE is True will not actually be executed.
    """
    FAKE = true_or_false

if __name__ == '__main__':
    doctest.testmod(verbose=True)
