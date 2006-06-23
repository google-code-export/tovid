#! /usr/bin/env python
# flipbook.py

import os
import sys
from libtovid.mvg import Drawing
from libtovid import layer
from libtovid import effect
from libtovid.VideoUtils import images_to_video

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    It has several frames (or "pages")
    """
    def __init__(self, frames=30, (width, height)=(720, 576)):
        self.frames = frames
        self.size = width, height
        self.layers = []
        self.drawings = []

    def add(self, layer):
        """Add a Layer to the flipbook."""
        self.layers.append(layer)

    def render(self, frame=1):
        """Render a Drawing for the given frame."""
        print "Rendering Flipbook frame %s" % frame
        # Render the drawing
        drawing = self.drawing(frame)
        drawing.render()

    def drawing(self, frame):
        """Get a Drawing of the given frame"""
        drawing = Drawing(self.size)
        # Write MVG header stuff
        drawing.push('graphic-context')
        drawing.viewbox((0, 0), self.size)
        # Draw each layer
        for layer in self.layers:
            layer.draw_on(drawing, frame)
        drawing.pop('graphic-context')
        return drawing

    def render_video(self, m2v_file):
        """Render the flipbook to an .m2v video stream file."""
        # TODO: Get rid of temp-dir hard-coding
        tmp = '/tmp/flipbook'
        try:
            os.mkdir(tmp)
        except:
            print "Temp dir %s already exists, overwriting."
        # Write each Flipbook frame as an .mvg file, then convert to .jpg
        frame = 1
        while frame < self.frames:
            drawing = self.drawing(frame)
            print "Drawing for frame: %s" % frame
            print drawing.code()
            drawing.save('%s/flip_%04d.mvg' % (tmp, frame))
            # jpeg2yuv likes frames to start at 0
            drawing.save_image('%s/%08d.jpg' % (tmp, frame - 1))
            frame += 1
        images_to_video(tmp, m2v_file, 'dvd', 'pal')

# Demo
if __name__ == '__main__':
    print "Flipbook demo"
    if len(sys.argv) < 4:
        print "Usage: flipbook.py IMAGE1 IMAGE2 VIDEO1"
        sys.exit(1)
    else:
        bgimage = os.path.abspath(sys.argv[1])
        fgimage = os.path.abspath(sys.argv[2])
        video = os.path.abspath(sys.argv[3])

    flip = Flipbook()

    # Background image
    bgd = layer.Background(flip.size, filename=bgimage)
    flip.add(bgd)

    # Text layer with fading and movement effects
    text = layer.Text("The quick brown fox", (0, 0), fontsize='40')
    text.effects.append(effect.Spectrum(1, 30))
    text.effects.append(effect.Fade(1, 30, 10))
    text.effects.append(effect.Movement(1, 30, (100, 100), (300, 300)))
    flip.add(text)

    pic = layer.Background((320, 240), 'black', fgimage)
    pic.effects.append(effect.Scale(0, 30, (0.0, 0.0), (1.0, 1.0)))
    flip.add(pic)

    clip = layer.VideoClip(video, (260, 200), (320, 240))
    clip.rip_frames(0, 30)
    flip.add(clip)

    # Render the final video
    flip.render_video('/tmp/flipbook.m2v')
    print "Output in /tmp/flipbook.m2v (we hope!)"

