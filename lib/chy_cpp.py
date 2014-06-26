'''
Routines to make it easier to process C and C++.
'''

import re, collections

_hash_block_pat = re.compile('[ \t]*(#[ \t]*(if(n?def)?|endif|else))(?![a-zA-Z0-9_])')

MASK_CPP_COMMENTS = 1
MASK_C_COMMENTS = 2
MASK_LITERALS = 3
MASK_IF_0 = 4

region = collections.namedtuple('region', ['begin', 'end', 'line_num', 'region_type', 'hash_start_line_num'])

class _region_parse_state:
    def __init__(self, txt):
        self.txt = txt
        self.i = 0
        self.end = len(txt)
        self.regions = []
        self.func = _default_state
        self.line_num = 1

def _double_quote(state):
    i = state.i + 1
    while i < state.end:
        c = state.txt[i]
        if c == '\\':
            i += 2
        elif c == '"':
            i += 1
            break
        elif c == '\n':
            break
        else:
            i += 1
    if i >= state.end:
        state.func = None
    else:
        state.func = _default_state
    state.regions.append(region(state.i, i, state.line_num, '"', None))
    state.i = i

def expect_state(state, idx, region_count, new_func, line_num):
    expect_eq(idx, state.i)
    expect_eq(region_count, len(state.regions))
    expect_eq(new_func, state.func)
    expect_eq(line_num, state.line_num)

def test_double_quote():
    state = _region_parse_state('"hello, world"')
    _double_quote(state)
    expect_state(state, len(state.txt), 1, _default_state, 1)

    state = _region_parse_state('"hi" is what she said')
    _double_quote(state)
    expect_state(state, 4, 1, _default_state, 1)

def _default_state(state):
    # Use a temporary idx until we know we have to hand control to another func.
    i = state.i

    # When we begin scanning, behave the same way we do right after we find '\n'...
    previous_was_line_break = (i == 0)

    while True:

        # Any time we start a new line in the default state, look for preprocessor
        # directives that would cause us to recognize "section" boundaries...
        if previous_was_line_break:
            previous_was_line_break = False
            next_chunk = state.txt[i:i+80]
            m = _hash_block_pat.match(next_chunk)
            if m:
                i = _find_end_of_condition(state.txt, m, i)
                state.regions.append(region(m.start(1), i, state.line_num, '#%s' % m.group(2), state.line_num))

        c = state.txt[i]
        if c == '"':
            state.func = _double_quote
            break
        elif c == "'":
            i += 2
            first = txt[i]
            if first == '\\':
                i += 1
            assert txt[i - 1] == "'"
        elif c == '/':
            second = state.txt[i + 1]
            if second == '/':
                state.i = i
                i = state.txt.find('\n', i + 2)
                if i == -1:
                    i = state.end
                state.regions.append(region(state.i, i, state.line_num, '//', None))
            elif second == '*':
                state.i = i
                i = state.txt.find('*/', i + 2)
                if i == -1:
                    i = state.end
                else:
                    i += 2
                state.regions.append(region(state.i, i, state.line_num, '/*', None))
                state.line_num += state.txt[state.i + 2:i - 2].count('\n')
            else:
                i += 1
        elif c == '\n':
            i += 1
            state.line_num += 1
            previous_was_line_break = True
        else:
            i += 1
        if i >= state.end:
            state.func = None
            break
    state.i = i

def test_default_state():
    state = _region_parse_state('x = 1\ny=z;')
    _default_state(state)
    expect_state(state, len(state.txt), 0, _default_state, 2)

    state = _region_parse_state('"hi" is what she said')
    _double_quote(state)
    expect_state(state, 4, 1, _default_state, 1)

def _find_end_of_condition(txt, m, offset = 0):
    end = m.end() + offset
    i = txt.find('\n', end)
    if i > -1:
        rest = txt[end:i]
        j = rest.find('//')
        k = rest.find('/*')
        if k > -1 and (k < j or j == -1):
            j = k
        if j != -1:
            return m.end() + j
        return i
    else:
        j = txt.find('//', end)
        k = txt.find('/*', end)
        if k > -1 and (k < j or j == -1):
            j = k
        if j != -1:
            return j
    return len(txt)

def test_find_end_of_condition():
    txt = '#if GCC_VERSION > 4.2\ndo something'
    m = _hash_block_pat.search(txt)
    expect_eq(21, _find_end_of_condition(txt, m))

    txt = '#ifdef foo // comment\n#include x'
    m = _hash_block_pat.search(txt)
    expect_eq(11, _find_end_of_condition(txt, m))

    txt = '#ifdef foo/* comment\n#include x*/'
    m = _hash_block_pat.search(txt)
    expect_eq(10, _find_end_of_condition(txt, m))

def find_code_regions(txt):
    '''
    Break C/C++ code into logical regions based on a simple scan. This allows
    processors to correctly parse string literals, comments, and #ifdefs without
    becoming confused and without re-inventing the wheel.
    '''
    state = _region_parse_state(txt)
    while state.func and (state.i < state.end):
        state.func(state)
    return state.regions

def test_find_code_regions():
    sample_c_code = '''
#ifndef foo_h // comment with "quoted" string
#define foo_h

const char * txt = "abc\\"\\n/*xyz*/ is //";
#if 0
int x = 0;
void do_something() {
    // insert body here
};
#else
template <class T>
class foo /* not bar */ {
public: //expose everthing
    foo();
};
#endif

#endif
'''
    x = find_code_regions(sample_c_code)
    print(x)

def mask(txt, mask_bitmask):
    '''
    Remove comments without altering line numbers (multiline comments
    are replaced by the same number of line breaks). Replace string
    literals with
    '''
    pass

def expect_eq(expected, actual):
    if expected != actual:
        raise AssertionError('%s != %s' % (expected, actual))

if __name__ == '__main__':
    test_find_code_regions()
    test_funcs = [x for x in globals().keys() if x.startswith('test_')]
    for func in test_funcs:
        print(func)
        func = globals()[func]
        func()

