#! /usr/bin/env python
# mvg.py

"""A Python interface for reading/writing Magick Vector Graphics (MVG)[1].

Run this script standalone for a demonstration:

    $ python libtovid/mvg.py

To build your own MVG vector image using this module, fire up your Python
interpreter:

    $ python

And do something like this:

    >>> from libtovid.mvg import MVG
    >>> pic = MVG(800, 600)

This creates an image (pic) at 800x600 display resolution. pic has a wealth
of draw functions, as well as a rough-and-ready editor interface (shown later).

This thing is pretty low-level for the time being; MVG is, as one user has
described it[2], the "assembly language" of vector graphics. But basically,
you can just call function names that resemble their MVG-syntax counterparts.
Now that you have an MVG object (pic), you can draw on it:

    >>> pic.fill('blue')
    >>> pic.rectangle((0, 0), (800, 600))
    >>> pic.fill('white')
    >>> pic.rectangle((320, 240), (520, 400))

If you want to preview what you have so far, call render():

    >>> pic.render()

This calls convert with a -draw command and -composite miff:- | display to
show the image. Whatever--it lets you see what the image looks like so far.
Press 'q' or ESC to close the preview window.

You can show the current MVG text contents (line-by-line) with:

    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: fill "white"
    4: rectangle 320,240 520,400
    >

This is where the "editor" interface comes in. Each line is numbered, and the
current "cursor" position is shown by a '>' character. You can move the cursor
with goto(line_number):

    >>> pic.goto(3)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    > 3: fill "white"
    4: rectangle 320,240 520,400

The cursor indicates where new commands are inserted; for instance:

    >>> pic.stroke('black')
    >>> pic.stroke_width(2)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: stroke "black"
    4: stroke-width 2
    > 5: fill "white"
    6: rectangle 320,240 520,400

Notice that the two new commands were inserted (in order) at the cursor
position. To resume appending at the end, call goto_end():

    >>> pic.goto_end()
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: stroke "black"
    4: stroke-width 2
    5: fill "white"
    6: rectangle 320,240 520,400
    >

You can remove a given line number (or range of lines) with:

    >>> pic.remove(3, 4)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: fill "white"
    4: rectangle 320,240 520,400
    >

You can undo all insert, append, or remove operations with:

    >>> pic.undo(2)


You can keep drawing on the image, and call render() whenever you want to
preview.

Oh, by the way--this is almost totally untested, so please report bugs if/when
you find them.

References:
[1] http://www.imagemagick.org/script/magick-vector-graphics.php
[2] http://studio.imagemagick.org/pipermail/magick-developers/2002-February/000156.html


MVG examples:
-------------

Radial gradient example
(From http://www.linux-nantes.fr.eu.org/~fmonnier/OCaml/MVG/u.mvg.html):

    push graphic-context
      encoding "UTF-8"
      viewbox 0 0 260 180
      affine 1 0 0 1 0 0
      push defs
        push gradient 'Gradient_B' radial 130,90 130,90 125
          gradient-units 'userSpaceOnUse'
          stop-color '#4488ff' 0.2
          stop-color '#ddaa44' 0.7
          stop-color '#ee1122' 1
        pop gradient
      pop defs
      push graphic-context
        fill 'url(#Gradient_B)'
        rectangle 0,0 260,180
      pop graphic-context
    pop graphic-context

Pie chart example: http://www.imagemagick.org/source/piechart.mvg

"""
import sys
import commands

