Name: kexec-tools
Version: 2.0.4
Release: 2
License: GPLv2
Group: System/Configuration/Hardware
Summary: The kexec/kdump userspace component
Url:	 https://kernel.org/pub/linux/utils/kernel/kexec
Source0: http://kernel.org/pub/linux/utils/kernel/kexec/%{name}-%{version}.tar.bz2
Source1: kdumpctl
Source2: kdump.sysconfig
Source3: kdump.sysconfig.x86_64
Source4: kdump.sysconfig.i386
Source5: kdump.sysconfig.ppc64
Source6: kdump.sysconfig.ia64
Source7: mkdumprd
Source8: kdump.conf
Source9: http://downloads.sourceforge.net/project/makedumpfile/makedumpfile/1.4.2/makedumpfile-1.4.2.tar.gz
Source10: kexec-kdump-howto.txt
Source11: firstboot_kdump.py
Source12: mkdumprd.8
Source13: kexec-tools-po.tar.gz
Source14: 98-kexec.rules
Source15: kdump.conf.5
Source16: kdump.service

#######################################
# These are sources for mkdumpramfs
# Which is currently in development
#######################################
Source100: dracut-files.tbz2

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(pre): coreutils sed zlib 
Requires: busybox >= 1.2.0, dracut
BuildRequires: dash 
BuildRequires: zlib-devel elfutils-devel bzip2-devel
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig intltool gettext 
BuildRequires: systemd-units elfutils-static-devel
%ifarch %{ix86} x86_64 ppc64 ia64 ppc
Obsoletes: diskdumputils netdump
%endif
Patch601: kexec-tools-2.0.3-disable-kexec-test.patch

%description
kexec-tools provides /sbin/kexec binary that facilitates a new
kernel to boot using the kernel's kexec feature either on a
normal or a panic reboot. This package contains the /sbin/kexec
binary and ancillary utilities that together form the userspace
component of the kernel's kexec feature.

%prep
%setup -q 

mkdir -p -m755 kcp
tar -z -x -v -f %{SOURCE9}

%patch601 -p1

tar -z -x -v -f %{SOURCE13}

%build

%configure \
    --sbindir=/sbin
rm -f kexec-tools.spec.in
# setup the docs
cp %{SOURCE10} . 

make
%ifarch %{ix86} x86_64 ia64 ppc64
make -C makedumpfile-1.4.2 LINKTYPE=dynamic
%endif
make -C kexec-tools-po

%install
%makeinstall_std
mkdir -p -m755 %buildroot%{_sysconfdir}/sysconfig
mkdir -p -m755 %buildroot%{_localstatedir}/crash
mkdir -p -m755 %buildroot%{_mandir}/man8/
mkdir -p -m755 %buildroot%{_mandir}/man5/
mkdir -p -m755 %buildroot%{_docdir}
mkdir -p -m755 %buildroot%{_datadir}/kdump
mkdir -p -m755 %buildroot%{_sysconfdir}/udev/rules.d
mkdir -p %buildroot%{_unitdir}
mkdir -p -m755 %buildroot%{_bindir}
install -m 755 %{SOURCE1} %buildroot%{_bindir}/kdumpctl

%ifarch x86_64
%define SYSCONFIG %SOURCE3
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE3
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE2
%else

%ifarch %{ix86}
%define SYSCONFIG %SOURCE4
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE4
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE2
%else

%ifarch ppc64
%define SYSCONFIG %SOURCE5
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE5
[ -f $SYSCONFIG ] || SYSCONFIG=%SOURCE2
%else
%endif
%endif
%endif

install -m 644 %{SYSCONFIG} %buildroot%{_sysconfdir}/sysconfig/kdump


install -m 755 %{SOURCE7} %buildroot/sbin/mkdumprd
install -m 644 %{SOURCE8} %buildroot%{_sysconfdir}/kdump.conf
install -m 644 kexec/kexec.8 %buildroot%{_mandir}/man8/kexec.8
install -m 755 %{SOURCE11} %buildroot%{_datadir}/kdump/firstboot_kdump.py
install -m 644 %{SOURCE12} %buildroot%{_mandir}/man8/mkdumprd.8
install -m 644 %{SOURCE14} %buildroot%{_sysconfdir}/udev/rules.d/98-kexec.rules
install -m 644 %{SOURCE15} %buildroot%{_mandir}/man5/kdump.conf.5
install -m 644 %{SOURCE16} %buildroot%{_unitdir}/kdump.service

%ifarch %{ix86} x86_64 ia64 ppc64
install -m 755 makedumpfile-1.4.2/makedumpfile %buildroot/sbin/makedumpfile
install -m 644 makedumpfile-1.4.2/makedumpfile.8.gz %buildroot/%{_mandir}/man8/makedumpfile.8.gz
%endif
make -C kexec-tools-po install DESTDIR=%buildroot
%find_lang %{name}


# untar the dracut package
mkdir -p -m755 %buildroot/etc/kdump-adv-conf
tar -C %buildroot/etc/kdump-adv-conf -jxvf %{SOURCE100}
chmod 755 %buildroot/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/module-setup.sh
chmod 755 %buildroot/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/kdump.sh


