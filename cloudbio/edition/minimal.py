from fabric.api import *

from cloudbio.edition import Edition

class Minimal(Edition):
    """Minimal specialization of BioLinux
    """
    def __init__(self, env):
        # Edition.__init__(self,env) Probably not a good idea to call super from Minimal
        self.name = "Minimal Edition"
        self.short_name = "minimal"
        self.version = env.version
        self.env = env
        self.include_oracle_virtualbox = False
        self.include_freenx = False
        self.include_apt_automation = False

    def check_packages_source(self):
        # Removes sources, just to be sure
        self.env.logger.debug("Clearing %s" % self.env.sources_file)
        sudo("cat /dev/null > %s" % self.env.sources_file)

