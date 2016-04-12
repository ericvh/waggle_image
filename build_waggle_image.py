#!/usr/bin/env python
import time, os, commands, subprocess, shutil, sys
from subprocess import call, check_call
import os.path


# One of the most significant modifications that this script does is setting static IPs. Nodecontroller and guest node have different static IPs.


print "usage: python -u ./build_waggle_image.py 2>&1 | tee build.log"

data_directory="/root"

report_file="/root/report.txt"

waggle_stock_url='http://www.mcs.anl.gov/research/projects/waggle/downloads/stock_images/'
base_images=   {
                'odroid-xu3' : {
                        'filename': "ubuntu-14.04lts-server-odroid-xu3-20150725.img",
                         'url': waggle_stock_url
                        },
                'odroid-c1' : {
                        'filename':"ubuntu-14.04.3lts-lubuntu-odroid-c1-20151020.img",
                        'url': waggle_stock_url
                    } 
                }


create_b_image = 0 # need to update the change_partition_uuid.sh first to get it work on loop device

change_partition_uuid_script = os.path.abspath(os.path.curdir) + '/change_partition_uuid.sh'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

mount_point_A="/mnt/newimage_A"




is_guestnode = 0 # will be set automatically to 1 if an odroid-xu3 is detected !



if create_b_image and not os.path.isfile(change_partition_uuid_script):
    print change_partition_uuid_script, " not found"
    sys.exit(1)

if not os.path.isfile( data_directory+ '/waggle-id_rsa'):
    print data_directory+ '/waggle-id_rsa not found. Disable this check in the script to continue anyway.' 
    sys.exit(1)


###                              ###
###  Script for chroot execution ###
###                              ###

#TODO enable upgrade again

