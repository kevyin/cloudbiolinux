"""Install software and configure package managers.
"""
import os

from fabric.api import run, cd
from fabric.contrib import files

from cloudbio.custom.shared import _make_tmp_dir
from cloudbio.package.deb import (_apt_packages, _add_apt_gpg_keys,
                                  _setup_apt_automation, _setup_apt_sources)
from cloudbio.package.rpm import (_yum_packages, _setup_yum_bashrc,
                                  _setup_yum_sources)


def _configure_and_install_native_packages(env, pkg_install):
    """
    Setups up native package repositories, determines list
    of native packages to install, and installs them.
    """
    home_dir = run("echo $HOME")
    if home_dir:
        if env.shell_config.startswith("~"):
            nonhome = env.shell_config.split("~/", 1)[-1]
            env.shell_config = os.path.join(home_dir, nonhome)
    if env.distribution in ["debian", "ubuntu"]:
        _setup_apt_sources()
        _setup_apt_automation()
        _add_apt_gpg_keys()
        _apt_packages(pkg_install)
    elif env.distribution in ["centos", "scientificlinux"]:
        _setup_yum_sources()
        _yum_packages(pkg_install)
        if env.edition.short_name not in ["minimal"]:
            _setup_yum_bashrc()
    else:
        raise NotImplementedError("Unknown target distribution")

def _connect_native_packages(env, pkg_install):
    """Connect native installed packages to local versions.

    This helps setup a non-sudo environment to handle software
    that needs a local version in our non-root directory tree.
    """
    bin_dir = os.path.join(env.system_install, "bin")
    path = run("echo $PATH")
    if bin_dir not in path and files.exists(env.shell_config):
        comment_line = "# CloudBioLinux PATH updates"
        add_path = "export PATH=$PATH:%s" % bin_dir
        if not files.contains(env.shell_config, add_path):
            files.append(env.shell_config, comment_line)
            files.append(env.shell_config, add_path)
    if "python" in pkg_install:
        _create_local_virtualenv(env.system_install)

def _create_local_virtualenv(target_dir):
    """Create virtualenv in target directory for non-sudo installs.
    """
    url = "https://raw.github.com/pypa/virtualenv/master/virtualenv.py"
    if not os.path.exists(os.path.join(target_dir, "bin", "python")):
        with _make_tmp_dir() as work_dir:
            with cd(work_dir):
                run("wget --no-check-certificate %s" % url)
                run("python virtualenv.py %s" % target_dir)
