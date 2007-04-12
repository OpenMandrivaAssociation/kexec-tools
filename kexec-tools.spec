%define name kexec-tools
%define version 1.101
%define mdkrelease 2mdk

Summary:	Tool for starting new kernel without reboot
Name:		%{name}
Version:	%{version}
Release:	%{mdkrelease}
License: 	GPL
Group: 		System/Configuration/Hardware
#http://developer.osdl.org/rddunlap/kexec/kexec-tools-%{version}.tar.bz2
Source0:	http://www.xmission.com/~ebiederm/files/kexec/%{name}-%{version}.tar.bz2
URL:		http://www.xmission.com/~ebiederm/files/kexec/
Requires:	kernel
BuildRoot: 	%{_tmppath}/%{name}-%{version}-build

%description
kexec is a set of system calls that allows you to load another kernel
from the currently executing Linux kernel. The current implementation
has only been tested, and had the kinks worked out on x86, but the
generic code should work on any architecture.

%prep
%setup -q

%build
%configure2_5x
%make

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/sbin

install objdir/build/sbin/{kexec,kdump} $RPM_BUILD_ROOT/sbin
install objdir/build/lib/kexec-tools/kexec_test $RPM_BUILD_ROOT/sbin

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc TODO News
%attr(755,root,root) /sbin/*

