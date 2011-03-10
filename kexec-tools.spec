%define name kexec-tools
%define version 2.0.0
%define rel 8

%define _sbindir /sbin

Summary:	Tool for starting new kernel without reboot
Name:		%{name}
Version:	%{version}
Release:	%mkrel %{rel}
License: 	GPL v2
Group: 		System/Configuration/Hardware
#http://developer.osdl.org/rddunlap/kexec/kexec-tools-%{version}.tar.bz2
Source0:	http://www.kernel.org/pub/linux/kernel/people/horms/kexec-tools/%{name}-%{version}.tar.bz2
Source1:    kexec.init
Source2:    kexec.sysconfig
Patch0:     kexec-tools-fix_as_needed.patch
Patch1:	    kexec-tools-2.0.0-disable-kexec-test.patch
URL:		http://www.kernel.org/pub/linux/kernel/people/horms/kexec-tools/
Requires:	kernel
BuildRoot: 	%{_tmppath}/%{name}-%{version}-build

%description
kexec is a set of system calls that allows you to load another kernel
from the currently executing Linux kernel. The current implementation
has only been tested, and had the kinks worked out on x86, but the
generic code should work on any architecture.

%prep
%setup -q
%patch0 -p0
%patch1 -p1
install -m 755 %{SOURCE1} kexec.init
install -m 755 %{SOURCE2} kexec.sysconfig

%build
%configure2_5x
%make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
%makeinstall
mkdir -p -m755 $RPM_BUILD_ROOT%{_mandir}/man8/
install -m 644 kexec/kexec.8 $RPM_BUILD_ROOT%{_mandir}/man8/kexec.8
install -m 644 kdump/kdump.8 $RPM_BUILD_ROOT%{_mandir}/man8/kdump.8
install -m 755 kexec.init %{buildroot}%{_initrddir}/kexec
install -m 755 kexec.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/kexec

%clean
rm -rf $RPM_BUILD_ROOT

%post
%_post_service kexec

%preun
%_preun_service kexec



%files
%defattr(644,root,root,755)
%doc TODO News
%attr(0755,root, root)%{_initrddir}/kexec
%config %{_sysconfdir}/sysconfig/kexec
%_mandir/*/*.*
%attr(0755, root, root) %_sbindir/*

