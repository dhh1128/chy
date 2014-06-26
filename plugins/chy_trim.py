
def clean(txt):
    lines = txt.split('\n')
    lines = [l.rstrip() for l in lines]
    txt = '\n'.join(lines)
    txt = txt.strip() + '\n'
    return txt