base_build_init_script = '''\
#!/bin/bash
set -x
set -e

###locale
locale-gen "en_US.UTF-8"
dpkg-reconfigure locales

### timezone 
echo "Etc/UTC" > /etc/timezone 
dpkg-reconfigure --frontend noninteractive tzdata

# because of "Failed to fetch http://ports.ubuntu.com/... ...Hash Sum mismatch"
rm -rf /var/lib/apt/lists/*
apt-get clean
apt-get update



mkdir -p /etc/waggle/
echo "10.31.81.10" > /etc/waggle/node_controller_host


# TODO: remove libgcc-4.9-dev libstdc++-4.9-dev or similar



export KEEP_PACKAGES="glib-networking+ libsoup2.4-1+ wpasupplicant+ policykit-1+ network-manager+ dpkg+ libselinux1+ python3+"

set -e

declare -a unwanted=("^gimp-*" "^x11*" abiword* apport* aspell aspell-en audacious* ca-certificates-java chromium-* consolekit python-crcmod cups-* dictionaries-common dpkg-dev fonts-* fonts-dejavu-core "^gnome-*" gstreamer* gvfs-common gvfs-libs:armhf hicolor-icon-theme hplip-data hunspell-en-us imagemagick-common jade java-common joe kerneloops-daemon ladspa-sdk laptop-detect libart-2.0-dev libasound2-dev libatomic-ops-dev libaudit-dev libavahi-client-dev libavahi-common-dev libavc1394-0:armhf libavresample1:armhf libavutil52:armhf libbison-dev libbluetooth3:armhf libbluray1:armhf libbonobo2-common libbonoboui2-common libboost* libbs2b0 libburn4 libbz2-dev libc-dev-bin libc6-dev libcaca0:armhf libcamel-1.2-45 libcap-dev libcdaudio1 libcddb2 libcdio-cdda1 libcdio-paranoia1 libcdio13 libcdparanoia0:armhf libcdt5 libcec2 libcgraph6 libcogl15:armhf libcolamd2.8.0:armhf libcolord1:armhf libcolorhug1:armhf libcompfaceg1 libcrack2:armhf libcroco3:armhf libcue1 libcups2:armhf libcupscgi1:armhf libcupsfilters1:armhf libcupsimage2:armhf libcupsmime1:armhf libcupsppdc1:armhf libdatrie1:armhf libdbus-1-dev libdc1394-22:armhf libdca0:armhf libdirac-decoder0:armhf libdirac-encoder0:armhf libdiscid0:armhf libdjvulibre-text libdjvulibre21:armhf libdmx1:armhf libdrm-nouveau2:armhf libdrm-omap1:armhf libdrm-radeon1:armhf libdv4:armhf libdvdnav4:armhf libdvdread4:armhf libegl1-mesa-drivers:armhf libegl1-mesa:armhf libenca-dev libexempi-dev libexo-common libexo-helpers libexpat1-dev libfaad2:armhf libfakeroot:armhf libffi-dev libfftw3-bin libfftw3-double3:armhf libfftw3-single3:armhf libfl-dev libflac8:armhf libfontembed1:armhf libfontenc1:armhf libframe6:armhf libfreetype6:armhf libfribidi0:armhf libfs6:armhf libftdi1:armhf libfuse2:armhf libgbm1:armhf libgck-1-0:armhf libgcr-3-common libgcr-base-3-1:armhf libgcrypt11-dev libgda-5.0-common libgdk-pixbuf2.0-0:armhf libgdk-pixbuf2.0-common libgdome2-0 libgdome2-cpp-smart0c2a libgeis1:armhf libgeoclue0:armhf libgeoip1:armhf libgif4:armhf libgirepository-1.0-1 libgl1-mesa-dri:armhf libgl1-mesa-glx:armhf libglapi-mesa:armhf libgles1-mesa:armhf libgles2-mesa:armhf libglib-perl libglib2.0-doc libgme0 libgmpxx4ldbl:armhf libgoffice-0.10-10-common libgomp1:armhf libgpg-error-dev libgphoto2-port10:armhf libgraphite2-3:armhf libgs9-common libgsf-1-114 libgsf-1-common libgsl0ldbl libgsm1:armhf libgtk* libgtk-3-common libgtk2.0-common libgtop2-7 libgtop2-common libguess1:armhf libgusb2:armhf libgutenprint2 libgweather-common libhogweed2:armhf libhpmud0 libhunspell-1.3-0:armhf libibus-1.0-5:armhf libical1 libid3tag0 libidn11-dev libieee1284-3:armhf libijs-0.35 libilmbase6:armhf libimage-exiftool-perl libiptcdata0 libisofs6 libiw30:armhf libjack-jackd2-0:armhf libjasper1:armhf libjavascriptcoregtk-3.0-0:armhf libjbig0:armhf libjbig2dec0 libjna-java libjpeg-turbo8:armhf libjpeg8:armhf libjs-jquery libjte1 libkate1 liblavjpeg-2.1-0 liblcms2-2:armhf libldap2-dev liblircclient0 libllvm3.4:armhf liblockfile-bin liblockfile1:armhf libloudmouth1-0 liblqr-1-0:armhf libltdl7:armhf liblua5.2-0:armhf liblzma-dev liblzo2-dev libmad0:armhf libmbim-glib0:armhf libmeanwhile1 libmenu-cache-bin libmenu-cache3 libmessaging-menu0 libmicrohttpd10 libmikmod2:armhf libmimic0 libmirprotobuf0:armhf libmjpegutils-2.1-0 libmms0:armhf libmodplug1 libmp3lame0:armhf libmpcdec6 libmpeg2-4:armhf libmpeg2encpp-2.1-0 libmpeg3-dev libmpg123-0:armhf libmplex2-2.1-0 libmtdev1:armhf libmtp-common libmtp-runtime libmtp9:armhf libncurses5-dev libnetpbm10 libnettle4:armhf libnfs-dev libobt2 libogg0:armhf libopenal-data libopenal1:armhf libopencv* libopenjpeg2:armhf libopenobex1 libopenvg1-mesa:armhf libopus-dev liborbit-2-0:armhf liborc-0.4-0:armhf libots0 libp11-kit-dev libp11-kit-gnome-keyring:armhf libpam-gnome-keyring:armhf libpaper-utils libpaper1:armhf libpathplan4 libpciaccess-dev libpcre3-dev libpixman-1-0-dbg:armhf libpixman-1-0:armhf libplist1:armhf libpopt-dev libpostproc52 libprotobuf-lite8:armhf libprotobuf8:armhf libpthread-stubs0-dev libpython2.7-dev libqmi-glib0:armhf libqpdf13:armhf libquvi-scripts libraptor2-0:armhf librarian0 librasqal3:armhf libraw1394-11:armhf libreadline-dev libreadline6-dev libreoffice-* librxtx-java libsamplerate0:armhf libsane-common libsbc1:armhf libschroedinger-1.0-0:armhf libsecret-1-0:armhf libsecret-common libselinux1-dev libsepol1-dev libsidplayfp:armhf libsoundtouch0:armhf libsp1c2 libspeex1:armhf libspeexdsp1:armhf libsqlite3-dev libsrtp0 libssh2-1-dev libt1-5 libtag1-vanilla:armhf libtag1c2a:armhf libtagc0:armhf libtasn1-6-dev libtcl8.6:armhf libtelepathy-glib0:armhf libthai-data libtheora0:armhf libtinfo-dev libtinyxml-dev libudev-dev libudisks2-0:armhf libusb-1.0-0-dev libusb-dev libusbmuxd2 libv4l2rds0:armhf libva1:armhf libvdpau1:armhf libvisual-0.4-0:armhf libvo-aacenc0:armhf libvo-amrwbenc0:armhf libvpx1:armhf libvte-2.90-common libvte-common libwavpack1:armhf libwayland-client0:armhf libwayland-cursor0:armhf libwayland-server0:armhf libwbclient0:armhf libwebcam0 libwebkitgtk-3.0-common libwebp5:armhf libwebpdemux1:armhf libwebpmux1:armhf libwhoopsie0 libwildmidi-config libwildmidi1:armhf libwnck-3-common libwnck-common libwpd-0.9-9 libwpg-0.2-2 libwps-0.2-2 libwvstreams4.6-base libwvstreams4.6-extras libx11-6:armhf libx11-data libx11-xcb1:armhf libx264-142:armhf libxapian22 libxau6:armhf libxcb-* libxcomposite1:armhf libxcursor1:armhf libxdamage1:armhf libxdmcp6:armhf libxdot4 libxext6:armhf libxfce4ui-common libxfce4util-common libxfce4util6 libxfixes3:armhf libxi6:armhf libxinerama1:armhf libxkbfile1:armhf libxml2-dev libxp6:armhf libxshmfence-dev libxslt1-dev libxvidcore-dev lightdm link-grammar-dictionaries-en lintian linux-libc-dev linux-sound-base lubuntu-lxpanel-icons lxmenu-data lxsession-data m4 mc mc-data mesa* metacity-common mircommon-dev:armhf mobile-broadband-provider-info mysql-common nautilus-data netpbm obex-data-server openjdk-7-jre openjdk-7-jre* openprinting-ppds p11-kit p11-kit-modules:armhf pastebinit pcmciautils pidgin-data policykit-desktop-privileges poppler-data printer-driver-c2esp printer-driver-foo2zjs-common printer-driver-min12xxw pulseaudio pulseaudio* python-cups python-cupshelpers python-dbus-dev python2.7-dev qpdf quilt rfkill samba* samba-* sgml-base sgml-data sgmlspl smbclient snappy sound-theme-freedesktop swig swig2.0 sylpheed-doc system-config-printer-common system-config-printer-udev t1utils transmission* transmission-common tsconf ttf-* uno-libs3 usb-modeswitch usbmuxd uvcdynctrl uvcdynctrl-data valgrind valgrind whoopsie wireless-tools wvdial wvdial x11-xfs-utils x11proto-* xarchiver xarchiver xbmc xdg-user-dirs xdg-user-dirs-gtk xfce4-* xfce4-power-manager xfonts-100dpi xfonts-base xfonts-mathml xfonts-scalable xfonts-utils xinit xinput xserver-* xserver-xorg-core xul-ext-ubufox dmz-cursor-theme gnumeric-common evince-common faenza-icon-theme filezilla-common extra-xdg-menus aptdaemon-data libhangul1 libhangul-data anthy app-install-data python-wheel sunpinyin-data libflite1 anthy-common m17n-db libchewing3* libjavascriptcoregtk-1.0-0 aria2 libaspell15 liblapack3 shared-mime-info python-reportlab gconf-service gconf2-common )

export unwanted_count=${{#unwanted[@]}}

# first try to remove what can be removed
CHUNK_SIZE=10
set +e
for i in $(seq 0 ${{CHUNK_SIZE}} ${{unwanted_count}})  ; do 
  export subset_unwanted=${{unwanted[@]:${{i}}:${{CHUNK_SIZE}}}}
  
  apt-get purge -y --force-yes --ignore-missing ${{subset_unwanted}} ${{KEEP_PACKAGES}}
  sleep 1
done
set -e


apt-get upgrade -y

CHUNK_SIZE=50
for i in $(seq 0 ${{CHUNK_SIZE}} ${{unwanted_count}})  ; do 
  export subset_unwanted=${{unwanted[@]:${{i}}:${{CHUNK_SIZE}}}}
  
  apt-get purge -y --force-yes --ignore-missing ${{subset_unwanted}} ${{KEEP_PACKAGES}}
  sleep 1
done


# uninstall ntp, we use beehive1 as time server
apt-get purge -y --force-yes --ignore-missing ntp ntpdate


#apt-get purge -y --force-yes --ignore-missing \
#"^gimp-*" "^x11*" abiword* apport* aspell aspell-en audacious* ca-certificates-java chromium-* consolekit python-crcmod cups-* dictionaries-common dpkg-dev fonts-* fonts-dejavu-core "^gnome-*" gstreamer* gvfs-common gvfs-libs:armhf hicolor-icon-theme hplip-data hunspell-en-us imagemagick-common jade java-common joe kerneloops-daemon ladspa-sdk laptop-detect libart-2.0-dev libasound2-dev libatomic-ops-dev libaudit-dev libavahi-client-dev libavahi-common-dev libavc1394-0:armhf libavresample1:armhf libavutil52:armhf libbison-dev libbluetooth3:armhf libbluray1:armhf libbonobo2-common libbonoboui2-common libboost* libbs2b0 libburn4 libbz2-dev libc-dev-bin libc6-dev libcaca0:armhf libcamel-1.2-45 libcap-dev libcdaudio1 libcddb2 libcdio-cdda1 libcdio-paranoia1 libcdio13 libcdparanoia0:armhf libcdt5 libcec2 libcgraph6 libcogl15:armhf libcolamd2.8.0:armhf libcolord1:armhf libcolorhug1:armhf libcompfaceg1 libcrack2:armhf libcroco3:armhf libcue1 libcups2:armhf libcupscgi1:armhf libcupsfilters1:armhf libcupsimage2:armhf libcupsmime1:armhf libcupsppdc1:armhf libdatrie1:armhf libdbus-1-dev libdc1394-22:armhf libdca0:armhf libdirac-decoder0:armhf libdirac-encoder0:armhf libdiscid0:armhf libdjvulibre-text libdjvulibre21:armhf libdmx1:armhf libdrm-nouveau2:armhf libdrm-omap1:armhf libdrm-radeon1:armhf libdv4:armhf libdvdnav4:armhf libdvdread4:armhf libegl1-mesa-drivers:armhf libegl1-mesa:armhf libenca-dev libexempi-dev libexo-common libexo-helpers libexpat1-dev libfaad2:armhf libfakeroot:armhf libffi-dev libfftw3-bin libfftw3-double3:armhf libfftw3-single3:armhf libfl-dev libflac8:armhf libfontembed1:armhf libfontenc1:armhf libframe6:armhf libfreetype6:armhf libfribidi0:armhf libfs6:armhf libftdi1:armhf libfuse2:armhf libgbm1:armhf libgck-1-0:armhf libgcr-3-common libgcr-base-3-1:armhf libgcrypt11-dev libgda-5.0-common libgdk-pixbuf2.0-0:armhf libgdk-pixbuf2.0-common libgdome2-0 libgdome2-cpp-smart0c2a libgeis1:armhf libgeoclue0:armhf libgeoip1:armhf libgif4:armhf libgirepository-1.0-1 libgl1-mesa-dri:armhf libgl1-mesa-glx:armhf libglapi-mesa:armhf libgles1-mesa:armhf libgles2-mesa:armhf libglib-perl libglib2.0-doc libgme0 libgmpxx4ldbl:armhf libgoffice-0.10-10-common libgomp1:armhf libgpg-error-dev libgphoto2-port10:armhf libgraphite2-3:armhf libgs9-common libgsf-1-114 libgsf-1-common libgsl0ldbl libgsm1:armhf libgtk* libgtk-3-common libgtk2.0-common libgtop2-7 libgtop2-common libguess1:armhf libgusb2:armhf libgutenprint2 libgweather-common libhogweed2:armhf libhpmud0 libhunspell-1.3-0:armhf libibus-1.0-5:armhf libical1 libid3tag0 libidn11-dev libieee1284-3:armhf libijs-0.35 libilmbase6:armhf libimage-exiftool-perl libiptcdata0 libisofs6 libiw30:armhf libjack-jackd2-0:armhf libjasper1:armhf libjavascriptcoregtk-3.0-0:armhf libjbig0:armhf libjbig2dec0 libjna-java libjpeg-turbo8:armhf libjpeg8:armhf libjs-jquery libjte1 libkate1 liblavjpeg-2.1-0 liblcms2-2:armhf libldap2-dev liblircclient0 libllvm3.4:armhf liblockfile-bin liblockfile1:armhf libloudmouth1-0 liblqr-1-0:armhf libltdl7:armhf liblua5.2-0:armhf liblzma-dev liblzo2-dev libmad0:armhf libmbim-glib0:armhf libmeanwhile1 libmenu-cache-bin libmenu-cache3 libmessaging-menu0 libmicrohttpd10 libmikmod2:armhf libmimic0 libmirprotobuf0:armhf libmjpegutils-2.1-0 libmms0:armhf libmodplug1 libmp3lame0:armhf libmpcdec6 libmpeg2-4:armhf libmpeg2encpp-2.1-0 libmpeg3-dev libmpg123-0:armhf libmplex2-2.1-0 libmtdev1:armhf libmtp-common libmtp-runtime libmtp9:armhf libncurses5-dev libnetpbm10 libnettle4:armhf libnfs-dev libobt2 libogg0:armhf libopenal-data libopenal1:armhf libopencv* libopenjpeg2:armhf libopenobex1 libopenvg1-mesa:armhf libopus-dev liborbit-2-0:armhf liborc-0.4-0:armhf libots0 libp11-kit-dev libp11-kit-gnome-keyring:armhf libpam-gnome-keyring:armhf libpaper-utils libpaper1:armhf libpathplan4 libpciaccess-dev libpcre3-dev libpixman-1-0-dbg:armhf libpixman-1-0:armhf libplist1:armhf libpopt-dev libpostproc52 libprotobuf-lite8:armhf libprotobuf8:armhf libpthread-stubs0-dev libpython2.7-dev libqmi-glib0:armhf libqpdf13:armhf libquvi-scripts libraptor2-0:armhf librarian0 librasqal3:armhf libraw1394-11:armhf libreadline-dev libreadline6-dev libreoffice-* librxtx-java libsamplerate0:armhf libsane-common libsbc1:armhf libschroedinger-1.0-0:armhf libsecret-1-0:armhf libsecret-common libselinux1-dev libsepol1-dev libsidplayfp:armhf libsoundtouch0:armhf libsp1c2 libspeex1:armhf libspeexdsp1:armhf libsqlite3-dev libsrtp0 libssh2-1-dev libt1-5 libtag1-vanilla:armhf libtag1c2a:armhf libtagc0:armhf libtasn1-6-dev libtcl8.6:armhf libtelepathy-glib0:armhf libthai-data libtheora0:armhf libtinfo-dev libtinyxml-dev libudev-dev libudisks2-0:armhf libusb-1.0-0-dev libusb-dev libusbmuxd2 libv4l2rds0:armhf libva1:armhf libvdpau1:armhf libvisual-0.4-0:armhf libvo-aacenc0:armhf libvo-amrwbenc0:armhf libvpx1:armhf libvte-2.90-common libvte-common libwavpack1:armhf libwayland-client0:armhf libwayland-cursor0:armhf libwayland-server0:armhf libwbclient0:armhf libwebcam0 libwebkitgtk-3.0-common libwebp5:armhf libwebpdemux1:armhf libwebpmux1:armhf libwhoopsie0 libwildmidi-config libwildmidi1:armhf libwnck-3-common libwnck-common libwpd-0.9-9 libwpg-0.2-2 libwps-0.2-2 libwvstreams4.6-base libwvstreams4.6-extras libx11-6:armhf libx11-data libx11-xcb1:armhf libx264-142:armhf libxapian22 libxau6:armhf libxcb-* libxcomposite1:armhf libxcursor1:armhf libxdamage1:armhf libxdmcp6:armhf libxdot4 libxext6:armhf libxfce4ui-common libxfce4util-common libxfce4util6 libxfixes3:armhf libxi6:armhf libxinerama1:armhf libxkbfile1:armhf libxml2-dev libxp6:armhf libxshmfence-dev libxslt1-dev libxvidcore-dev lightdm link-grammar-dictionaries-en lintian linux-libc-dev linux-sound-base lubuntu-lxpanel-icons lxmenu-data lxsession-data m4 mc mc-data mesa* metacity-common mircommon-dev:armhf mobile-broadband-provider-info mysql-common nautilus-data netpbm obex-data-server openjdk-7-jre openjdk-7-jre* openprinting-ppds p11-kit p11-kit-modules:armhf pastebinit pcmciautils pidgin-data policykit-desktop-privileges poppler-data printer-driver-c2esp printer-driver-foo2zjs-common printer-driver-min12xxw pulseaudio pulseaudio* python-cups python-cupshelpers python-dbus-dev python2.7-dev qpdf quilt rfkill samba* samba-* sgml-base sgml-data sgmlspl smbclient snappy sound-theme-freedesktop swig swig2.0 sylpheed-doc system-config-printer-common system-config-printer-udev t1utils transmission* transmission-common tsconf ttf-* uno-libs3 usb-modeswitch usbmuxd uvcdynctrl uvcdynctrl-data valgrind valgrind whoopsie wireless-tools wvdial wvdial x11-xfs-utils x11proto-* xarchiver xarchiver xbmc xdg-user-dirs xdg-user-dirs-gtk xfce4-* xfce4-power-manager xfonts-100dpi xfonts-base xfonts-mathml xfonts-scalable xfonts-utils xinit xinput xserver-* xserver-xorg-core xul-ext-ubufox dmz-cursor-theme gnumeric-common evince-common faenza-icon-theme filezilla-common extra-xdg-menus aptdaemon-data libhangul1 libhangul-data anthy app-install-data python-wheel sunpinyin-data libflite1 anthy-common m17n-db libchewing3* libjavascriptcoregtk-1.0-0 aria2 libaspell15 liblapack3 shared-mime-info python-reportlab gconf-service gconf2-common \
#${{KEEP_PACKAGES}}

set +e
# Note that the last line contains packages we do not want to be removed ! Those package have a plus character as suffix.


# In case you make changes to the above list of packages, you may want to sort it afterwards:
# example: echo b a | tr " " "n" | sort | tr "n" " " # n should be linebreak
# another tipp: use dpkg -S <path> to find packages

# more tipps:

# full list of installed packages: 
# export MYPACKAGES=`dpkg -l | grep "ii" | cut -d ' ' -f 3 | tr 'n' ' '` ; echo ${{MYPACKAGES}}
# dpkg-query -W --showformat='${{Installed-Size;10}}\t${{Package}}n' | sort -k1,1n


# Cleaning, upgrading and more cleaning:

rm -rf /usr/local/share/kodi/ /etc/cups /usr/lib/xorg/modules/drivers /var/lib/{{bluetooth,alsa}} /usr/share/{{icons,anthy,python-wheels}}


apt-get clean
apt-get autoclean
apt-get upgrade -y
apt-get clean
apt-get autoclean
apt-get autoremove -y
dpkg --list | grep ^rc | awk -F" " ' {{ print $2 }} ' | xargs apt-get -y purge

# Packages we want to install:
set -e
apt-get install -y htop iotop iftop bwm-ng screen git python-dev python-serial python-pip tree psmisc wvdial



mkdir -p /usr/lib/waggle/
cd /usr/lib/waggle/
git clone https://github.com/waggle-sensor/waggle_image.git
cd waggle_image
./configure


# make sure serial console requires password
sed -i -e 's:exec /bin/login -f root:exec /bin/login:' /bin/auto-root-login

'''


