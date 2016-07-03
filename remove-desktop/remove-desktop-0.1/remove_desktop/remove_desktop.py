#!/usr/bin/env python

#=============================================================================
# Copyright: 2013 Andrei Chiver andreichiver@gmail.com
# License: GPL-3
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  On Debian systems, the complete text of the GNU General
#  Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
#=============================================================================


"""
Uninstall metapackages like desktop packages which have a lot of dependencies:
gnome-desktop, xubuntu-desktop, lubuntu-desktop, kubuntu-desktop, etc.

Usage:
    remove_desktop [options] <metapackage>
    remove_desktop -h | --help
    remove_desktop -v | --version

Arguments:
    <metapackage>    the name of the metapackage(Eg. gnome-desktop)

Options:
    -h --help      Show this screen.
    -v --version   Show program version.
    -t --test      Just test the script is working, don't remove anything.

Eg:
    remove_desktop kubuntu-desktop
    remove_desktop xubuntu-desktop
    remove_desktop -t openbox
"""

import logging
from logging import INFO, DEBUG
import sys
import os                        # needed to check if root runs the script
import re
import collections               # OrderedDict
import subprocess
import decimal

# Third party libraries
import docopt                    # creates the command line interface
import sh
from sh import glob   # always use sh.glob() instead of glob.glob()
# sh -> subprocess interface for Python that allows you to call any program as
# if it were a function
import colorlog                         # Colorize log text

# Own modules
import utils


__all__ = ["defaults", "Locator", "validator", "parser", "parser_stage_2",
           "worker"]


def __dir__():
    '''This method will be called by dir() and must return the list of
    attributes. This defines the interface of this module.'''

    return ["defaults", "Locator", "validator", "parser", "parser_stage_2",
            "worker"]


### SOME DEFAULT CONFIGURATION ###

defaults = {'log_level': 'DEBUG',
            'path': "/var/log/apt/history*",
            'conf_file': 'main.conf',
            'log_file': 'out.log',
            }

# 'log_level'    just 2 levels: DEBUG or INFO
# 'path'         path to pkg manager's log files
# 'conf_file'    config file user can edit
# 'log_file'     app's log file


class Locator(object):
    def __init__(self):
        super(Locator, self).__init__()
        self.paths = []
        '''paths holds paths to package managers log files.'''
        self.main_line = ""
        '''
        main_line holds the line that contains the installation
        command of the form:
        Install: lightdm-gtk-greeter:i386 (1.3.1-0ubuntu1), ...
        '''
        self.installation_lines = []
        '''
        Holds possible main_line candidates, only one of them is the
        installation command line.
        '''

    def search(self, package, path):
        '''Looks for package in files in path using zgrep shell binary.'''

        try:
            log_lines = sh.zgrep(package, glob(path))
        except sh.ErrorReturnCode_1 as e:      # buffer overflown??
            # don't know why this happens when using sh.
            log_lines = e.stdout

        log_lines = log_lines.split("\n")
        # get all but the last line -> get rid of last '' empty line
        log_lines = log_lines[:-1]

        for line in log_lines:
            #logger.debug("Following line was found:\n%s" % line)
            logger.debug("Following line containing metapackage was found "
                         "in package manager's log files:")
            print(line)
            self.installation_lines.append(line)

        if not self.installation_lines:
            logger.info("zgrep could not find in logs any info that ",
                        "can be used to uninstall the package.",
                        "Exiting...")
            sys.exit()
        else:
            logger.info("Search results from zgrep where collected.")

        self._check()
        return self.main_line

    def _check(self):
        '''Parses self.installation_lines and decides based on hints which
        one is the self.main_line. Called by .search()'''
        # checker should be an object which has different hints as properties
        # & methods => self.checker = Checker()
        # hints can be tests based on unittest.TestCase
        for line in self.installation_lines:
            match = re.search('Install: ', line)
            if match:
                logger.info("The line with the package installation command "
                            "was found.")
                self.main_line = line
                return
            else:
                continue

        logger.critical("The line with the package installation command "
                        "was not found. Exiting...")
        sys.exit()


