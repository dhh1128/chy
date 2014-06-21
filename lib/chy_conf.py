import ConfigParser

class conf:

    def __init__(self, path, parent=None):
        self.path = path
        self.parent = parent
        self.cfg = ConfigParser.ConfigParser()
        with open(self.path, 'r') as f:
            self.cfg.readfp(f)

    def get(self, section, key, default_value):
        if self.cfg.has_section(section):
            if self.cfg.has_option(section, key):
                return self.cfg.get(section, key)
        if self.parent:
            return self.parent.get(section, key, default_value)
        return default_value