base_build_final_script='''\


### kill X processses
set +e
killall -u lightdm -9



### username
export odroid_exists=$(id -u odroid > /dev/null 2>&1; echo $?)
export waggle_exists=$(id -u waggle > /dev/null 2>&1; echo $?)

# rename existing user odroid to waggle
if [ ${{odroid_exists}} == 0 ] && [ ${{waggle_exists}} != 0 ] ; then
  echo "I will kill all processes of the user \"odroid\" now."
  sleep 1
  killall -u odroid -9
  sleep 2

  set -e

  #This will change the user's login name. It requires you logged in as another user, e.g. root
  usermod -l waggle odroid

  # real name
  usermod -c "waggle user" waggle

  #change home directory
  usermod -m -d /home/waggle/ waggle

  set +e
fi

# create new user waggle
if [ ${{odroid_exists}} != 0 ] && [ ${{waggle_exists}} != 0 ] ; then
  
  
  set -e
  
  adduser --disabled-password --gecos "" waggle

  # real name
  usermod -c "waggle user" waggle


  set +e
fi


# verify waggle user has been created
set +e
id -u waggle > /dev/null 2>&1
if [ $? -ne 0 ]; then 
  echo "error: unix user waggle was not created"
  exit 1 
fi


# check if odroid group exists
getent group odroid > /dev/null 2>&1
if [ $? -eq 0 ]; then 
  echo "\"odroid\" group exists, will rename it to \"waggle\""
  groupmod -n waggle odroid || exit 1 
else
  getent group waggle > /dev/null 2>&1 
  if [ $? -eq 0 ]; then 
    echo "Neither waggle nor odroid group exists. Will create odroid group."
    addgroup waggle
  fi
fi



# verify waggle group has been created
getent group waggle > /dev/null 2>&1 
if [ $? -ne 0 ]; then 
  echo "error: unix group waggle was not created"
  exit 1 
fi

echo "adding user waggle to group waggle"
adduser waggle waggle

echo "sudo access for user waggle"
adduser waggle sudo

set -e


### disallow root access
sed -i 's/\(PermitRootLogin\) .*/\\1 no/' /etc/ssh/sshd_config

### default password
echo waggle:waggle | chpasswd
echo root:waggle | chpasswd

### Remove ssh host files. Those will be recreated by the /etc/rc.local script by default.
rm -f /etc/ssh/ssh_host*


# set AoT_key
mkdir -p /home/waggle/.ssh/
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYPMSrC6k33vqzulXSx8141ThfNKXiyFxwNxnudLCa0NuE1SZTMad2ottHIgA9ZawcSWOVkAlwkvufh4gjA8LVZYAVGYHHfU/+MyxhK0InI8+FHOPKAnpno1wsTRxU92xYAYIwAz0tFmhhIgnraBfkJAVKrdezE/9P6EmtKCiJs9At8FjpQPUamuXOy9/yyFOxb8DuDfYepr1M0u1vn8nTGjXUrj7BZ45VJq33nNIVu8ScEdCN1b6PlCzLVylRWnt8+A99VHwtVwt2vHmCZhMJa3XE7GqoFocpp8TxbxsnzSuEGMs3QzwR9vHZT9ICq6O8C1YOG6JSxuXupUUrHgd AoT_key" >> /home/waggle/.ssh/authorized_keys
chmod 700 /home/waggle/.ssh/
chmod 600 /home/waggle/.ssh/authorized_keys
chown waggle:waggle /home/waggle/.ssh/ /home/waggle/.ssh/authorized_keys


### mark image for first boot 

touch /root/first_boot
ln -s /usr/lib/waggle/waggle_image/waggle_boot.sh /etc/init.d/waggle_boot.sh
update-rc.d waggle_boot.sh defaults

rm -f /etc/network/interfaces.d/*
rm -f /etc/udev/rules.d/70-persistent-net.rules 

### for paranoids
echo > /root/.bash_history
echo > /home/waggle/.bash_history

set +e
# monit accesses /dev/null even after leaving chroot, which makes it impossible unmount the new image
/etc/init.d/monit stop
killall monit
sleep 3


### create report

echo "image created: " > {0}
date >> {0}
echo "" >> {0}
uname -a >> {0}
echo "" >> {0}
cat /etc/os-release >> {0}
dpkg -l >> {0}



'''

