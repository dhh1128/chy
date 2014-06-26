import re

supported_filetypes_pat = re.compile(r'\.h(h|pp|xx)?$', re.IGNORECASE)
first_token_pat = re.compile(r'\s*', re.MULTILINE)
hash_pat = re.compile(r'^\s*#\s*[a-z]+)', re.MULTILINE)
ifndef_pat = re.compile(r'^\s*#\s*ifndef\s+([_a-zA-Z0-9]+)', re.MULTILINE)

def supports_path(path):
    return bool(supported_filetypes_pat.search(path))

def clean(txt):
    # We support a sentry that is the first token in the header, or one that is
    # preceded by at most one logical comment. A "logical comment" is any block

    m = hash_pat.search(txt)
    if m:
        if m.start() > 0:
            i