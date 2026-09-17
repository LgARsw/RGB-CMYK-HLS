import unittest
import model.spaces as space_math

class TestColorMathVariant2(unittest.TestCase):
    def test_rgb_to_hls_pure_white(self):
        h, l, s = space_math.rgb_to_hls(255, 255, 255)
        self.assertAlmostEqual(l, 100.0)
        self.assertAlmostEqual(s, 0.0)

    def test_rgb_to_hls_pure_red(self):
        h, l, s = space_math.rgb_to_hls(255, 0, 0)
        self.assertAlmostEqual(h, 0.0)
        self.assertAlmostEqual(l, 50.0)
        self.assertAlmostEqual(s, 100.0)

    def test_hls_to_rgb_back(self):
        r, g, b, _ = space_math.hls_to_rgb(120.0, 50.0, 100.0)
        self.assertEqual(r, 0)
        self.assertEqual(g, 255)
        self.assertEqual(b, 0)

if __name__ == '__main__':
    unittest.main()