# guest node specific code
guestnode_build_script=base_build_init_script + '''\

echo -e "10.31.81.10\tnodecontroller" >> /etc/hosts

apt-get --no-install-recommends install -y network-manager
apt-get autoclean
apt-get autoremove -y




mkdir -p /usr/lib/waggle/

git clone --recursive https://github.com/waggle-sensor/plugin_manager.git

cd /usr/lib/waggle/plugin_manager/
scripts/install_dependencies.sh


'''+base_build_final_script

# node controller specific code
nodecontroller_build_script=base_build_init_script + '''\

echo -e "10.31.81.51\tguestnode1 guestnode" >> /etc/hosts
for i in 2 3 4 5 ; do
  echo -e "10.31.81.5${{i}}\tguestnode${{i}}" >> /etc/hosts
done


echo -e "127.0.0.1\tnodecontroller" >> /etc/hosts

set +e


### get nodecontroller repo
if [ ! -d /usr/lib/waggle/nodecontroller ] ; then
  mkdir -p /usr/lib/waggle/
  git clone --recursive https://github.com/waggle-sensor/nodecontroller.git /usr/lib/waggle/nodecontroller
else  
  cd /usr/lib/waggle/nodecontroller
  git pull
fi

cd /usr/lib/waggle/nodecontroller
./scripts/install_dependencies.sh


### get plugin_manager repo
cd /usr/lib/waggle/
git clone --recursive https://github.com/waggle-sensor/plugin_manager.git
cd /usr/lib/waggle/plugin_manager/
scripts/install_dependencies.sh


'''+base_build_final_script


