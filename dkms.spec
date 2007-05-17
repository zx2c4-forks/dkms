Summary: Dynamic Kernel Module Support Framework
Name: dkms
Version: 2.0.0
Release: 1
Vendor: Dell Computer Corporation
License: GPL
Packager: Gary Lerhaupt <gary_lerhaupt@dell.com>
Group: System Environment/Base
BuildArch: noarch
Requires: sed gawk findutils modutils tar cpio gzip grep mktemp
Requires: bash > 1.99
Provides: dkms-minimal
Source: dkms-%version.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root/

%description
This package contains the framework for the Dynamic
Kernel Module Support (DKMS) method for installing
module RPMS as originally developed by the Dell
Computer Corporation.

%prep

%setup -q

%triggerpostun -- dkms < 1.90.00-1
for dir in `find /var/dkms -type d -maxdepth 1 -mindepth 1`; do
	mv -f $dir /var/lib/dkms
done
[ -e /etc/dkms_framework.conf ] && ! [ -e /etc/dkms/framework.conf ] && mkdir /etc/dkms && cp /etc/dkms_framework.conf /etc/dkms/framework.conf
arch_used=""
[ `uname -m` == "x86_64" ] && [ `cat /proc/cpuinfo | grep -c "Intel"` -gt 0 ] && [ `ls /lib/modules/`uname -r`/build/configs 2>/dev/null | grep -c "ia32e"` -gt 0 ] && arch_used="ia32e" || arch_used=`uname -m`
echo ""
echo "ALERT! ALERT! ALERT!"
echo ""
echo "You are using a version of DKMS which does not support multiple system"
echo "architectures.  Your DKMS tree will now be modified to add this support."
echo ""
echo "The upgrade will assume all built modules are for arch: $arch_used"
current_kernel=`uname -r`
dkms_tree="/var/lib/dkms"
source_tree="/usr/src"
tmp_location="/tmp"
dkms_frameworkconf="/etc/dkms/framework.conf"
. $dkms_frameworkconf 2>/dev/null
echo ""
echo "Fixing directories."
for directory in `find $dkms_tree -type d -name "module" -mindepth 3 -maxdepth 4`; do
	dir_to_fix=`echo $directory | sed 's#/module$##'`
	echo "Creating $dir_to_fix/$arch_used..."
	mkdir $dir_to_fix/$arch_used
	mv -f $dir_to_fix/* $dir_to_fix/$arch_used 2>/dev/null 
done
echo ""
echo "Fixing symlinks."	
for symlink in `find $dkms_tree -type l -name "kernel*" -mindepth 2 -maxdepth 2`; do
	symlink_kernelname=`echo $symlink | sed 's#.*/kernel-##'`
	dir_of_symlink=`echo $symlink | sed 's#/kernel-.*$##'`
	cd $dir_of_symlink
        read_link="$symlink"
        while [ -L "$read_link" ]; do
            read_link=`ls -l $read_link | sed 's/.*-> //'`
        done
	if [ `echo $read_link | sed 's#/# #g' | wc -w | awk {'print $1'}` -lt 3 ]; then
		echo "Updating $symlink..."
		ln -sf $read_link/$arch_used kernel-$symlink_kernelname-$arch_used
		rm -f $symlink
	fi
	cd -
done
echo ""

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
        rm -rf $RPM_BUILD_ROOT
fi
mkdir -p $RPM_BUILD_ROOT/{var/lib/dkms,/usr/sbin,usr/share/man/man8,etc/init.d,etc/dkms}
install -m 755 dkms $RPM_BUILD_ROOT/usr/sbin/dkms
install -m 644 dkms.8.gz $RPM_BUILD_ROOT/usr/share/man/man8
install -m 644 dkms_framework.conf  $RPM_BUILD_ROOT/etc/dkms/framework.conf
install -m 644 template-dkms-mkrpm.spec $RPM_BUILD_ROOT/etc/dkms
install -m 644 dkms_dbversion $RPM_BUILD_ROOT/var/lib/dkms/dkms_dbversion
install -m 755 dkms_autoinstaller $RPM_BUILD_ROOT/etc/init.d/dkms_autoinstaller
install -m 755 dkms_mkkerneldoth $RPM_BUILD_ROOT/usr/sbin/dkms_mkkerneldoth

%clean 
if [ "$RPM_BUILD_ROOT" != "/" ]; then
        rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root)
