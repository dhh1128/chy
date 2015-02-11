#! /usr/bin/python

import unittest

from chy_cpp import *

class chy_cpp_test(unittest.TestCase):
    def test_double_quote():
        state = _region_parse_state('"hello, world"')
        _double_quote(state)
        expect_state(state, len(state.txt), 1, _default_state, 1)
    
        state = _region_parse_state('"hi" is what she said')
        _double_quote(state)
        expect_state(state, 4, 1, _default_state, 1)

if __name__ == '__main__':
    unittest.main()