nodecontroller_etc_network_interfaces_d ='''
# interfaces(5) file used by ifup(8) and ifdown(8)
# created by Waggle autobuild

auto lo eth0
iface lo inet loopback

iface eth0 inet static
        address 10.31.81.10
        netmask 255.255.255.0
        
'''


#set static IP
guest_node_etc_network_interfaces_d = '''\
# interfaces(5) file used by ifup(8) and ifdown(8)
# created by Waggle autobuild

auto lo eth0
iface lo inet loopback

iface eth0 inet static
      address 10.31.81.51
      netmask 255.255.255.0
      #gateway 10.31.81.10

'''





def run_command(cmd, die=1):
    '''
    Will throw exception on execution error.
    '''
    print "execute: %s" % (cmd) 
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception as e:
        print "Error: %s" % (str(e)) 
        if not die:
            return -1
        sys.exit(1)
    if die and child.returncode != 0:
        print "Commmand exited with return code other than zero: %s" % (str(child.returncode)) 
        sys.exit(1)
        
    return child.returncode

def run_command_f(cmd):
    '''
    Execute, wait, ignore error
    '''
    print "execute: %s" % (cmd) 
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception as e:
        pass

def get_output(cmd):
    '''
    Execute, get STDOUT
    '''
    print "execute: %s" % (cmd) 
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]


