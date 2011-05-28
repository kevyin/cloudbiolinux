= Hacking BioLinux tips and tricks

The BioLinux tools allow building a full environment for Bioinformatics. The
design allows for flexible targets (Editions) and specializations (Flavors).

== Start with the Minimal edition

The Minimal edition is the smallest common denominator of all Editions, as it
installs the minimum of packages to bootstrap a full install. Minimal is invoked by

          fab -f $source/fabfile.py -H target_hostname -c $source/contrib/minimal/fabricrc_debian.txt install_bare:packagelist=$source/contrib/minimal/main.yaml

The main.yaml file ascertains the major editors are included, as well remote
access, version control, and the basic build system (gcc and friends). Note the
Minimal edition overwrites the (apt) sources file to make sure there are no
conflicts with user settings.

== Adding install packages

To expand on the package list you can define your own main.yaml, and pass that
in. In your main.yaml file add the meta-packages listed in
config/packages.yaml. Invoke your new package list with

          fab -f $source/fabfile.py -H target_hostname -c $source/contrib/minimal/fabricrc_debian.txt install_bare:packagelist=myproject/main.yaml

It is that simple!

If packages.yaml is not complete, you may suggest changing its contents in the
main repository. The alternative is to create your own flavor, which we will do
in a minute. The same strategy holds for the other definitions in the ./config
directory, such as for Ruby gems, Python eggs, Perl CPAN, R-CRAN etc.

== Define a Flavor

For a cross language Bio* project performance test I needed to create a special
version of BioLinux that would pull in a list of scripts and some additional
packages.  Starting from an existing edition (in this case the Minimum edition,
but it also works on top of BioNode and BioLinux editions), I created a new
flavor in ./contrib/flavor/pjotrp/biotest/biotestflavor.py, named BioTestFlavor
(note you also need an empty __init__.py file).  The flavor comes with a new
fabricrc.txt file, and a new main.yaml file.  So kicking it into submission
would look like:

          fab -f $source/fabfile.py -H target_hostname -c $source/contrib/flavor/pjotrp/biotest/fabricrc_debian.txt install_bare:packagelist=$source/contrib/flavor/pjotrp/biotest/main.yaml

The flavor module sets env.flavor (this can only happen once). For examples
see the files in ./contrib/flavor

== Flavor: add sources

BioLinux creates a (default, or edition based) list of package sources. These
sources can be overridden by the Flavor.rewrite_apt_sources_list method - which
should return a new list.

== Flavor: add packages

The primary way of adding new packages is by creating a new main.yaml file, as
discussed above in ''Define a flavor''. In addition a flavor can define a
method: BioLinux creates a (default, or edition based) list of packages. These
sources can be overridden by the Flavor.rewrite_packages_list method - which
should return a new list. In your Flavor add a function:

    def rewrite_packages_list(self, list):
        list.append('testpackage')
        return list

== Flavor: filter packages

To filter/remove packages from the default list, use rewrite_packages_list, add
the following to your Flavor to remove testpackage from the install list:

    def rewrite_packages_list(self, list):
        list.remove('testpackage')
        return list

== Flavor: install special software

BioLinux comes with a bag of tricks to install special software outside the
main package system. There are methods for checking out source repositories,
and building software. There are methods for accessing public data resources
(such as Amazon S3). These are so called custom installs which are defined in
custom.yaml. Each of these can be pulled in and are configured by code in the
./cloudbio/custom/ directory. These mechanisms are shared between BioLinux
editions.

But, importantly, it is easy to role your own using a Flavor!

For example, you can tell your flavor to clone a git repository, and execute
a script by 

= Tips and tricks

== Tip for checking BioLinux installation effects

To see the what a BioLinux install does to your system, store the settings of
the original (untouched) state of a VM:

1. Make a dump of the current installed package list
2. Store the /etc tree - one way is to use git in /etc

After running BioLinux you can see what has been done to your system by diffing
against the package list, and checking /etc.