%attr(0755,root,root) /usr/sbin/dkms
%attr(0755,root,root) /var/lib/dkms
%attr(0755,root,root) /etc/init.d/dkms_autoinstaller
%attr(0755,root,root) /usr/sbin/dkms_mkkerneldoth
%doc %attr(0644,root,root) /usr/share/man/man8/dkms.8.gz
%doc %attr (-,root,root) sample.spec sample.conf AUTHORS COPYING
%config(noreplace) /etc/dkms/framework.conf
%config(noreplace) /etc/dkms/template-dkms-mkrpm.spec

%post
[ -e /sbin/dkms ] && mv -f /sbin/dkms /sbin/dkms.old 2>/dev/null
/sbin/chkconfig dkms_autoinstaller on


%changelog
* Thu Aug 26 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 2.0.0-1
- Output to stderr is now >> and not >
- Added kludge to allow redhat1 driver disks with BOOT kernel modules
- Allow cross arch building on 2.6 if --kernelsourcedir is passed
- Generic make commands now respect --kernelsourcedir
- Bumped dkms_dbversion to 2.0.0

* Thu Aug 19 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.96.02-1
- Fixed suse driver disks for i386

* Thu Aug 12 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.96.01-1
- Look for /etc/SuSEconfig also to know if its a SuSE box
- If no make command, set the clean command

* Wed Aug 11 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.32-1
- Added suse mkdriverdisk support
- Updated man page

* Tue Aug 10 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.25-1
- Added provides: dkms-minimal for Mandrake
- Added -r, --release for use in SuSE driver disks

* Fri Aug 06 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.24-1
- Fixed kernelsourcedir error message.
- dkms_autoinstaller now excepts a kernel parameter

* Tue Jul 27 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.19-1
- Created a set_kernel_source_dir function to remove dup code

* Mon Jul 26 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.18-1
- Added John Hull's SuSE support patches (mkinitrd, config prep)

* Fri Jul 23 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.11-1
- Split modulesconf_modify to separate add and remove functions
- Added support for /etc/modprobe.conf

* Thu Jul 15 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.10-1
- Remove coreutils as a dependency to avoid RH21 error.

* Wed Jul 14 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.09-1
- DKMS ldtarball now check dbversion and wont load future tarballs

* Mon Jul 12 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.95.06-1
- Buchan Milne's Mandrake prep support patch
- Buchan Milne's macro additions to template-dkms-mkrpm.spec
- Buchan Milne's typo corrections in mkrpm
- Buchan Milne's change to how mkrpm works (mktarball happen in rpm prep)

* Tue Jul 06 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.94.16-1
- Added a dependency on modutils for usage of modinfo
- Added version sanity check
- dkms_autoinstaller now check for sanity of version
- Changed conversion algorithm for /var/dkms to /var/lib/dkms
- Changed all warning to get to stderr
- set_module_suffix doesn't use version_checker because its too slow

* Thu Jul 01 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.94.06-1
- Reworked version checking to handle non-digit characters
- Added coreutils as a dependency
- Create a tempdir in mkdriverdisk, whoops (thanks Charles Duffy)

* Wed Jun 30 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.94.03-1
- dkms_dbversion belongs in /var/lib/dkms (thanks Thomas Palmieri)
- Added a version checking subroutine
- Removed gt2dot4 variable in favor of kernel version checking
- MAKE is no longer required.  If none specified, it uses a default.

* Thu Jun 24 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.94.01-1
- Buchan Milne's optimization of the arch detection code

* Wed Jun 23 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.93.14-1
- Fixed bug when find finds more than one thing (thanks Paul Howarth)
- Changed arch detection code to first try RPM which always will get it right (thanks Vladimir Simonov)

* Tue Jun 22 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.93.12-1
- Initial mkrpm is working
- Added --source-only option to mktarball
- mkrpm handles --source-only
- Updated manpage

* Fri Jun 17 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.93.04-1
- Started adding mkrpm

* Wed Jun 16 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.93.01-1
- Fixed dkms_autoinstaller bugs (thanks Vladimir Simonov)
- Fixed paths in the tarball's install.sh

* Tue Jun 15 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.33-1
- kernelver/arch handling for mktarball

* Mon Jun 14 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.26-1
- Added support for RH v2 driver disks (they support multiple arches)

