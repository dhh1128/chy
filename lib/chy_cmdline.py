import argparse, sys

def process():
    p = argparse.ArgumentParser(description='Enforce good code hygiene.')
    p.add_argument('action', nargs=1, help='operation to perform--"clean" or "test"')
    p.add_argument('path', nargs='*', help='files or folders to process')
    args = p.parse_args()
    return args
