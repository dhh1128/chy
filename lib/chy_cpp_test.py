#! /usr/bin/python

import unittest

from chy_cpp import _parse_state, _double_quote_region, _hash_block_pat
from chy_cpp import _code_region, _find_end_of_condition
from chy_cpp import *

sample_c_code = '''
#ifndef foo_h // comment with "quoted" string
#define foo_h

const char * txt = "abc\\"\\n/*xyz*/ is //";
 # if 0
int x = 0;
void do_something() {
    // insert body here
};
#else
template <class T>
class foo /* not abc */ {
public: //expose everything with this
    foo();
};
    #endif

#endif
'''

class chy_cpp_test(unittest.TestCase):
    
    def expect_state(self, state, idx, region_count, new_func, line_num):
        msg = None
        if idx != state.i:
            msg = 'Expected to be at index %s, not %s.' % (idx, state.i)
        elif region_count != len(state.regions):
            msg = 'Expected %s regions, not %s.' % (region_count, len(state.regions))
        elif new_func != state.func:
            msg = 'Expected to be in %s, not %s.' % (new_func.func_name, state.func)
        elif line_num != state.line_num:
            msg = 'Expected to be on line %s, not %s.' % (line_num, state.line_num)
        if msg:
            self.fail(msg)

    def test_double_quote_region(self):
        state = _parse_state('"hello, world"')
        _double_quote_region(state)
        self.expect_state(state, len(state.txt), 1, None, 1)
    
        state = _parse_state('"hi" is what she said')
        _double_quote_region(state)
        self.expect_state(state, 4, 1, _code_region, 1)
        
    def test_code_region(self):
        state = _parse_state('x = 1\ny=z;')
        _code_region(state)
        self.expect_state(state, len(state.txt), 1, None, 2)
    
        state = _parse_state('"hi" is what she said')
        _double_quote_region(state)
        self.expect_state(state, 4, 1, _code_region, 1)
        
    def test_find_end_of_condition(self):
        txt = '#if GCC_VERSION > 4.2\ndo something'
        m = _hash_block_pat.search(txt)
        self.assertEquals(22, _find_end_of_condition(txt, m))
    
        txt = '#ifdef foo // comment\n#include x'
        m = _hash_block_pat.search(txt)
        self.assertEquals(11, _find_end_of_condition(txt, m))
    
        txt = '#ifdef foo/* comment\n#include x*/'
        m = _hash_block_pat.search(txt)
        self.assertEquals(10, _find_end_of_condition(txt, m))

    def test_find_code_regions(self):
        regions = find_code_regions(sample_c_code)
        #for r in regions:
        #    print r
        region_types = [r.region_type for r in regions]
        expected = 'code,#ifndef,//,code,",code,#if,code,//,code,#else,code,/*,code,//,code,#endif,code,#endif'
        self.assertEquals(expected, ','.join(region_types))
        
    def test_mask(self):
        n = sample_c_code.count('\n')
        m = mask(sample_c_code).count('\n')
        self.assertEquals(n, m)
        

if __name__ == '__main__':
    unittest.main()