* Fri Jun 11 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.24-1
- Continue rework of kernelver/arch handling
- Added PATH fix (thanks Andrey Ulanov <andrey.ulanov@acronis.com>)
- config_contents should not be local (thanks Andrey Ulanov)
- If no config in /configs, just use .config (thanks Andrey Ulanov)
- match now pays attention to --kernelsourcedir

* Wed Jun 09 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.06-1
- Started coding new kernelver arch CLI handling

* Mon Jun 07 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.04-1
- Added STRIP[] directive.  By default dkms now runs strip -g on all built modules.
- Fix set_module_suffix in dkms build
- Changed /etc/dkms_framework.conf to /etc/dkms/framework.conf
- Added reload into dkms_autoinstaller to limit Mandrake error messages
- Moved /var/dkms to /var/lib/dkms !!!!!!!!!!!!!!!!

* Fri Jun 04 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.92.01-1
- PRE_BUILD, POST_BUILD, POST_ADD, etc all now allow their scripts to accept parameters

* Thu Jun 03 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.18-1
- Added --installtree option to specify different install location besides /lib/modules
- Took Charles Duffy's advice and removed brackets on error messages

* Wed Jun 02 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.14-1
- Added set_module_suffix function

* Tue Jun 01 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.12-1
- Added a PRE_BUILD dkms.conf directive.

* Thu May 27 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.11-1
- Added build time check for gcc and make if there is a build failure
- You can now specify --archive to mktarball to control the naming of the made tarball (thanks Vladimir Simonov)

* Wed May 26 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.07-1
- Removed rpm dependency on gcc (thanks Vladimir Simonov)
- Re-implemented dkms status recursively

* Mon May 24 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.91.01-1
- Added local variable declarations to local variables

* Fri May 21 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.46-1
- Vladimir Simonov's invoke_command improvements for keeping /tmp clean

* Thu May 20 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.45-1
- Pass --targetarch to dkms_mkkerneldoth (thanks to Vladimir Simonov <validimir.simonov@acronis.com>)
- Moved arch detection into a function called detect_arch

* Wed May 19 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.44-1
- Bug fixes on arch support
- Updated man page

* Tue May 18 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.32-1
- Completing arch awareness and transition scripts
- Created upgrade_dkms_archify.sh to update DKMS trees for arch support

* Mon May 17 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.06-1
- Continued adding arch awareness

* Thu May 13 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.90.01-1
- Started adding arch awareness into the DKMS tree

* Fri May 07 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.10-1
- bumped the revision

* Thu May 06 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.09.21-1
- Improved readability of install and uninstall text to the screen
- You can now specify multiple actions in the same command

* Wed May 05 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.09.05-1
- Added arch_used as part of the filename of a tarball created by mktarball
- If multiple original modules exist in a single kernel, the one in /updates is preferred
- Changed multiple original module handling to move out and store all collisions

* Mon May 03 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.09.01-1
- Changed 2.6 prep prepare-all target usage to make modules_prepare
- Changed 2.6 make command to always use M= as this is fixed in 2.6.6-rc3-bk5

* Fri Apr 30 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.09-1
- If module build exit status is bad, die accordingly
- 2.6 kernel prep changes (not quite there yet, still broken)

* Thu Apr 29 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.08.06-1
- Added BUILD_EXCLUSIVE_KERNEL & BUILD_EXCLUSIVE_ARCH directives for dkms.conf
- Tweaked dkms_autoinstaller to more gracefully handle a build failure

* Tue Apr 27 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.08.02-1
- Got rid of make clean warning if not present

* Tue Apr 20 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.08.01-1
- Fixed error message when compiling with --no-prepare-kernel

* Tue Apr 13 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.08-1
- Fixed the format of rhdd-6.1 for Red Hat driver disks
- Update man page with new white paper info

* Thu Apr 1 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.07-1
- Added work-around to recognize ia32e kernel config instead of x86_64
- Got rid of start and stop functions which were no-ops anyway

* Thu Mar 25 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.06-1
- Added a fix to keep the driver disk filename from being so long that it breaks

* Mon Feb 09 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.05-1
- Added a fix to resolve RHEL21 depmod errors when an obsolete reference is found

* Thu Jan 15 2004 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.02-1
- Fixed mkinitrd for ia64

* Tue Dec 09 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.00.01-1
- Fixed /usr/share/doc/dkms-<version> mode to 755

* Mon Dec 01 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 1.00-1
- Bumped version to 1.00

* Mon Nov 24 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.99.02-1
- Add -t vfat to loopback mount during creation of driver disk

