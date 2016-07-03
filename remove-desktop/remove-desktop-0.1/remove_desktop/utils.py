### Library file ###


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


import logging
import sys
import ConfigParser
import unittest
from StringIO import StringIO
import glob


class Tee(object):
    '''Emulates 'tee' shell cmd, you can write to multiple files
    at once.'''
    def __init__(self, file_like_obj):
        #def __init__(self, name, mode):
        #self.file = open(name, mode)
        self.file = file_like_obj
        self.stdout = sys.stdout
        # this makes print() to output text to a Tee obj by default:
        sys.stdout = self

    def __del__(self):
        #reset my stdout the the default stdout:
        sys.stdout = sys.__stdout__   # self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        # redirect to console when writing to a Tee instance:
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def close(self):
        self.__del__()


def emit(self, record):
    """
    The content of this function is taken from logging.StreamHandler.emit()
    and tailored a bit to pretty print the record.

    Read the docs of logging.StreamHandler.emit() if you need more info.
    """

    ### My customization, taken from header of logging module ####
    try:
        unicode
        _unicode = True
    except NameError:
        _unicode = False
    ### end customization ###
    ############################################

    try:
        msg = self.format(record)

        ### My customization ####################

        ''' Eg:
        >>> msg          # as it appears formatted with ANSI color codes,
                         # printed to a file
        '[33m 2013-07-05 09:58:42,475 [35m check: [37m INFO [39;49;0m [34m This is the log msg.[39;49;0m'

        but on terminal you get, with colored text:
        '2013-07-04 22:22:53,749 check: INFO This is the log msg.'
        '''
        # logging.FileHandler inherits logging.StreamHandler
        # FileHandler.emit() delegates to StreamHandler.emit()
        # if message formats differ between the two, we need to operate
        # accordingly
        if not isinstance(self, logging.FileHandler):
            # when self is a logging.StreamHandler obj
            l = msg.split(' ', 7)
            '''
            >>> l
            ['[33m',
             '2013-07-04',
             '22:22:53,749',
             '[35m',
             'check:',
             '[37m',
             'INFO',
             '[39;49;0m [34m - This is the log msg.[39;49;0m']
            '''
            l[4] = l[4].ljust(12)      # l[4] contains funcName -> 'check:'
            l[6] = l[6].ljust(6)       # l[6] contains log level -> 'INFO'
            # the values for .ljust() are to be set according to the shortest
            # and longest function names.
            '''
            >>> l[4]
            'check:     '
            >>> l[6]
            'INFO    '
            '''
        else:
            # when self is a logging.FileHandler obj
            l = msg.split(' ', 4)
            l[2] = l[2].ljust(12)      # l[2] contains funcName -> 'check:'
            l[3] = l[3].ljust(8)       # l[3] contains log level -> 'INFO'

        msg = ' '.join(l)
        '''
        >>> msg
        '2013-07-04 22:22:53,749 check:      INFO     This is the log msg.'
        '''
        ### end customization ###
        #############################################

        stream = self.stream
        fs = "%s\n"
        if not _unicode:  # if no unicode support...
            stream.write(fs % msg)
        else:
            try:
                if (isinstance(msg, unicode) and
                        getattr(stream, 'encoding', None)):
                    ufs = fs.decode(stream.encoding)
                    try:
                        stream.write(ufs % msg)
                    except UnicodeEncodeError:
                        #Printing to terminals sometimes fails. For example,
                        #with an encoding of 'cp1251', the above write will
                        #work if written to a stream opened or wrapped by
                        #the codecs module, but fail when writing to a
                        #terminal even when the codepage is set to cp1251.
                        #An extra encoding step seems to be needed.
                        stream.write((ufs % msg).encode(stream.encoding))
                else:
                    stream.write(fs % msg)
            except UnicodeError:
                stream.write(fs % msg.encode("UTF-8"))
        self.flush()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        self.handleError(record)


### Config file stuff ###

class ConfigParserWithComments(ConfigParser.SafeConfigParser):
    '''This class implements .add_comment() by overriding .write()'''

    def add_comment(self, section, comment):
        self.set(section, '# %s' % comment, None)

    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write("[%s]\n" % ConfigParser.DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                #if (value is not None) or (self._optcre == self.OPTCRE):
                #    key = " = ".join((key, str(value).replace('\n', '\n\t')))
                #fp.write("%s\n" % (key))
                self._write_item(fp, key, value)
            fp.write("\n")

    def _write_item(self, fp, key, value):
        if key.startswith('#') and value is None:
            fp.write("%s\n" % (key,))
        else:
            fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))


def write_default_config_file(d):
    '''This can be used to create the config file from code when the program
    gets installed.
    d -> a dictionary
    '''

    #default_config = {'LOG_LEVEL': "debug",
    #                  'PATH': "/var/log/apt/history*",
    #                  }

    ## set defaults which will be located under [DEFAULT] section:
    #config = ConfigParserWithComments(default_config, allow_no_value=True)

    # ConfigParser.ConfigParser() doesn't seem to care about uppercase letters
    # for keys, only for values.
    config = ConfigParserWithComments(allow_no_value=True)
    config.add_section("LOG")
    config.add_comment("LOG", "Debug level can be 'info' or 'debug'")
    config.set("LOG", "log_level", d['log_level'])
    config.add_comment("LOG", "Set path to default package manager's log files.")
    config.add_comment("LOG", "Path is given as argument to 'zgrep'. It can be a shell path or a shell glob, etc.")
    config.set("LOG", "path", d['path'])

    # TODO: write all config params to file, using a for loop?

    # save config
    with open("main.conf", "wb") as config_file:
        config.write(config_file)


