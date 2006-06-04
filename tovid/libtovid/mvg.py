#! /usr/bin/env python
# mvg.py

"""Provides a Python interface for reading/writing Magick Vector Graphics (MVG).

MVG references:
http://www.imagemagick.org/script/magick-vector-graphics.php
http://studio.imagemagick.org/pipermail/magick-developers/2002-February/000156.html
"""
import sys
import commands


class MVG:
    """A Magick Vector Graphics (MVG) image file with load/save, insert/append,
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
    def __init__(self):
        self.clear()

    def load(self, filename):
        """Load MVG from the given file."""
        self.clear()
        infile = open(filename, 'r')
        for line in infile.readlines():
            self.append(line)
        infile.close()

    def save(self, filename):
        """Save to the given MVG file."""
        outfile = open(filename, 'w')
        for line in self.data:
            outfile.write("%s\n", line)
        outfile.close()

    def display(self):
        """Print out complete MVG text."""
        for line in self.data:
            print "%s" % line

    def render(self, width, height):
        """Render the MVG image with ImageMagick at the given size, and
        display it."""
        # TODO
        cmd = "convert -size %sx%s " % (width, height)
        cmd += " xc:black "
        cmd += " -draw '%s' " % ' '.join(self.data)
        cmd += " -composite miff:- | display"
        print "Running command:"
        print cmd
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
        self.goto(len(self.data) + 1)

    def clear(self):
        """Clear the current contents and position the cursor at line 1."""
        self.data = [''] # Line 0 is null
        self.cursor = 1

    def append(self, mvg_string):
        """Append the given MVG string as the last line, and position the
        cursor after the last line."""
        self.data.append(mvg_string)
        self.goto_end()

    def insert(self, mvg_string):
        """Insert the given MVG string before the current line, and position
        the cursor after the inserted line."""
        self.data.insert(self.cursor, mvg_string)
        self.cursor += 1

    """
    Draw commands
    """

    def circle(self, (x_center, y_center), (x_perimeter, y_perimeter)):
        self.insert('circle %s,%s %s,%s' % \
                    (x_center, y_center, x_perimeter, y_perimeter))

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
        self.insert('image %s,%s %s,%s "%s"' % \
                    (compose, x, y, width, height, filename))
    
    def line(self, (x0, y0), (x1, y1)):
        """Draw a line from (x0, y0) to (x1, y1)."""
        self.insert('line %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def matte(self, (x, y), method):
        # method may be: point, replace, floodfill, filltoborder, reset
        # (What do x, y mean?)
        self.insert('matte %s,%s %s' % (x, y, method))
    
    def rectangle(self, (x0, y0), (x1, y1)):
        """Draw a rectangle from (x0, y0) to (x1, y1)."""
        self.insert('rectangle %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        self.insert('stroke-width %s' % width)
    
    def text(self, (x, y), text_string):
        # TODO: Escape special characters in text string
        self.insert('text %s,%s "%s"' % (x, y, text_string))
    
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
    img.display()
    img.render(720, 480)