* Fri Nov 21 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.99.01-1
- Only edit /etc/modules.conf if remake_initrd is set or if this is the last uninstall and no original module exists
- Added MODULES_CONF_OBSOLETE_ONLY array directive in dkms.conf
- Updated man page

* Wed Nov 19 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.46.05-1
- Fixed a bug in mktarball to limit the tarball name to less than 255 chars

* Tue Nov 18 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.46.04-1
- Binary only tarballs now contain a copy of dkms.conf so that they can be force loaded

* Mon Nov 17 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.45.03-1
- Updated man page, recommended rpm naming: <module>-<version>-<rpmversion>dkms.noarch.rpm

* Thu Nov 13 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.45.02-1
- dkms_autoinstaller is now installed to /etc/init.d for cross-distro happiness

* Fri Nov 07 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.45.01-1
- Added kernel config prepping for hugemem kernel (thanks Amit Bhutani)
- modules.conf only now gets changed during install or uninstall of active module

* Tue Nov 03 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.44.05-1
- Changed MODULES_CONF_ALIAS_TYPE to an array in dkms.conf
- Added MODULES_CONF_OBSOLETES array in dkms.conf
- Reworked modules_conf_modify to make use of OBSOLETES logic
- Updated man page

* Fri Oct 31 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.42.03-1
- Added --binaries-only option to mktarball
- Updated man page

* Thu Oct 30 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.41.15-1
- If depmod or mkinitrd fail during install, automatically go back to built state
- Warn heavily if mkinitrd fails during uninstall

* Wed Oct 29 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.41.11-1
- Removed paths from dkms calls in sample.spec
- Fixed typo of KERNELRELEASE

* Wed Oct 29 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.41.10-1
- Added Red Hat specific kernel prep to avoid make dep (Thanks Matt Domsch)
- Added dkms_mkkerneldoth script to support RH kernel prep
- Moved dkms from /sbin/ to /usr/sbin
- Fixed typo which caused original_module not to get replaced on uninstall
- No longer edit Makefiles, just specify KERNELVERSION=$kernel_version on the command line
- Removed unnecessary depmod during uninstall

* Thu Oct 23 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.16-1
- Fixed mkdriverdisk to copy rhdd-6.1 file into driver disk image

* Wed Oct 22 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.15-1
- Changed expected driver disk filename from module-info to modinfo to work on legacy RH OSs

* Tue Oct 14 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.14-1
- Unset all arrays before using them.  duh.

* Tue Oct 07 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.12-1
- Fixed bug in autoinstaller where it wasn't looking for dkms.conf through source symlink

* Thu Oct 02 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.11-1
- Added --rpm_safe_upgrade flag
- Updated the man page and sample.spec

* Wed Oct 01 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.40.05-1
- No longer copy dkms.conf into /var/dkms tree, just go to the source_tree so as to reduce duplication
- Got rid of --post-add, --post-build, --post-install and --post-remove
- Replaced the above with DKMS directives POST_ADD, POST_BUILD, POST_INSTALL, POST_REMOVE
- Fixed ldtarball and mktarball to no longer look for these duplicate files
- Added a sample.conf for /usr/share/doc
- Updated dkms_dbversion to 1.01 from 1.00 due to these changes
- Update the man page

* Tue Sep 30 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.39.17-1
- Added diff checking in status command in case modules are overwritten by someone else
- Fixed already built error message in build_module
- Changed build-arch to noarch
- Updated sample.spec
- Change dest_module_location to not get prefaced by /lib/modules/$kernel_version
- When saving old initrd, copy it instead of moving it in case new one doesn't build
- Only create source symlink during loadtarball if --force or if it doesn't exist
- Decide to completely remove during remove_module after doing find with maxdepth of 0 not 1

* Mon Sep 29 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.39.08-1
- Reworked mktarball format to remove dependence on /var/dkms and /usr/src
- Reworked ldtarball to match new tarball format
- Ldtarball now uses --archive=tarball-location flag instead of --config flag
- Ldtarball can now load any old source tarball as long as it contains a good dkms.conf
- Added --kernelsourcedir cli option to provide alternate location for kernel source
- Driver disk files are now looked for in /redhat_driver_disk
- Added $tmp_location specifiable in /etc/dkms_framework.conf to specify your /tmp dir (default /tmp)
- Updated man page