def write_file(filename, content):
    print "writing file "+filename
    with open(filename, "w") as text_file:
        text_file.write(content)
            

def unmount_mountpoint(mp):
    for i in ['/proc', '/dev', '/sys', '']:
        while int(get_output('mount | grep '+mp+i+' | wc -l')) != 0:
            run_command_f('umount -d '+mp+i)
            time.sleep(3)
    time.sleep(3)
    


def mount_mountpoint(device, mp):
    run_command('mount /dev/loop%dp1 %s' % (device, mp))
    run_command('mount -o bind /proc %s/proc' % (mp))
    run_command('mount -o bind /dev  %s/dev' % (mp))
    run_command('mount -o bind /sys  %s/sys' % (mp))
    time.sleep(3)
    
    
def check_partition():
    run_command('e2fsck -f -y /dev/loop1')
    



def losetup(loopdev, file, offset=0):
    """
    Create single loop device
    """
    offset_option = ''
    
    if offset:
        offset_option = '-o %d ' % (offset)
        
    run_command('losetup %s %s %s' % (offset_option, loopdev, file))
    
    
    

def create_loop_devices(filename, device_number, start_block):
    """
    Create loop devices for complete image and for the root partition
    startblock (optional) is the start of the second partition
    """
    # get partition start position
    #fdisk -lu ${base_image}
    
    loop_device = '/dev/loop'+str(device_number)
    loop_partition_1 = loop_device+'p1' # boot partition
    loop_partition_2 = loop_device+'p2' # data/root partition
    
    if not start_block:
        start_block_str = get_output("fdisk -lu {0} | grep '{0}2' | awk '{{print $2}}'".format(filename))
        start_block=int(start_block_str)
        print "start_block: ", start_block

    offset=start_block*512 
    print "offset: ", offset

    # create loop device for disk
    losetup(loop_device, filename)
    
    time.sleep(1)
    # create loop device for root partition    
    losetup(loop_partition_2, loop_device, offset)
    
    return start_block


