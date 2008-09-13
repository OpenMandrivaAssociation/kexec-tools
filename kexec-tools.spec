%define name kexec-tools
%define version 2.0.0
%define rel 2

Summary:	Tool for starting new kernel without reboot
Name:		%{name}
Version:	%{version}
Release:	%mkrel %{rel}
License: 	GPL v2
Group: 		System/Configuration/Hardware
#http://developer.osdl.org/rddunlap/kexec/kexec-tools-%{version}.tar.bz2
Source0:	http://www.kernel.org/pub/linux/kernel/people/horms/kexec-tools/%{name}-%{version}.tar.bz2
Patch0:     kexec-tools-fix_as_needed.patch
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
%patch -p0

%build
%configure2_5x
%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc TODO News
%_libdir/%name/kexec_test
%_sbindir/*