* Thu Sep 25 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.38.03-1
- Fixed tmp_dir_name typo in ldtarball
- Fixed mkdriverdisk to correctly create kernel/module structure
- Don't expect a rhdd-6.1 file for RH driver disk, dkms will create it
- Remove mkdriverdisk warning on non BOOT kernels
- Moved driver_disk directory location to underneath $module_version
- mkdriverdisk can now accept multiple kernel versions
- Updated man page with info about $dkms_tree and $source_tree as dkms.conf variables

* Wed Sep 24 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.37.10-1
- Don't allow installs of modules onto non-existant kernels
- Suppressed stderr on some commands
- Fixed brain-dead bug for REMAKE INITRD
- During uninstall, dont remake initrd if it was not installed
- ldtarball into unique tempdir and delete it when finished

* Tue Sep 23 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.37.04-1
- Changed PATCH to array based system (added PATCH_MATCH array)
- PATCHes can now be matched against regular expressions, not just substrings
- Changed MODULES_CONF to array based system
- CHANGED MAKE to array based system (added MAKE_MATCH array)
- MAKEs can now be matched against regular expressions, not just substrings.
- Updated man page

* Mon Sep 22 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.36.10-1
- Changed autoinstaller bootup priority from 08 to 04
- Changed invoke_command routine to use mktemp for better security
- Changed invoke_command in dkms_autoinstaller too

* Fri Sep 19 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.36.05-1
- Continued bug testing and fixing new features

* Wed Sep 17 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.36.02-1
- Got rid of MODULE_NAME: replaced with BUILT_MODULE_NAME, DEST_MODULE_NAME arrays
- Got rid of LOCATION: replaced with BUILT_MODULE_LOCATION, DEST_MODULE_LOCATION arrays
- Update man page

* Tue Sep 16 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.36.01-1
- Fixed the setting of the gt2dot4 variable

* Wed Sep 10 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.35.02-1
- Added PACKAGE_NAME, PACKAGE_VERSION requirements to dkms.conf for gmodconfig use
- Fixed creation of /var/dkms before cp of dkms_dbversion in install.sh

* Mon Sep 08 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.34.10-1
- Continued adding autoinstall stuff
- Updated man page

* Fri Sep 05 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.34.01-1
- Added dkms_autoinstaller service (builds module on boot if AUTOINSTALL="yes" in dkms.conf)
- DKMS usage no longer sent to std_err
- Added --no-prepare-kernel cli option

* Fri Aug 08 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.33.02-1
- Fixed quote bugs in match (Reported by: John Hull <john_hull@dell.com>) 
- Added Fred Treasure to the AUTHORS list
- Added dkms_dbversion file to DKMS tree to track architecture of dkms db layout

* Thu Jul 03 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.32.04-1
- Added mkinitrd support for SuSE (etc_sysconfig_kernel_modify)
- Added generic make command for kernel >2.4 (make -C <path-to-kernel-source> SUBDIRS=<build dir> modules)
- Fixed kernel prepare to do Red Hat/Generic by default
- Only do make dep if < 2.5

* Tue Jun 03 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.31.04-1
- Modified the Red Hat prep routine to be smaller and more robust (including summit support)
- Added sample.spec to the sources for /usr/share/doc
- If you save a .config before make mrproper, return it right afterwards
- Updated the man page

* Fri May 30 2003 Gary Lerhaupt <gary_lerahupt@dell.com> 0.30.17-1
- Added a remake_initrd function to keep SuSE from doing wrong things
- If you know the correct right steps for rebuilding SuSE initrds, please let me know!
- Updated man page

* Thu May 29 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.30.15-1
- Added a native readlink function to make sure it exists
- Added a mkdir -p to $location to make sure it exists
- Added --directive

* Wed May 28 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.30.05-1
- Added kernel preparation support for SLES/United Linux (Many thanks to: Fred Treasure <fwtreas@us.ibm.com>)

* Tue May 20 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.29.09-1
- On remove, to remove all kernel versions you must now specify --all
- Added grep, cpio and gzip to the Requires of the RPM
- Added cleaning kernel tree (make mrproper) after last build completes
- Before prepare kernel, the current .config is stored in memory to be restored later
- Added a verbose warning to the status command to remind people it only shows DKMS modules
- Added /etc/dkms_framwork.conf for controlling source_tree and dkms_tree
- Added the undocumented --dkmstree and --sourcetree options for cli control of these vars
- When looking for original modules, dkms now employs the find command to expand search past $location
- Updated man page

* Wed May 14 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.28.05-1
- Fixed a typo in the man page.

