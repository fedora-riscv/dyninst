%define version 7.99

Summary: An API for Run-time Code Generation
License: LGPLv2+
Name: dyninst
Group: Development/Libraries
Release: 0.18%{?dist}
URL: http://www.dyninst.org
Version: %version
Exclusiveos: linux
#Right now dyninst does not know about the following architectures
ExcludeArch: s390 s390x %{arm}

# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#  git clone http://git.dyninst.org/dyninst.git; cd dyninst
#  git archive --format=tar.gz --prefix=dyninst/ 96826d0b7cbec7deb1398019ecadea5cf756c9c7 >  dyninst-7.99.tar.gz
#  git clone http://git.dyninst.org/docs.git; cd docs
#  git archive --format=tar.gz fe92e5b28804791ecadc893e469bc2215dbc3066 > dyninst-docs-7.99.tar.gz
Source0: %{name}-%{version}.tar.gz
Source1: %{name}-docs-%{version}.tar.gz
# Change version number so official dyninst 8.0 will replace it
Patch3: dyninst-git.patch
Patch5: dyninst-unused_vars.patch
Patch6: dyninst-delete_array.patch
BuildRequires: libxml2-devel >= 2.7.8
BuildRequires: libdwarf-devel 
BuildRequires: elfutils-libelf-devel
BuildRequires: boost-devel

%description

Dyninst is an Application Program Interface (API) to permit the insertion of
code into a running program. The API also permits changing or removing
subroutine calls from the application program. Run-time code changes are
useful to support a variety of applications including debugging, performance
monitoring, and to support composing applications out of existing packages.
The goal of this API is to provide a machine independent interface to permit
the creation of tools and applications that use run-time code patching.

%package devel
Summary: Header files for the compiling programs with Dyninst
Group: Development/System
Requires: dyninst = %{version}-%{release}
%description devel
Dyninst-devel includes the C header files that specify the Dyninst user-space
libraries and interfaces. This is required for rebuilding any program
that uses Dyninst.

%package static
Summary: Static libraries for the compiling programs with Dyninst
Group: Development/System
Requires: dyninst = %{version}-%{release}
%description static
dyninst-static includes the static versions of the library files for
the dyninst user-space libraries and interfaces.

%prep
%setup -q -n %{name}-%{version} -c
%setup -q -T -D -a 1

%patch3 -p1 -b .git

pushd dyninst
%patch5 -p1 -b .unused
%patch6 -p1 -b .delete
popd

%build

cd dyninst

%configure
make \
  DONT_BUILD_NEWTESTSUITE=1 \
  all StackwalkerAPI

%install

cd dyninst
make \
  LIBRARY_DEST=%{buildroot}/%{_libdir}/dyninst \
  PROGRAM_DEST=%{buildroot}/usr/bin \
  INCLUDE_DEST=%{buildroot}/usr/include/dyninst \
  DONT_BUILD_NEWTESTSUITE=1 \
  install

mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_libdir}/dyninst" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf

# Ugly hack to fix permissions
chmod 644 %{buildroot}%{_includedir}/dyninst/*
chmod 644 %{buildroot}%{_libdir}/dyninst/*.a

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)

# FIXME parseThat is not part of normal build
#%{_bindir}/parseThat
%{_libdir}/dyninst/*.so.*

# The README also contains the license information
#%doc LICENSE
%doc dyninst/dyninstAPI/README

%doc depGraphAPI.pdf
%doc dynC_API.pdf
%doc dyninstProgGuide.pdf
%doc symtabAPI/symtabProgGuide.pdf
%doc instructionProgGuide.pdf
%doc parseapi.pdf
%doc ProcControlAPI.pdf
%doc stackwalk/stackwalker.pdf
%doc dynC_API.pdf

%config(noreplace) /etc/ld.so.conf.d/*

%files devel
%defattr(-,root,root,-)
%{_includedir}/dyninst
%{_libdir}/dyninst/*.so

%files static
%defattr(-,root,root,-)
%{_libdir}/dyninst/*.a

%changelog
* Fri Jul 13 2012 William Cohen <wcohen@redhat.com> - 7.99-0.18
- Rebase on newer git tree the has a number of merges into it.
- Adjust spec file to allow direct use of git patches
- Fix to eliminate unused varables.
- Proper delete for array.

* Thu Jun 28 2012 William Cohen <wcohen@redhat.com> - 7.99-0.17
- Rebase on newer git repo.

* Thu Jun 28 2012 William Cohen <wcohen@redhat.com> - 7.99-0.16
- Eliminate dynptr.h file use with rebase on newer git repo.

* Mon Jun 25 2012 William Cohen <wcohen@redhat.com> - 7.99-0.14
- Rebase on newer git repo.

* Tue Jun 19 2012 William Cohen <wcohen@redhat.com> - 7.99-0.12
- Fix static library and header file permissions.
- Use sources from the dyninst git repositories.
- Fix 32-bit library versioning for libdyninstAPI_RT_m32.so.

* Wed Jun 13 2012 William Cohen <wcohen@redhat.com> - 7.99-0.11
- Fix library versioning.
- Move .so links to dyninst-devel.
- Remove unneded clean section.

* Fri May 11 2012 William Cohen <wcohen@redhat.com> - 7.0.1-0.9
- Clean up Makefile rules.

* Wed May 5 2012 William Cohen <wcohen@redhat.com> - 7.0.1-0.8
- Clean up spec file.

* Wed May 2 2012 William Cohen <wcohen@redhat.com> - 7.0.1-0.7
- Use "make install" and do staged build.
- Use rpm configure macro.

* Thu Mar 15 2012 William Cohen <wcohen@redhat.com> - 7.0.1-0.5
- Nuke the bundled boost files and use the boost-devel rpm instead.

* Mon Mar 12 2012 William Cohen <wcohen@redhat.com> - 7.0.1-0.4
- Initial submission of dyninst spec file.
