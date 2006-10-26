import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.cairo_ import Drawing
import effect
from libtovid.animation import Keyframe

class TestEffect(unittest.TestCase):
    """Test the Effect class"""

    
    def test_effect(self):
        pass
    

    def test_instantiate_effects(self):
        e1 = effect.Effect(0, 10)
        e2 = effect.Movement(0, 10, (10, 10), (20, 20))
        e3 = effect.Translate(0, 10, (-10, -10))
        e4 = effect.Fade(0, 10, 2)
        k = [Keyframe(0, 0.0),
             Keyframe(10, 1.0),
             Keyframe(30, 0.0)]
        e5 = effect.Fade(0, 30,
                         keyframes=k,
                         method='cosine')
                             

if __name__ == '__main__':
    unittest.main()

