#!/usr/bin/python

import unittest
import collections

# Import remove_desktop modules
import remove_desktop as rd
#import utils


class TestParser(unittest.TestCase):
    def setUp(self):
        self.line = "/var/log/apt/history.log.7.gz:Install: " + \
                    "lightdm-gtk-greeter:i386 (1.3.1-0ubuntu1), " + \
                    "pidgin-libnotify:i386 (0.14-4ubuntu11, automatic), " + \
                    "libgpgme++2:i386 (4.9.2-0ubuntu1, automatic), " + \
                    "libxfcegui4-4:i386 (4.10.0-1, automatic)"
        self.d = rd.parser(self.line)

    def test_returns_ordered_dict(self):
        x = isinstance(self.d, collections.OrderedDict)
        self.assertEqual(True, x)

    def test_parser_finds_package_name_arch_version(self):
        self.assertEqual(self.d['lightdm-gtk-greeter'],
                         (u'i386', u'1.3.1-0ubuntu1'))

    def test_parser_finds_package_pidgin_libnotify(self):
        self.assertEqual(self.d['pidgin-libnotify'],
                         (u'i386', u'0.14-4ubuntu11, automatic'))

    def test_parser_finds_package_libxfcegui4(self):
        self.assertEqual(self.d['libxfcegui4-4'],
                         (u'i386', u'4.10.0-1, automatic'))

    def test_parser_finds_package_libgpgme(self):
        '''This libgpgme++2 is part of kubuntu-desktop meta-package.'''
        self.assertEqual(self.d['libgpgme++2'],
                         (u'i386', u'4.9.2-0ubuntu1, automatic'))

    def test_parser_extracts_all_packages(self):
        x = len(self.d.keys())
        self.assertEqual(4, x)


