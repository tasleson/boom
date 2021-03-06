%{!?__python2: %global __python2 /usr/bin/python2}
%{!?py2_build: %global py2_build %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} build --executable="%{__python2} -s"}}
%{!?py2_install: %global py2_install %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}}}
%{!?python2_sitelib: %global python2_sitelib %{python_sitelib}}

%if 0%{?rhel}
%global py2_pkgname python-boom
%else
%global py2_pkgname python2-boom
%global with_python3 1
%endif

%global summary A set of libraries and tools for managing boot loader entries

Name: boom
Version: 0.9
Release: 1%{?dist}
Summary: %{summary}

Group: Applications/System
License: GPLv2
URL: https://github.com/bmr-cymru/boom	
Source0: boom-%{version}.tar.gz

BuildArch: noarch

BuildRequires: python2-devel
%if 0%{?rhel}
BuildRequires: python-sphinx
%else
BuildRequires: python2-sphinx
%endif
%if 0%{!?with_python3:1}
BuildRequires: python-setuptools
%endif

%if 0%{?with_python3}
BuildRequires: python2-setuptools
BuildRequires: python3-devel
BuildRequires: python3-sphinx
BuildRequires: python3-setuptools
%endif # if with_python3

%description
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the bls patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

%package -n %{?py2_pkgname}
Summary: %{summary}
%{?python_provide:%python_provide python2-boom}

# RHEL6's Python-2.6 does not include the python-argparse module in
# the main python-libs pacage, and the dbus package is required to
# provide a machine_id on this release.
#
# Since the machine_id is only automatically generated at boot time
# (and since the machine may not have been rebooted since the package
# was installed), ensure the file is present by generating it in the
# %post script.
%if 0%{?rhel} == 6
Requires: python-argparse
Requires: dbus

%post -n %{?py2_pkgname}
if [ ! -e /var/lib/dbus/machine-id ]; then
    dbus-uuidgen > /var/lib/dbus/machine-id
fi
%endif

%description -n %{?py2_pkgname}
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the bls patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

This package provides the python2 version of boom.


%if 0%{?with_python3}
%package -n python3-boom
Summary: %{summary}
%{?python_provide:%python_provide python3-boom}

%description -n python3-boom
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the bls patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

This package provides the python3 version of boom.


%endif # if with_python3
%prep
%autosetup -n boom-%{version}

%build
%py2_build

%if 0%{?with_python3}
%py3_build
%endif # if with_python3

%install
# Install Python3 first, so that the py2 build of usr/bin/boom is not
# overwritten by the py3 version of the script.
%if 0%{?with_python3}
%py3_install
make -C doc html BUILDDIR=../doc
%endif # if with_python3

%py2_install

# Install Grub2 integration scripts
mkdir -p ${RPM_BUILD_ROOT}/etc/grub.d
mkdir -p ${RPM_BUILD_ROOT}/etc/default
install -m 755 etc/grub.d/42_boom ${RPM_BUILD_ROOT}/etc/grub.d
install -m 644 etc/default/boom ${RPM_BUILD_ROOT}/etc/default

# Make configuration directories
mkdir -p ${RPM_BUILD_ROOT}/boot/boom/profiles
mkdir -p ${RPM_BUILD_ROOT}/boot/loader/entries
install -d -m 750 ${RPM_BUILD_ROOT}/boot/boom/profiles ${RPM_BUILD_ROOT}
install -d -m 750 ${RPM_BUILD_ROOT}/boot/loader/entries ${RPM_BUILD_ROOT}
install -m 644 examples/profiles/*.profile ${RPM_BUILD_ROOT}/boot/boom/profiles
install -m 644 examples/boom.conf ${RPM_BUILD_ROOT}/boot/boom

# Automatically enable legacy bootloader support for RHEL6 builds
%if 0%{?rhel} == 6
sed -i 's/enable = False/enable = True/' ${RPM_BUILD_ROOT}/boot/boom/boom.conf
%endif

mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man8
mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man5
install -m 644 man/man8/boom.8 ${RPM_BUILD_ROOT}/%{_mandir}/man8
install -m 644 man/man5/boom.5 ${RPM_BUILD_ROOT}/%{_mandir}/man5

%check
# Test suite currently does not operate in rpmbuild environment
#%{__python2} setup.py test

#%if 0%{?with_python3}
#%{__python3} setup.py test
#%endif # if with_python3

%files -n %{?py2_pkgname}
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc README.md
%doc %{_mandir}/man*/boom.*
%if 0%{?sphinx_docs}
%doc doc/html/
%endif # if sphinx_docs
%doc examples/*
%{python2_sitelib}/*
%{_bindir}/boom
/etc/grub.d/42_boom
%config(noreplace) /etc/default/boom
%config(noreplace) /boot/boom/boom.conf
/boot/*

%if 0%{?with_python3}
%files -n python3-boom
%license COPYING
%doc README.md
%doc %{_mandir}/man*/boom.*
%if 0%{?sphinx_docs}
%doc doc/html/
%endif # if sphinx_docs
%doc examples/*
%{python3_sitelib}/*
/etc/grub.d/42_boom
/etc/default/boom
/boot/*
%endif # if with_python3

%changelog
* Thu Jun 21 2018 Bryn M. Reeves <bmr@redhat.com> = 0.9-1
- Bump package release

* Fri Apr 06 2018 Bryn M. Reeves <bmr@redhat.com> = 0.8-5.6
- Automatically enable legacy support on RHEL6 builds
- Add %post snippet to generate machine_id on RHEL6
- Add additional needed dependencies for RHEL6 builds
- Print error if machine_id cannot be found

* Tue Mar 27 2018 Bryn M. Reeves <bmr@redhat.com> = 0.8-5.3
- Include fixes for issue #11 in Copr build

* Fri Mar 16 2018 Bryn M. Reeves <bmr@redhat.com> = 0.8-5.2
- Add python-2.6 compatibility patch (el6)

* Thu Mar 15 2018 Bryn M. Reeves <bmr@redhat.com> = 0.8-5.1
- Add built-in profiles to RPM package
- Bump package release

* Fri Mar 09 2018 Bryn M. Reeves <bmr@redhat.com> = 0.8-5
- Add boom(5) configuration file man page

* Tue Oct 31 2017 Bryn M. Reeves <bmr@redhat.com> = 0.8-1
- Merge spec file changes from mcsontos
- Add boom.8 manual page
- Update minor version number

* Fri Oct 27 2017 Bryn M. Reeves <bmr@redhat.com> = 0.1-4
- Update RPM build to latest master

* Sat Oct 21 2017 Bryn M. Reeves <bmr@redhat.com> = 0.1-2
- Prevent py3 boom script clobbering py2 version

* Thu Oct 19 2017 Bryn M. Reeves <bmr@redhat.com> = 0.1-1
- Initial RPM spec
