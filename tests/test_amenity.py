import unittest

from models.amenity import Amenity


class TestAmenity(unittest.TestCase):

    def test_amenity(self):
        test = Amenity("test", "test")
        self.assertEqual(test.name, "test")