def read_config(logger, filename, defaults):
    '''
    Read from a configuration file that was created by ConfigParser or
    follows a similar layout.

    filename -> a configuration file following the specific layout, syntax.
    defaults -> a dictionary
    '''

    config = ConfigParser.ConfigParser()
    logger.info("Reading configuration file '%s'" % filename)
    config.read(filename)
    for section in config.sections():
        new_config = dict(config.items(section))
        logger.debug("reading values for section '%s'" % section)
        if validate(logger, defaults, new_config):
            defaults.update(new_config)
        #for option, value in config.items(section):
        #    if option in defaults:
        #        if validate(defaults):
        #            defaults.update(config.items(section))
        #        else:
        #            raise ValueError("%s of '%s' is not a valid value" %
        #                             (value, option))
        #    else:
        #        raise KeyError("'%s' is not a valid option" % option)
    logger.info("Loaded configuration file successfully!")
    return defaults


def validate(logger, defaults, new_config):
    '''Tests value based on the type of option. It takes advantage of
    test cases already defined in test.py.'''

    # select only some test classes to be run:
    loader = unittest.defaultTestLoader
    # replace test data with actual data:
    TestConfigValidate.defaults = defaults
    TestConfigValidate.new_config = new_config
    suite = loader.loadTestsFromTestCase(TestConfigValidate)
    # disable TextTestRunner output by passing a stream that no one reads
    runner = unittest.TextTestRunner(stream=StringIO(), verbosity=1)
    logger.debug("parsing values...")
    test_result = runner.run(suite)

    if test_result.failures:          # or .errors if unexpected exceptions
        logger.info("Errors in configuration file, exiting!")
        sys.exit()

    return True


class TestConfigValidate(unittest.TestCase):
    # this is what you get after reading a config file:
    defaults = {'log_level': 'DEBUG',
                'path': "/var/log/apt/history*",
                'conf_file': 'main.conf',
                'log_file': 'out.log',
                }

    # 'log_level'    just 2 levels: DEBUG or INFO
    # 'path'         path to pkg manager's log files
    # 'conf_file'    config file user can edit
    # 'log_file'     app's log file

    # defaults is a class level var so it can be changed outside of the class
    # and thus the change will apply to all class instances.

    new_config = {'log_level': 'DEBUG',
                  'path': "/var/log/apt/history*",
                  'conf_file': 'main.conf',
                  'log_file': 'out.log',
                  }

    def setUp(self):
        '''This is run for every instance of this class.'''

        for d in [self.defaults, self.new_config]:
            # make values case insensitive:
            for key, value in d.items():
                d[key] = value.lower()

            # Log level should be uppercase as it is in logging module
            d['log_level'] = d['log_level'].upper()

    def test_options_are_valid(self):
        #        raise KeyError("'%s' is not a valid option" % option)
        # it should take keys as args or have self.new_config as class
        # attribute
        default_options = set(self.defaults.keys())
        real_options = set(self.new_config.keys())
        for option in real_options:
            try:
                # set up a nice error message for user
                self.assertIn(option, default_options)
            except AssertionError:
                print("Configuration file: "
                      "'%s' is not a valid option.\n"
                      "These are the valid options that you can set: %s \n" %
                      (option, ', '.join(default_options)))
                # without it, the test passes because of 'except':
                raise

    def test_valid_log_level(self):
        log_level = self.new_config['log_level']
        possible_values = ['INFO', 'DEBUG']
        # suppress the ugly AssertionError message upon failure
        # using a 'try: ... except' block.
        # I could have used self.fail(msg="A pretty error message...") but
        # that's ugly too for the user.
        try:
            self.assertIn(log_level, possible_values)
        except AssertionError:
            print("Configuration file: "
                  "'%s' of option '%s' is not a valid value.\n"
                  "Choose one of: %s" %
                  (log_level, 'log_level', ' or '.join(possible_values)))
            # without it, the test passes because of 'except':
            raise

    def test_valid_path(self):
        '''Path must be a shell glob which, after shell expansion, should
        resolve to an absolute or relative path to one or more files (not
        directories).
        '''
        path = self.new_config['path']
        files = glob.glob(path)
        try:
            self.assertNotEqual(files, [])
        except AssertionError:
            print("Configuration file: "
                  "'path' doesn't contain a valid path: '%s'" %
                  (path))
            # without it, the test passes because of 'except':
            raise

#    def test_valid_conf_filename(self):
#        '''Don't know what to test about a filename which gets created anyway
#        if it doesn't exist.'''
#        pass
#
#    def test_valid_log_filename(self):
#        '''The same as test_valid_conf_filename.'''
#        pass


### End Config file stuff ###