def destroy_loop_devices():
    for device in ('/dev/loop0', '/dev/loop1' ):
        for partition in ('p1', 'p2'):
            loop_device = device+partition
            while int(get_output('losetup '+loop_device+' | wc -l')) != 0:
                run_command_f('losetup -d '+loop_device)
                time.sleep(3)



def detect_odroid_model():
    odroid_model_raw=get_output("head -n 1 /media/boot/boot.ini | cut -d '-' -f 1 | tr -d '\n'")
    odroid_model=""
    
    # The XU4 is actually a XU3.
    if odroid_model_raw == "ODROIDXU":
        print "Detected device: %s" % (odroid_model_raw)
        if os.path.isfile('/media/boot/exynos5422-odroidxu3.dtb'):
            odroid_model="odroid-xu3"
            #is_guestnode = 1
        else:
            odroid_model="odroid-xu"
            print "Did not find the XU3/4-specific file /media/boot/exynos5422-odroidxu3.dtb."
            return None
            
    elif odroid_model_raw  == "ODROIDC":
        print "Detected device: %s" % (odroid_model)
        odroid_model="odroid-c1"
    else:
        print "Could not detect ODROID model. (%s)" % (odroid_model)
        return None
    
    return odroid_model
        

##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
    


# clean up first

unmount_mountpoint(0, mount_point_A)

    
time.sleep(3)
destroy_loop_devices()







# install parted
if call('hash partprobe > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y parted')

# install pipeviewer
if call('hash pv > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y pv')



odroid_model = detect_odroid_model()

if not odroid_model:
    sys.exit(1)


if odroid_model == "odroid-xu3":
    is_guestnode = 1




date_today=get_output('date +"%Y%m%d"').rstrip()

if is_guestnode:
    image_type = "guestnode"
else:
    image_type = "nodecontroller"


print "image_type: ", image_type

new_image_prefix="%s/waggle-%s-%s-%s" % (data_directory, image_type, odroid_model, date_today) 
new_image_a="%s.img" % (new_image_prefix)

new_image_b="%s_B.img" % (new_image_prefix)


os.chdir(data_directory)

try:
    base_image = base_images[odroid_model]['filename']
except:
    print "image %s not found" % (odroid_model)
    sys.exit(1)

base_image_xz = base_image + '.xz'

if not os.path.isfile(base_image_xz):
    run_command('wget '+ base_images[odroid_model]['url'] + base_image_xz)
  

if not os.path.isfile(base_image):
    run_command('unxz --keep '+base_image_xz)

 
try:
    os.remove(new_image_a)
except:
    pass

print "Copying file %s to %s ..." % (base_image, new_image_a)
shutil.copyfile(base_image, new_image_a)


#
# LOOP DEVICES HERE
#

start_block = create_loop_devices(new_image_a, 0, None)



time.sleep(3)
print "first filesystem check on /dev/loop1"
check_partition()



print "execute: mkdir -p "+mount_point_A
try: 
    os.mkdir(mount_point_A)
except:
    pass



mount_mountpoint(0, mount_point_A)


# TODO remove this test
unmount_mountpoint(0, mount_point_A)
time.sleep(3)
destroy_loop_devices()
time.sleep(2)
create_loop_devices(new_image_a, 0, start_block)
print "filesystem check on /dev/loop1 after first mount"
check_partition()



mount_mountpoint(0, mount_point_A)



if is_guestnode:
    local_build_script = guestnode_build_script.format(report_file)
else: 
    local_build_script = nodecontroller_build_script.format(report_file)
    
    
write_file( mount_point_A+'/root/build_image.sh',  local_build_script)

print "-------------------------\n"
print local_build_script
print "-------------------------\n"

run_command('chmod +x %s/root/build_image.sh' % (mount_point_A))

#
# CHROOT HERE
#

print "################### start of chroot ###################"

run_command('chroot %s/ /bin/bash /root/build_image.sh' % (mount_point_A))


print "################### end of chroot ###################"


# 
# After changeroot
#
try:
    os.remove(new_image_a+'.report.txt')
except:
    pass

print "copy: ", mount_point_A+'/'+report_file, new_image_a+'.report.txt'
shutil.copyfile(mount_point_A+'/'+report_file, new_image_a+'.report.txt')





if is_guestnode:
    write_file(mount_point_A+'/etc/network/interfaces', guest_node_etc_network_interfaces_d)
