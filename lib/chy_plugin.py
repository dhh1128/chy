import os, collections, sys, traceback

plugin_item = collections.namedtuple('plugin_item', ['module_name', 'folder', 'module'])
all = {}

def load(folder):
    load_count = 0
    if os.path.isdir(folder):
        folder = os.path.abspath(folder)
        sys.path.insert(0, folder)
        try:
            global all
            for item in os.listdir(folder):
                if item.startswith('chy') and item.endswith('.py'):
                    module_name = item[:-3]
                    if all.has_key(module_name):
                        sys.stderr.write(
                            "Can't load %s from %s; already loaded that module from %s.\n" % (
                                module_name, all[module_name].folder))
                    else:
                        import_statement = 'import %s' % module_name
                        try:
                            eval(import_statement)
                            all[module_name] = plugin_item(module_name, folder, locals(module_name))
                        except:
                            sys.stderr.write(
                                "Can't load %s from %s.\n" % module_name, folder)
                            sys.stderr.write(traceback.format_exc() + '\n')
        finally:
            sys.path.remove(0)