# TODO: Separate editor interface from MVG data structure
class MVG:
    """A Magick Vector Graphics (MVG) image with load/save, insert/append,
    and low-level drawing functions based on the MVG syntax.

    Drawing commands are mostly identical to their MVG counterparts, e.g.
    these two are equivalent:

        rectangle 100,100 200,200       # MVG command
        rectangle((100,100), (200,200)) # Python function

    The only exception is MVG commands that are hyphenated. For these, use an
    underscore instead:

        font-family "Serif"      # MVG command
        font_family("Serif")     # Python function

    """
    def __init__(self, width=800, height=600):
        self.clear()
        self.width = width
        self.height = height

    def clear(self):
        """Clear the current contents and position the cursor at line 1."""
        self.data = [''] # Line 0 is null
        self.cursor = 1
        self.history = []

    def load(self, filename):
        """Load MVG from the given file."""
        self.clear()
        infile = open(filename, 'r')
        for line in infile.readlines():
            cleanline = line.lstrip(' \t').rstrip(' \n\r')
            # Convert all single-quotes to double-quotes
            cleanline = cleanline.replace("'", '"')
            self.append(cleanline)
        infile.close()

    def save(self, filename):
        """Save to the given MVG file."""
        outfile = open(filename, 'w')
        for line in self.data:
            outfile.write("%s\n" % line)
        outfile.close()

    def code(self):
        """Return complete MVG text with line numbers and a > at the
        cursor position. Useful for doing interactive editing."""
        code = ''
        line = 1
        while line < len(self.data):
            # Put a > at the cursor position
            if line == self.cursor:
                code += "> "
            code +=  "%s: %s\n" % (line, self.data[line])
            line += 1
        # If cursor is after the last line
        if line == self.cursor:
            code += ">"
        print code

    def render(self):
        """Render the MVG image with ImageMagick, and display it."""
        # TODO: Write .mvg to a file and use @drawfile; command-line length
        # is exceeded easily with the current approach
        cmd = "convert -size %sx%s " % (self.width, self.height)
        cmd += " xc:none "
        cmd += " -draw '%s' " % ' '.join(self.data)
        cmd += " -composite miff:- | display"
        print "Creating preview rendering."
        print "Press 'q' or ESC in the image window to close the image."
        print commands.getoutput(cmd)

    def goto(self, line_num):
        """Move the insertion cursor to the start of the given line."""
        if line_num <= 0 or line_num > (len(self.data) + 1):
            print "Can't goto line %s" % line_num
            sys.exit(1)
        else:
            self.cursor = line_num

    def goto_end(self):
        """Move the insertion cursor to the last line in the file."""
        self.goto(len(self.data))

    def remove(self, from_line, to_line=None):
        """Remove the given line, or range of lines, and position the cursor
        where the removed lines were."""
        # Remove a single line
        if not to_line:
            to_line = from_line
        cur_line = from_line
        while cur_line <= to_line:
            self.history.append(['remove', cur_line, self.data.pop(cur_line)])
            cur_line += 1
        self.cursor = from_line

    def extend(self, mvg):
        """Extend self to include all data from the given MVG object."""
        self.data.extend(mvg.data)

    def append(self, mvg_string):
        """Append the given MVG string as the last line, and position the
        cursor after the last line."""
        self.goto_end()
        self.insert(mvg_string)

    def insert(self, mvg_string):
        """Insert the given MVG string before the current line, and position
        the cursor after the inserted line."""
        self.history.append(['insert', self.cursor])
        self.data.insert(self.cursor, mvg_string)
        self.cursor += 1

    def undo(self, steps=1):
        """Undo the given number of operations. Leave cursor at end."""
        step = 0
        while step < steps and len(self.history) > 0:
            action = self.history.pop()
            cmd = action[0]
            line_num = action[1]
            # Undo insertion
            if cmd == 'insert':
                print "Undoing insertion at line %s" % line_num
                self.data.pop(action[1])
            # Undo removal
            elif cmd == 'remove':
                print "Undoing removal at line %s" % line_num
                self.data.insert(line_num, action[2])
            step += 1
        if step < steps:
            print "No more to undo."
        self.goto_end()

    # Draw commands

    def affine(self, (sx, rx), (ry, sy), (tx, ty)):
        self.insert('affine %s %s %s %s %s %s' % (sx, rx, ry, sy, tx, ty))

    def arc(self, (x0, y0), (x1, y1), (a0, a1)):
        self.insert('arc %s,%s %s,%s %s,%s' % (x0, y0, x1, y1, a0, a1))

    def bezier(self, point_list):
        # point_list = [(x0, y0), (x1, y1), ... (xn, yn)]
        command = 'bezier'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)
        
    def circle(self, (center_x, center_y), (perimeter_x, perimeter_y)):
        self.insert('circle %s,%s %s,%s' % \
                    (center_x, center_y, perimeter_x, perimeter_y))

    def clip_path(self, url):
        self.insert('clip-path url(%s)' % url)

    def clip_rule(self, rule):
        # rule in [evenodd, nonzero]
        self.insert('clip-rule %s' % rule)

    def clip_units(self, units):
        # May be: userSpace, userSpaceOnUse, objectBoundingBox
        self.insert('clip-units %s' % units)

    def color(self, (x, y), method='floodfill'):
        # method may be: point, replace, floodfill, filltoborder, reset
        self.insert('color %s,%s %s' % (x, y, method))
    
    def decorate(self, decoration):
        # decoration in [none, line-through, overline, underline]
        self.insert('decorate %s' % decoration)

    def ellipse(self, (center_x, center_y), (radius_x, radius_y),
                (arc_start, arc_stop)):
        self.insert('ellipse %s,%s %s,%s %s,%s' % \
                (center_x, center_y, radius_x, radius_y, arc_start, arc_stop))
        
    def fill(self, color):
        """Set the current fill color."""
        self.insert('fill "%s"' % color)
    
    def fill_opacity(self, opacity):
        # opacity may be [0.0-1.0], or [0-100]%
        # TODO: Check for float (e.g. 0.7), int (eg 70), or string (eg 70%)
        # and do correct formatting
        self.insert('fill-opacity %s' % opacity)
    
    def fill_rule(self, rule):
        # rule may be: evenodd, nonzero
        self.insert('fill-rule %s' % rule)
    
    def font(self, name):
        """Set the current font, by name."""
        self.insert('font "%s"' % name)
    
    def font_family(self, family):
        """Set the current font, by family name."""
        self.insert('font-family "%s"' % family)
    
    def font_size(self, pointsize):
        """Set the current font size in points."""
        self.insert('font-size %s' % pointsize)
    
    def font_stretch(self, stretch_type):
        # May be e.g. normal, condensed, ultra-condensed, expanded ...
        self.insert('font-stretch %s' % stretch_type)
    
    def font_style(self, style):
        # May be: all, normal, italic, oblique
        self.insert('font-style %s' % style)
    
    def font_weight(self, weight):
        # May be: all, normal, bold, 100, 200, ... 800, 900
        self.insert('font-weight %s' % weight)
    
    def gradient_units(self, units):
        # May be: userSpace, userSpaceOnUse, objectBoundingBox
        self.insert('gradient-units %s' % units)
    
    def gravity(self, direction):
        self.insert('gravity %s' % direction)
    
    def image(self, compose, (x, y), (width, height), filename):
        # compose may be e.g. Add, Clear, Copy, Difference, Over ...
        self.insert('image %s %s,%s %s,%s "%s"' % \
                    (compose, x, y, width, height, filename))
    
    def line(self, (x0, y0), (x1, y1)):
        """Draw a line from (x0, y0) to (x1, y1)."""
        self.insert('line %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def matte(self, (x, y), method='floodfill'):
        # method may be: point, replace, floodfill, filltoborder, reset
        # (What do x, y mean?)
        self.insert('matte %s,%s %s' % (x, y, method))

    def offset(self, offset):
        self.insert('offset %s' % offset)

    def opacity(self, opacity):
        self.insert('opacity %s' % opacity)

    def path(self, point_list):
        # point_list = [(x0, y0), (x1, y1), ... (xn, yn)]
        command = 'path'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)

    def point(self, (x, y)):
        self.insert('point %s,%s' % (x, y))

    def polygon(self, point_list):
        # point_list = [(x0, y0), (x1, y1), ... (xn, yn)]
        command = 'polygon'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)
    
    def polyline(self, point_list):
        # point_list = [(x0, y0), (x1, y1), ... (xn, yn)]
        command = 'polyline'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)
    
    def rectangle(self, (x0, y0), (x1, y1)):
        """Draw a rectangle from (x0, y0) to (x1, y1)."""
        self.insert('rectangle %s,%s %s,%s' % (x0, y0, x1, y1))
        
    def rotate(self, angle):
        self.insert('rotate %s' % angle)

    def roundrectangle(self, (x0, y0), (x1, y1), (width, height)):
        self.insert('roundrectangle %s,%s %s,%s %s,%s' % \
                (x0, y0, x1, y1, width, height))

    def scale(self, (x, y)):
        self.insert('scale %s,%s' % (x, y))

    def skewX(self, angle):
        self.insert('skewX %s' % angle)
    
    def skewY(self, angle):
        self.insert('skewY %s' % angle)

    def stop_color(self, color, offset):
        self.insert('stop-color %s %s' % (color, offset))
        
    def stroke(self, color):
        """Set the current stroke color."""
        self.insert('stroke %s' % color)

    def stroke_antialias(self, flag):
        # flag in [0, 1]
        self.insert('stroke-antialias %s' % flag)

    def stroke_dasharray(self, array):
        # array in [none, (numeric list)]
        print "stroke_dasharray() not implemented yet"
        
    def stroke_dashoffset(self, offset):
        self.insert('stroke-dashoffset %s' % offset)

    def stroke_linecap(self, cap_type):
        # cap_type in [butt, round, square]
        self.insert('stroke-linecap %s' % cap_type)

    def stroke_linejoin(self, join_type):
        # join_type in [bevel, miter, round]
        self.insert('stroke-linejoin %s' % join_type)

    def stroke_opacity(self, opacity):
        self.insert('stroke-opacity %s' % opacity)

    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        self.insert('stroke-width %s' % width)
    
    def text(self, (x, y), text_string):
        # TODO: Escape special characters in text string
        self.insert('text %s,%s "%s"' % (x, y, text_string))
    
    def text_antialias(self, flag):
        # flag in [0, 1]
        self.insert('text-antialias %s' % flag)

    def text_undercolor(self, color):
        self.insert('text-undercolor %s' % color)

    def translate(self, (x, y)):
        self.insert('translate %s,%s' % (x, y))
    
    def viewbox(self, (x0, y0), (x1, y1)):
        self.insert('viewbox %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def pop(self, context):
        # context may be: clip-path, defs, gradient, graphic-context, pattern
        self.insert('pop %s' % context)
    
    def push(self, context, *args, **kwargs):
        # context may be: clip-path, defs, gradient, graphic-context, pattern
        # TODO: Accept varying arguments depending on context, e.g.
        #    push('graphic-context')
        # or push('pattern', id, radial, x, y, width,height)
        self.insert('push %s' % context)




# Demo
if __name__ == '__main__':
    img = MVG()

    # Start MVG file with graphic-context and viewbox
    img.push('graphic-context')
    img.viewbox((0, 0), (720, 480))

    # Add a background fill
    img.fill('darkblue')
    img.rectangle((0, 0), (720, 480))

    # Some decorative circles
    img.fill('blue')
    img.circle((280, 350), (380, 450))
    img.fill('orange')
    img.circle((670, 100), (450, 200))

    # White text in a range of sizes
    img.fill('white')
    for size in [5,10,15,20,25,30,35]:
        ypos = 100 + size * size / 5
        img.font('Helvetica')
        img.font_size(size)
        img.text((100, ypos), "%s pt: The quick brown fox" % size)

    # Close out the MVG file
    img.pop('graphic-context')

    # Display the MVG text, then show the generated image
    img.code()
    img.render()