else:
    write_file(mount_point_A+'/etc/network/interfaces', nodecontroller_etc_network_interfaces_d)






old_partition_size_kb=int(get_output('df -BK --output=size /dev/loop1 | tail -n 1 | grep -o "[0-9]\+"'))
print "old_partition_size_kb: ", old_partition_size_kb


unmount_mountpoint(0, mount_point_A)
time.sleep(3)
destroy_loop_devices()
time.sleep(3)
create_loop_devices(new_image_a, 0, start_block)
time.sleep(3)
print "filesystem check on /dev/loop1 after chroot"
check_partition()

time.sleep(3)


estimated_fs_size_blocks=int(get_output('resize2fs -P /dev/loop1 | grep -o "[0-9]*"') )

block_size=int(get_output('blockdev --getbsz /dev/loop1'))

estimated_fs_size_kb = estimated_fs_size_blocks*block_size/1024


# add 500MB
new_partition_size_kb = estimated_fs_size_kb + (1024*500)


# add 100MB
new_fs_size_kb = estimated_fs_size_kb + (1024*100)

# verify partition:
run_command('e2fsck -f -y /dev/loop1')


sector_size=int(get_output('fdisk -lu {0} | grep "Sector size" | grep -o ": [0-9]*" | grep -o "[0-9]*"'.format(new_image_a)))


front_size_kb = sector_size * start_block/ 1024

if new_partition_size_kb < old_partition_size_kb: 

    print "new_partition_size_kb is smaller than old_partition_size_kb"

    # shrink filesystem (that does not shrink the partition!)
    run_command('resize2fs -p /dev/loop1 %sK' % (new_fs_size_kb))


    run_command('partprobe  /dev/loop1')

    time.sleep(3)

    ### fdisk (shrink partition)
    # fdisk: (d)elete partition 2 ; (c)reate new partiton 2 ; specify start position and size of new partiton
  
    run_command('echo -e "d\n2\nn\np\n2\n%d\n+%dK\nw\n" | fdisk %s' % (start_block, new_partition_size_kb, new_image_a))
  


    run_command('partprobe /dev/loop1')

    #set +e
    #resize2fs /dev/loop1
    #set -e

    # does not show the new size
    #fdisk -lu ${new_image_a}

    # shows the new size (-b for bytes)
    #partx --show /dev/loop1 (fails)

    time.sleep(3)

    run_command('e2fsck -n -f /dev/loop1')

    #e2fsck_ok=1
    #set +e
    #while [ ${e2fsck_ok} != "0" ] ; do
    #  e2fsck -f /dev/loop1
    #  e2fsck_ok=$?
    #  sleep 2
    #done
    #set -e

else:
    print "new_partition_size_kb is NOT smaller than old_partition_size_kb"

destroy_loop_devices()




# add size of boot partition

combined_size_kb = new_partition_size_kb+front_size_kb
combined_size_bytes = (new_partition_size_kb + front_size_kb) * 1024

# from kb to mb
blocks_to_write = combined_size_kb/1024


# write image to file
run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_a))

new_image_a_compressed = new_image_a+'.xz'

try:
    os.remove(new_image_a_compressed)
except:
    pass
    
os.rename(new_image_a+'.xz_part',  new_image_a_compressed)




# create second dd with different UUIDs
if create_b_image:
    
    
    if not os.path.isfile(change_partition_uuid_script):
        print change_partition_uuid_script, " not found"
        sys.exit(1)
    
    #copy image b (from a)
    run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d  > %s.part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_b))
    
    try:
        os.remove(new_image_b)
    except:
        pass
    
    os.rename(new_image_b+'.part',  new_image_b)
    
    # create loop device
    create_loop_devices(new_image_b, 1)
    
    # change UUID
    run_command(change_partition_uuid_script+ ' /dev/loop1')
    
    
    # the recovery image on the eMMC needs space:
    
    new_image_a_compressed_size = os.path.getsize(new_image_a_compressed)
    new_image_a_compressed_size_mb = new_image_a_compressed_size / 1048576
    
    # increase partition size again
    run_command('dd if=/dev/zero bs=1MiB of={} conv=notrunc oflag=append count={}'.format(new_image_b, new_image_a_compressed_size_mb+50))
    
    
    # make filesystem use new space
    run_command('resize2fs /dev/loop1p2')
    
    
    # mount
    mount_mountpoint(1, mount_point_B)
    
    
    # copy SD-card image into eMMC as a backup
    shutil.copyfile(new_image_a+'.xz', mount_point_B+'/root/')

    # umount
    unmount_mountpoint(mount_point_B)
    
    
    try:
        os.remove(new_image_b+'.xz')
    except:
        pass
    
    # compress 
    run_command('xz -1 '+new_image_b)
    
    
    #run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_b))
    #os.rename(new_image_b+'.xz_part',  new_image_b+'.xz')    



if os.path.isfile( data_directory+ '/waggle-id_rsa'):
    scp_target = 'waggle@terra.mcs.anl.gov:/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images'
    run_command('md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(new_image_a) ) 
    run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(data_directory, new_image_a, scp_target))
  
    if os.path.isfile( new_image_b+'.xz'):
        # upload second image with different UUID's
        run_command( 'md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(new_image_b))
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(data_directory, new_image_b, scp_target))

  
    if os.path.isfile( new_image_a+'.report.txt'): 
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(data_directory, new_image_a,scp_target))
      
  
    if os.path.isfile( new_image_a+'.build_log.txt'): 
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(data_directory, new_image_a,scp_target))
      
  