def validator(package):
    '''looks up package name with apt-cache or aptitude and checks if package
    exists, therefore package is valid.'''
    # TODO: implement this
    # len(package) > 2
    # package.startswith(('0','1','2','3','4','5','6','7','8','9','-','_','.'))
    pass


def parser(line):
    '''Sanitizes the line and returns a string only of package names.'''

    # trim the filename by substituting it with an empty space:
    pattern = r'.*:Install: '
    line = re.sub(pattern, '', line)

    sequence = re.finditer(r"""
        # blanks are ignored inside pattern because of re.VERBOSE
        (?P<pkg_name>[a-zA-Z0-9._-]+ | [^:\s]+):     # Eg.  lightdm-gtk-greeter:
        (?P<arch>i?\d{3} | amd64) [ ]                # Eg. 'i386 ' notice one blank ' '
        \( (?P<version>.*?) \),?            # Eg.  (1.3.1-0ubuntu1), or
                                            # (1.3.1-0ubuntu1)  without
                                            # trailing comma(last in the line)
        # in first group, A | B was used, where A, B are regexs. B catches all
        # weird package names that don't contain ':' or any whitespace
        """, line, flags=re.VERBOSE)

    # preserve same order as found in apt archives/log files:
    d = collections.OrderedDict()
    for match in sequence:
        key = match.group('pkg_name')
        # TODO: validator(key)
        d[key] = match.groups()[1:]

    return d


def is_installed(package):
    '''
    Tell if a package is installed on the system or not.
    In a shell you can tell using this:
    $: dpkg-query -l | grep <package>
    If output is empty => package isn't installed
    '''
    try:
        subprocess.check_output("dpkg-query -l | grep '%s'" % package,
                                shell=True)
        # if above doesn't raise an exception => package is installed
        return True
    except subprocess.CalledProcessError:
        # usually, this exception is raised when output of cmd if None
        # so this means that package is not installed
        pass

    return False


def parser_stage_2(rdeps, packages, callback=is_installed):
    '''Find which packages can't be removed because are needed as dependencies
    for packages that you don't want to remove.

    rdeps -> a list of reverse dependencies
    packages -> a list of installed packages
    callback -> introduced to make testing easy. In real case scenario,
                callback can be a fct. that checks if a package is installed,
                when testing, it can be a fct. that tells whatever you want.

    One way to find packages that can't be removed is to use:
    $: apt-cache rdepends <package>

    'rdepends' outputs all the packages that depend on <package> which are
    either installed or uninstalled!
    And shows packages even if they depend directly or indirectly of the
    current package!
    If at least one of them is not going to be removed, then <package> is not
    going to be removed either, otherwise the dependency chain will be broken.

    Eg. find which packages depend on libabiword-2.9:
    $: apt-cache rdepends libabiword-2.9
    libabiword-2.9
    Reverse Depends:
      python-abiword
      libabiword-2.9-dev
      abiword-plugin-mathview
      abiword-plugin-grammar
      abiword

    We need to check if the packages are in the list of packages to be
    removed. If they are not, we can't remove libabiword-2.9.
    If they are, we need to check which packages depend on them.

    Eg. find which packages depend on abiword-plugin-mathview
    $: apt-cache rdepends abiword-plugin-mathview
    abiword-plugin-mathview
    Reverse Depends:
      xubuntu-desktop
      abiword
    '''

    # if no reverse dependencies => metapackage/top pkg
    if not rdeps:
        return "remove"

    for p in rdeps:
        if p in packages:
            # if p is going to be removed anyway, its dependencies will
            # be removed too.
            flag = "remove"
        elif callback(p):
            # apt-cache rdepends shows uninstalled packages too!
            # but we need only installed ones.
            flag = "keep"
            break
        else:
            flag = "remove"

    return flag