%define dracutlibdir %{_prefix}/lib/dracut
#and move the custom dracut modules to the dracut directory
mkdir -p %buildroot/%{dracutlibdir}/modules.d/
mv %buildroot/etc/kdump-adv-conf/kdump_dracut_modules/* %buildroot/%{dracutlibdir}/modules.d/

%post
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
touch /etc/kdump.conf
# This portion of the script is temporary.  Its only here
# to fix up broken boxes that require special settings 
# in /etc/sysconfig/kdump.  It will be removed when 
# These systems are fixed.

if [ -d /proc/bus/mckinley ]
then
	# This is for HP zx1 machines
	# They require machvec=dig on the kernel command line
	sed -e's/\(^KDUMP_COMMANDLINE_APPEND.*\)\("$\)/\1 machvec=dig"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
elif [ -d /proc/sgi_sn ]
then
	# This is for SGI SN boxes
	# They require the --noio option to kexec 
	# since they don't support legacy io
	sed -e's/\(^KEXEC_ARGS.*\)\("$\)/\1 --noio"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
fi


%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart kdump.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable kdump.service > /dev/null 2>&1 || :
    /bin/systemctl stop kdump.service > /dev/null 2>&1 || :
fi

%triggerun -- kexec-tools < 2.0.2-3
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply kdump
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save kdump >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del kdump >/dev/null 2>&1 || :
/bin/systemctl try-restart kdump.service >/dev/null 2>&1 || :


%triggerin -- firstboot
# we enable kdump everywhere except for paravirtualized xen domains; check here
if [ -f /proc/xen/capabilities ]; then
	if [ -z `grep control_d /proc/xen/capabilities` ]; then
		exit 0
	fi
fi
if [ ! -e %{_datadir}/firstboot/modules/firstboot_kdump.py ]
then
	ln -s %{_datadir}/kdump/firstboot_kdump.py %{_datadir}/firstboot/modules/firstboot_kdump.py
fi

%triggerin -- kernel-kdump
touch %{_sysconfdir}/kdump.conf


%triggerun -- firstboot
rm -f %{_datadir}/firstboot/modules/firstboot_kdump.py

%triggerpostun -- kernel kernel-xen kernel-debug kernel-PAE kernel-kdump
# List out the initrds here, strip out version nubmers
# and search for corresponding kernel installs, if a kernel
# is not found, remove the corresponding kdump initrd

#start by getting a list of all the kdump initrds
MY_ARCH=`uname -m`

for i in `ls $IMGDIR/initrd*kdump.img 2>/dev/null`
do
	KDVER=`echo $i | sed -e's/^.*initrd-//' -e's/kdump.*$//'`
	if [ ! -e $IMGDIR/vmlinuz-$KDVER ]
	then
		# We have found an initrd with no corresponding kernel
		# so we should be able to remove it
		rm -f $i
	fi
done

%files -f %{name}.lang
/sbin/*
%{_bindir}/*
%{_datadir}/kdump
%config(noreplace,missingok) %{_sysconfdir}/sysconfig/kdump
%config(noreplace,missingok) %{_sysconfdir}/kdump.conf
%config %{_sysconfdir}/udev/rules.d/*
%{dracutlibdir}/modules.d/*
%dir %{_localstatedir}/crash
%{_mandir}/man8/*
%{_mandir}/man5/*
%{_unitdir}/kdump.service
%doc News
%doc COPYING
%doc TODO
%doc kexec-kdump-howto.txt


%changelog
* Fri Feb 17 2012 Alexander Khrukin <akhrukin@mandriva.org> 2.0.3-1
+ Revision: 776089
- *ifarch macros rpmlint fix
- *added systemd service \n *patch with test package returned \n *ppc and ia64 arches
- merged with fedora16
- version update 2.0.3

* Thu Mar 10 2011 Leonardo Coelho <leonardoc@mandriva.org> 2.0.0-8
+ Revision: 643537
-add a kexec-tool service
-add a kexec-tools service

* Fri Dec 10 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-7mdv2011.0
+ Revision: 619960
- the mass rebuild of 2010.0 packages

* Fri Sep 11 2009 Thierry Vignaud <tv@mandriva.org> 2.0.0-6mdv2010.0
+ Revision: 438095
- rebuild

* Thu Mar 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 2.0.0-5mdv2009.1
+ Revision: 349455
- Add disable-kexec-test patch from Fedora (#47890).

* Thu Mar 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 2.0.0-4mdv2009.1
+ Revision: 349064
- Installing correct permissions on kexec executables.

* Mon Mar 02 2009 Eugeni Dodonov <eugeni@mandriva.com> 2.0.0-3mdv2009.1
+ Revision: 347291
- Installing kexec binaries to /sbin (#47889).
  Added manpages.

* Sat Sep 13 2008 Michael Scherer <misc@mandriva.org> 2.0.0-2mdv2009.0
+ Revision: 284438
- cleanly fix linking error, patch 1

* Sat Sep 13 2008 Michael Scherer <misc@mandriva.org> 2.0.0-1mdv2009.0
+ Revision: 284418
- new version thanks to Tomasz Chmielewski

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Apr 22 2007 Michael Scherer <misc@mandriva.org> 1.101-3mdv2008.0
+ Revision: 16807
- use %%mkrel

