import unittest

import utils

class TestUtils(unittest.TestCase):

    def test_clip_int_input(self):
        self.assertRaises(TypeError, utils.clip_int, 4.2, 0, 10)

    def test_clip_int_bounds(self):
        self.assertRaises(ValueError, utils.clip_int, 0, -1, -10)

    def test_clip_int_bounds_equal(self):
        self.assertEqual(
            utils.clip_int(10, 0, 0),
            0
        )

    def test_clip_int_below(self):
        self.assertEqual(
            utils.clip_int(-20, -10, 10),
            -10
        )

    def test_clip_int_lower_bound(self):
        self.assertEqual(
            utils.clip_int(-10, -10, 10),
            -10
        )

    def test_clip_int_within(self):
        self.assertEqual(
            utils.clip_int(-10, 0, 10),
            0
        )

    def test_clip_int_upper_bound(self):
        self.assertEqual(
            utils.clip_int(10, -10, 10),
            10
        )

    def test_clip_int_above(self):
        self.assertEqual(
            utils.clip_int(15, -10, 10),
            10
        )

    def test_float_to_pix(self):
        self.assertEqual(
            utils.float_to_pix(0.3),
            1
        )
        self.assertEqual(
            utils.float_to_pix(-0.3),
            -1
        )
        self.assertEqual(
            utils.float_to_pix(4.7),
            int(4.7)
        )