def worker(packages):
    '''Executes sudo apt-get purge package_names'''

    # Some stats:
    logger.info('A total number of %s packages will be purged.' %
                len(packages))

    #logger.debug('These are:\n %s \n\n' % ' '.join(packages))
    # bypass logger.debug above to print text white:
    logger.debug('These are:')
    print(' '.join(packages))

    logger.info('The rest will be kept because are needed as dependencies '
                'for packages that you want to keep.')

    with sh.sudo:
        """
        If you use sudo, the user executing the script must have the
        NOPASSWD option set for whatever command that user is running,
        otherwise sudo will hang.
        Solution to bypass the NOPASSWD option:
        run the script that contains the sh.sudo command with sudo and
        enter the password.
        """

        try:
            if not arguments['--test']:
                logger.info("Purging...")
                sh.apt_get("--assume-yes", "--ignore-missing", "purge",
                           packages,
                           _out=outputter)    # _out=sys.stdout
            # sh.apt_get(list_of_package_names_not_string)
            # if package names have changed since they were installed, apt-get
            # will raise error: 'Can't locate package ...' so we use
            # --ignore-missing.
            # _out=sys.stdout to let the original output of underlying cmd
            # to be visible
            # OR
            # _out=utils.Tee(file_handler.stream) to write to console and to file.
            else:
                logger.info("Testing purging...")
                sh.apt_get("--simulate", "--ignore-missing", "purge",
                           packages,  _err_to_out=True,
                           _out=outputter)   # utils.Tee(file_handler.stream))
        except sh.ErrorReturnCode as e:
            logger.critical(e)


def set_up_logging(default_level, log_file):
    logger = logging.getLogger('Main')
    # Set default log level; DEBUG -> most detailed level
    logger.setLevel(default_level)

    ### SET UP A CONSOLE HANDLER ###
    # Handlers send the log records (created by loggers) to the appropriate
    # destination: a console, a file, over the internet, by email, etc.

    # This line enables pretty printing of log messages:
    logging.StreamHandler.emit = utils.emit
    # all classes that inherit StreamHandler, eg. FileHandler, etc. will use it

    console_handler = logging.StreamHandler()       # stream -> sys.stdout

    # Formatters specify the layout of log records in the final output.
    # Set formatter for Stream Handler to colorize text for the command line.
    #message_format = '%(asctime)s %(funcName)s: %(levelname)s - %(message)s'
    message_format = "%(yellow)s %(asctime)s %(purple)s %(funcName)s: " +\
                     "%(log_color)s %(levelname)s %(reset)s %(blue)s " +\
                     "%(message)s"
    # the syntax of message_format accepts colors, unlike python's std format.
    formatter = colorlog.ColoredFormatter(message_format,
                                          datefmt=None,
                                          reset=True,
                                          )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    ###  SET UP A HANDLER THAT LOGS TO FILE ###
    file_handler = logging.FileHandler(filename=log_file, mode='w')

    # Log level can be set per handler too:
    #file_handler.setLevel(logging.DEBUG)

    # Set formatter for File Handler
    message_format = '%(asctime)s %(funcName)s: %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt=message_format)

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


