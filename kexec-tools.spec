%define name kexec-tools
%define version 2.0.3
%define rel 1

%define _sbindir /sbin

Summary:	Tool for starting new kernel without reboot
Name:		%{name}
Version:	%{version}
Release:	%{rel}
License: 	GPL v2
Group: 		System/Configuration/Hardware
Source0:	http://kernel.org/pub/linux/utils/kernel/kexec/%{name}-%{version}.tar.bz2
Source1:    kexec.init
Source2:    kexec.sysconfig
URL:		http://www.kernel.org/pub/linux/kernel/people
Requires:	kernel

%description
kexec is a set of system calls that allows you to load another kernel
from the currently executing Linux kernel. The current implementation
has only been tested, and had the kinks worked out on x86, but the
generic code should work on any architecture.

%prep
%setup -q
install -m 755 %{SOURCE1} kexec.init
install -m 755 %{SOURCE2} kexec.sysconfig

%build
%configure2_5x
%make

%install
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
%makeinstall
mkdir -p -m755 $RPM_BUILD_ROOT%{_mandir}/man8/
install -m 644 kexec/kexec.8 $RPM_BUILD_ROOT%{_mandir}/man8/kexec.8
install -m 644 kdump/kdump.8 $RPM_BUILD_ROOT%{_mandir}/man8/kdump.8
install -m 755 kexec.init %{buildroot}%{_initrddir}/kexec
install -m 755 kexec.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/kexec

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
