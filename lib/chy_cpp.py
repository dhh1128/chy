'''
Routines to make it easier to process C and C++.
'''

import re, collections

_hash_block_pat = re.compile('[ \t]*(#[ \t]*(if(n?def)?|endif|else))(?![a-zA-Z0-9_])')

MASK_CPP_COMMENTS = 1
MASK_C_COMMENTS = 2
MASK_LITERALS = 3
MASK_IF_0 = 4

'''

'''
region = collections.namedtuple('region', ['begin', 'end', 'line_num', 'region_type', 'hash_start_line_num'])

class _parse_state:
    def __init__(self, txt):
        self.txt = txt
        self.i = 0
        self.end = len(txt)
        self.regions = []
        self.func = _code_region
        self.line_num = 1
    def log(self):
        name = 'None'
        if self.func:
            name = self.func.func_name
        print('In %s at index %s (line %s, %s...)' % (name, self.i, self.line_num, repr(self.txt[self.i:self.i+3])))

def _save_region(state, end, region_type, hash_line_num=None):
    state.regions.append(region(state.i, end, state.line_num, region_type, hash_line_num))
    state.i = end

def _double_quote_region(state):
    state.log()
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
        state.func = _code_region
    _save_region(state, i, '"')
    
def _save_code_region_if_not_empty(state, end):
    if end > state.i:
        _save_region(state, end, 'code')
    else:
        print('Empty code region at index %s (line %s, %s...)' % (state.i, state.line_num, repr(state.txt[state.i:state.i+3])))
    
def _code_region(state):
    state.log()
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
                i += m.start()
                print('m.start(1) = %d, state.i = %d' % (m.start(1), state.i))
                _save_code_region_if_not_empty(state, i)
                i = _find_end_of_condition(state.txt, m, i)
                _save_region(state, i, '#%s' % m.group(2), state.line_num)
                if i >= state.end:
                    state.func = None
                    break

        c = state.txt[i]
        if c == '"':
            _save_code_region_if_not_empty(state, i)
            state.func = _double_quote_region
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
                _save_code_region_if_not_empty(state, i)
                i = state.txt.find('\n', i + 2)
                if i == -1:
                    i = state.end
                else:
                    i += 1
                _save_region(state, i, '//')
                state.line_num += 1
            elif second == '*':
                _save_code_region_if_not_empty(state, i)
                x = state.i
                i = state.txt.find('*/', i + 2)
                if i == -1:
                    i = state.end
                else:
                    i += 2
                _save_region(state, i, '/*')
                state.line_num += state.txt[x:i].count('\n')
            else:
                i += 1
        elif c == '\n':
            i += 1
            state.line_num += 1
            previous_was_line_break = True
        else:
            i += 1
        if i >= state.end:
            _save_code_region_if_not_empty(state, i)
            state.func = None
            state.log()
            break
    state.i = i

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
        # Consume line break to avoid clutter
        return i + 1
    else:
        j = txt.find('//', end)
        k = txt.find('/*', end)
        if k > -1 and (k < j or j == -1):
            j = k
        if j != -1:
            return j
    return len(txt)

def find_code_regions(txt):
    '''
    Break C/C++ code into logical regions based on a simple scan. This allows
    processors to correctly parse string literals, comments, and #ifdefs without
    becoming confused and without re-inventing the wheel.
    
    A region 
    
    @return a list of region tuples (begin, end, line_num, region_type, hash_start_line_num).
    '''
    state = _parse_state(txt)
    while state.func and (state.i < state.end):
        state.func(state)
    return state.regions

def mask(txt, mask_bitmask):
    '''
    Remove comments without altering line numbers (multiline comments
    are replaced by the same number of line breaks). Replace string
    literals with
    '''
    pass

if __name__ == '__main__':
    import os, sys
    if len(sys.argv) == 2 and not re.match('-?-h(elp)?', sys.argv[1]):
        with open(sys.argv[1], 'r') as f:
            txt = f.read()
        regions = find_code_regions(txt)
        i = 0
        for r in regions:
            print('%s: %s' % (i, r))
            i += 1
    else:
        print('python %s FNAME -- print code regions in FNAME.' % os.path.split(__file__)[1])