## MAIN ##
# if this module is imported, all code executes until here:
if __name__ == '__main__':

    ### GET SCRIPT ARGUMENTS ###
    ############################

    # Create a beautiful CLI interface from the help string, in this case, __doc__
    # and read the script arguments
    arguments = docopt.docopt(__doc__, help=True, version="Remove Desktop 0.1")
    # script is stopped here by docopt if called with wrong arguments

    # for all use cases other than --help, --version, run as root:
    if os.geteuid() != 0:
        print("sorry, you need to run this as root user.")
        sys.exit(1)

    logger = set_up_logging(defaults['log_level'], defaults['log_file'])

    # Create a file like obj. that writes both to sys.stdout(as 'print' does) and
    # to log file:
    file_handler = logger.handlers[1]
    outputter = utils.Tee(file_handler.stream)
    # from now on, every time 'print' is used, outputter is used.

    # read user config from file, thus updating default config:
    if os.path.exists(defaults['conf_file']):
        conf = utils.read_config(logger, defaults['conf_file'], defaults)
    else:
        print('no config file found')
        conf = defaults      # shallow copy!

    logger.setLevel(conf['log_level'])

    metapackage = arguments['<metapackage>']
    logger.debug('metapackage argument: %s' % metapackage)

    ### look up package with `apt-cache search` and if it doesn't find it, say
    ### package name is invalid, but try to show suggestions; create a validate fct.
    loc = Locator()
    results = loc.search(metapackage, conf['path'])
    d = parser(results)

    # Some stats:
    logger.info('A total number of %s packages were installed.' % len(d.keys()))
    #logger.debug('These are:\n' + ' '.join(d.keys()))
    logger.debug('These are:')
    print(' '.join(d.keys()))

    logger.info("Computing what packages to remove and what to keep in order "
                "not to break packages that need them as dependencies:")
    packages = d.keys()

    # TODO: validator(packages) -> show which ones are wrong.

    # storage for packages that will be removed:
    obsolete = []

    ### Print a progress bar, as computing what packages to remove takes time
    #########################################################################
    # this progress bar is for smaller identical tasks of known quantity
    # Ref:
    # http://thelivingpearl.com/2012/12/31/creating-progress-bars-with-python/

    # Progress bar will have a resolution of 5% = 5/100 = 1/20
    # resolution will be: res = len(packages) / 20
    res = decimal.Decimal(len(packages)) / 20
    # If we have 95 packages, for 5%, res will be 4.75
    # Theoretically, for every 4.75 packages handled by task, progress
    # bar increases. In practice, progress bar increases every
    # int(4.75 * i) where i in range(1,21)
    marks = (int(res * i) for i in range(1, 21))
    i = marks.next()

    # if it fills for every 20% completion time, uncomment below:
    print 'Computing [                    ]',
    print '\b' * 22,
    sys.stdout.flush()

    # if it fills for every 10% completion time, uncomment below:
    #print 'Starting [          ]',
    #print '\b' * 12,

    # adjust according to n; if n=10 => '\b' * 12
    # , (comma) suppresses carriage return(Enter) for python <= 2.7.5
    # The special character \b returns the printing cursor one
    # step backwards

    for index, package in enumerate(packages):
        err_counter = 0
        try:
            rdeps = sh.apt_cache.rdepends(package)
        except sh.ErrorReturnCode_100 as e:
            # catch 'No packages found' error
            # this occurs if repositories have changed, old pkg was removed
            # or parser() didn't get the correct name -> regex's <pkg_name>
            # group character range is incomplete -> it doesn't contain
            # the character in the package name.
            # In this case, no neighbouring package names are wrong.
            # Well, when we're talking about tens or hundreds of pkgs, just
            # a couple of them can be ignored.
            err_counter += 1
            continue
        finally:
            if err_counter > 2:
                logger.error("Too many package naming errors, exiting...")
                sys.exit()

        '''
        >>> rdeps.stdout.split("\n")
        ['abiword-plugin-mathview',
        'Reverse Depends:',
        '  xubuntu-desktop',
        '  abiword',
        '']
        '''
        # get all lines but the first 2:
        rdeps = rdeps.stdout.split("\n")[2:-1]
        rdeps = [pkg.lstrip() for pkg in rdeps]
        '''
        >>> rdeps
        ['xubuntu-desktop', 'abiword']
        '''
        # this is the smaller, identical task for all packages:
        flag = parser_stage_2(rdeps, packages)

        if flag == "remove":
            obsolete.append(package)

        # Increase progress bar with 1 unit
        if index + 1 == i:
            print '\b.',
            sys.stdout.flush()
            try:
                i = marks.next()
            except StopIteration:
                pass

    print '\b] Done!'
    print

    if obsolete:
        worker(obsolete)

    logger.info("Program terminated")
