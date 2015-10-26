from unittest2 import TestCase
from wtf.utils import get_in, which, flatten_key_name

__author__ = 'avishai'


class UtilsTest(TestCase):
    def test_which(self):
        self.assertEqual(which('no such program'), None)
        self.assertTrue(which('python').endswith('python'))

    def test_get_in(self):
        self.assertEqual(get_in({'a': {'b': 'val'}}, ['a', 'b']), 'val')
        self.assertEqual(get_in({'a': 'val'}, ['a']), 'val')
        self.assertEqual(get_in({'a': 'val'}, 'a'), 'val')
        self.assertEqual(get_in({'a': 'a'}, ('a',)), 'a')
        self.assertEqual(get_in({'a': ['val1', 'val2']}, ['a', 1]), 'val2')
        self.assertRaises(KeyError, get_in, {'a': None}, ['A', 'B'])
        self.assertRaises(TypeError, get_in, {'a': None}, ['a', 'b'])

    def test_flatten_key_name(self):
        self.assertEqual(flatten_key_name(('a', 'b')), 'a.b')
        self.assertEqual(flatten_key_name('a'), 'a')
