==============
REMOVE DESKTOP
==============
[LONG DESCRIPTION]

Remove Desktop uninstalls desktops like gnome-desktop, xubuntu-desktop, etc. that leave a lot of dependencies behind when removed with the default package manager.

Although it was designed for desktop meta-packages, any meta-package will do.

The program is useful when desktops were installed at the command line or using graphical package managers on:
Ubuntu 10.04, Ubuntu 10.10, Ubuntu 11.04, Ubuntu 11.10, Ubuntu 12.04, Ubuntu 12.10, etc.

Currently, the script is for distributions using the *apt** family package managers.

What is a meta-package?
-----------------------
A package that installs other packages designed to work as a whole. Although it's installed like any other package, usually it cannot be removed easily(it leaves a lot of packages, as dependencies, behind when removed with the default package manager).

Examples of metapackages:

* xubuntu-desktop
* ubuntu-desktop
* sugar-session
* kubuntu-desktop
* lubuntu-desktop
* etc.

Example::

    sudo apt-get purge lubuntu-desktop

removes lubuntu-desktop meta-package(a few MBytes) but might leave behind a lot of dependencies that can take up to several hundred MBytes.

This is where *remove-desktop* steps in::

    remove-desktop lubuntu-desktop 

For more info, type::

    remove-desktop --help

Features:
---------
    * When fully removing the metapackages, it keeps all packages needed by packages external to the metapackage.  

References
----------
The scripts' logic is based on:
    * for ubuntu 12.04
           http://complete-concrete-concise.com/ubuntu-2/ubuntu-12-04/ubuntu-12-04-how-to-completely-uninstallremove-a-packagesoftwareprogram

    * for ubuntu 12.10
           http://complete-concrete-concise.com/ubuntu-2/ubuntu-12-10/ubuntu-12-10-how-to-completely-uninstallremove-a-packagesoftwareprogram