class TestParserStage2(unittest.TestCase):
    def setUp(self):
        '''
        This fixture simulates that 'xubuntu-desktop' metapackage was
        installed, usually with these packages.
        '''

        self.packages = [u'lightdm-gtk-greeter', u'libxfcegui4-4',
                         u'gthumb', u'blueman',
                         u'pidgin-libnotify', u'tumbler',
                         u'gmusicbrowser', u'xchat-common',
                         u'libxfce4util-bin', u'brltty-x11',
                         u'xscreensaver-gl', u'tumbler-common',
                         u'libthunarx-2-0', u'libotr2',
                         u'libots0', u'xfce4-xkb-plugin',
                         u'gthumb-data', u'libdigest-crc-perl',
                         u'xfce4-notifyd', u'xchat',
                         u'xfce4-volumed', u'libintl-perl',
                         u'xfce4-verve-plugin', u'xfce4-panel',
                         u'libtagc0', u'abiword-common',
                         u'xfce4-taskmanager', u'abiword',
                         u'abiword-plugin-mathview', u'xfce4-mailwatch-plugin',
                         u'libjpeg-turbo-progs', u'xscreensaver',
                         u'libgtk2-notify-perl', u'thunar-volman',
                         u'libgtk2-trayicon-perl', u'libxml-twig-perl',
                         u'xfce4-notes-plugin', u'plymouth-theme-xubuntu-logo',
                         u'shimmer-themes', u'parole',
                         u'fonts-lyx', u'orage',
                         u'pidgin-data', u'libabiword-2.9',
                         u'indicator-application-gtk2', u'xfce4-appfinder',
                         u'system-tools-backends', u'libgarcon-1-0',
                         u'pavucontrol', u'libxfce4util6',
                         u'libloudmouth1-0', u'link-grammar-dictionaries-en',
                         u'xfce-keyboard-shortcuts', u'libsexy2',
                         u'libido-0.1-0', u'libtidy-0.99-0',
                         u'libxfce4util-common', u'libnet-dbus-perl',
                         u'xfce4-weather-plugin', u'xfce4-netload-plugin',
                         u'thunar-archive-plugin', u'ristretto',
                         u'xubuntu-default-settings', u'screensaver-default-images',
                         u'xfce4-indicator-plugin', u'libwv-1.2-4',
                         u'thunar', u'libgarcon-common',
                         u'libgdome2-0', u'xfce4-notes',
                         u'libgsf-1-common', u'xfwm4',
                         u'abiword-plugin-grammar', u'xbrlapi',
                         u'xfce4-systemload-plugin', u'thunar-media-tags-plugin',
                         u'xubuntu-artwork', u'libtumbler-1-0',
                         u'xubuntu-desktop', u'indicator-sound-gtk2',
                         u'gigolo', u'libxfce4ui-1-0',
                         u'xfce4-settings', u'gnome-time-admin',
                         u'xfce4-cpugraph-plugin', u'thunar-data',
                         u'libxfce4ui-utils', u'xfdesktop4',
                         u'xfce4-power-manager', u'plymouth-theme-xubuntu-text',
                         u'libxml-xpath-perl', u'xfce4-power-manager-data',
                         u'libgdome2-cpp-smart0c2a', u'libexo-1-0',
                         u'xfce4-quicklauncher-plugin', u'pidgin',
                         u'liboobs-1-5', u'libkeybinder0',
                         u'exo-utils', u'xubuntu-docs',
                         u'liblink-grammar4', u'gnome-system-tools',
                         u'libgtkmathview0c2a', u'libgstreamer-perl',
                         u'pidgin-otr', u'xfce4-terminal',
                         u'pidgin-microblog', u'xfconf',
                         u'catfish', u'gstreamer0.10-gnomevfs',
                         u'xfburn', u'xfce4-session',
                         u'xfce4-screenshooter', u'libxfconf-0-2',
                         u'libjpeg-progs', u'xfce4-places-plugin',
                         u'pastebinit', u'xubuntu-wallpapers',
                         u'xfdesktop4-data', u'libexo-common',
                         u'xscreensaver-data', u'libgsf-1-114',
                         u'xubuntu-icon-theme',
                         u'libexo-helpers']

    def test_package_will_be_removed(self):
        def is_installed(package):
            '''
            Tells which packages are installed on a virtual testing OS.
            Helpful to test what packages will be removed or kept, even if
            they don't exist on the system.
            '''
            if package in ['gnome-brave-icon-theme']:
                return False
            return True

        '''
        decide if xubuntu-artwork is to be removed, as it is a dependency
        only for packages that will be removed and for a package that is not
        installed:
        get reverse dependencies for 'xubuntu-artwork', using:
         $: apt-cache rdepends xubuntu-artwork
        xubuntu-artwork
        Reverse Depends:
          xubuntu-desktop                       # will be removed
          xubuntu-default-settings              # will be removed
          shimmer-themes                        # will be removed
          shimmer-themes                        # will be removed
          gnome-brave-icon-theme                # not installed
        '''
        # The first four will be removed because they exist in self.packages,
        # The last one is not installed
        # after some python space stripping, we get:
        rdeps = ['xubuntu-desktop', 'xubuntu-default-settings',
                 'shimmer-themes', 'shimmer-themes', 'gnome-brave-icon-theme']

        self.assertEqual("remove", rd.parser_stage_2(rdeps,
                                                     self.packages,
                                                     callback=is_installed))

    def test_package_will_be_kept(self):
        '''
        Decide if lightdm-gtk-greeter is going to be removed.
          $: apt-cache rdepends lightdm-gtk-greeter
        lightdm-gtk-greeter
        Reverse Depends:
          xubuntu-desktop                     # will be removed
          xubuntu-default-settings            # will be removed
          ubuntustudio-lightdm-theme          # not installed
          ubuntustudio-desktop                # not installed
          ubuntustudio-default-settings       # not installed
          mythbuntu-lightdm-theme             # not installed
          lubuntu-default-settings            # installed & will be kept
          lubuntu-core                        # installed & will be kept
        '''
        def is_installed(package):
            '''
            Tells which packages are installed on a virtual testing OS.
            Helpful to test what packages will be removed or kept, even if
            they don't exist on the system.
            '''
            if package in ['ubuntustudio-lightdm-theme',
                           'ubuntustudio-desktop',
                           'ubuntustudio-default-settings',
                           'mythbuntu-lightdm-theme']:
                return False
            return True

        rdeps = ['xubuntu-desktop',
                 'xubuntu-default-settings',
                 'ubuntustudio-lightdm-theme',
                 'ubuntustudio-desktop',
                 'ubuntustudio-default-settings',
                 'mythbuntu-lightdm-theme',
                 'lubuntu-default-settings',
                 'lubuntu-core']

        self.assertEqual("keep", rd.parser_stage_2(rdeps,
                                                   self.packages,
                                                   callback=is_installed))


# run all tests:
if __name__ == '__main__':
    print("Running tests...")
    ### load and run tests from other files ###
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromName('utils.TestConfigValidate')
    #print(suite.countTestCases())
    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)

    ### run tests from this file ###
    unittest.main()
    print("Done!")