* Tue May 05 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.28.04-1
- Fixed ldtarball/mktarball to obey source_tree & dkms_tree (Reported By: Jordan Hargrave <jordan_hargrave@dell.com>)
- Added DKMS mailing list to man page

* Tue Apr 29 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.27.05-1
- Changed NEEDED_FOR_BOOT to REMAKE_INITRD as this makes more sense
- Redid handling of modifying modules.conf 
- Added MODULE_CONF_ALIAS_TYPE to specs

* Mon Apr 28 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.26.12-1
- Started adding ldtarball support
- added the --force option
- Update man page

* Thu Apr 24 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.26.05-1
- Started adding mktarball support
- Fixed up the spec file to use the tarball

* Tue Mar 25 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.25.14-1
- Continued integrating mkdriverdisk
- Updated man page

* Mon Mar 24 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.25.03-1
- Added renaming ability to modules after builds (MODULE_NAME="beforename.o:aftername.o")
- Started adding mkdriverdisk support
- Added distro parameter for use with mkdriverdisk
- Now using readlink to determine symlink pointing location
- Added redhat BOOT config to default location of config files
- Fixed a bug in read_conf that caused the wrong make subdirective to be used
- Remove root requirement for build action

* Wed Mar 19 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.23.19-1
- Fixed archiving of original modules (Reported by: Kris Jordan <kris@sagebrushnetworks.com>)

* Wed Mar 12 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.23.18-1
- Added kernel specific patching ability

* Mon Mar 10 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.23.16-1
- Removed the sourcing in of /etc/init.d/functions as it was unused anyway
- Implemented generic patching support
- Updated man page
- Fixed timing of the creation of DKMS built infrastructure in case of failure

* Fri Mar 07 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.23.11-1
- Builds now occur in /var/dkms/$module/$module_version/build and not in /usr/src
- Fixed the logging of the kernel_config

* Thu Mar 06 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.23.01-1
- Started adding patch support
- Redid reading implementation of modules_conf entries in dkms.conf (now supports more than 5)
- Updated man page

* Tue Mar 04 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.22.06-1
- Module names are not just assumed to end in .o any longer (you must specify full module name)
- At exit status to invoke_command when bad exit status is returned

* Fri Feb 28 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.22.03-1
- Changed the way variables are handled in dkms.conf, %kernelver to $kernelver

* Mon Feb 24 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.22.02-1
- Fixed a typo in install

* Tue Feb 11 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.22.01-1
- Fixed bug in remove which made it too greedy
- Updated match code

* Mon Feb 10 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.21.16-1
- Added uninstall action
- Updated man page

* Fri Feb 07 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.20.06-1
- Added --config option to specify where alternate .config location exists
- Updated the man page to indicate the new option.
- Updated the spec to allow for software versioning printout
- Added -V which prints out the current dkms version and exits

* Thu Jan 09 2003 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.19.01-1
- Added GPL stuffs

* Mon Dec 09 2002 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.18.04-1
- Added support for multiple modules within the same install
- Added postadd and fixed up the man page

* Fri Dec 06 2002 Gary Lerhaupt <gary_lerhaupt@dell.com> 0.17.01-1
- Cleaned up the spec file.

* Fri Nov 22 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Fixed a bug in finding MAKE subdirectives

* Thu Nov 21 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Fixed make.log path error when module make fails
- Fixed invoke_command to work under RH8.0
- DKMS now edits kernel makefile to get around RH8.0 problems

* Wed Nov 20 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Reworked the implementation of -q, --quiet

* Tue Nov 19 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Version 0.16: added man page

* Mon Nov 18 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Version 0.13: added match option
- Version 0.14: dkms is no longer a SysV service
- Added depmod after install and remove
- Version 0.15: added MODULES_CONF directives in dkms.conf

* Fri Nov 15 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Version 0.12: added the -q (quiet) option

* Thu Nov 14 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Version 0.11: began coding the status function

* Wed Nov 13 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Changed the name to DKMS
- Moved original_module to its own separate directory structure
- Removal now does a complete clean up

* Mon Nov 11 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Split build into build and install
- dkds.conf is now sourced in
- added kernelver variable to dkds.conf

* Fri Nov 8 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Added date to make.log
- Created the prepare_kernel function

* Thu Nov 7 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Barebones implementation complete

* Wed Oct 30 2002 Gary Lerhaupt <gary_lerhaupt@dell.com>
- Initial coding
