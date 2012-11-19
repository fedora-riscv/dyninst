Summary: An API for Run-time Code Generation
License: LGPLv2+
Name: dyninst
Group: Development/Libraries
Release: 1%{?dist}
URL: http://www.dyninst.org
Version: 8.0
Exclusiveos: linux
#Right now dyninst does not know about the following architectures
ExcludeArch: s390 s390x %{arm}

# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#  git clone http://git.dyninst.org/dyninst.git; cd dyninst
#  git archive --format=tar.gz --prefix=dyninst/ v8.0 > dyninst-8.0.tar.gz
#  git clone http://git.dyninst.org/docs.git; cd docs
#  git archive --format=tar.gz v8.0 > dyninst-docs-8.0.tar.gz
# Verify the commit ids with:
#  gunzip -c dyninst-8.0.tar.gz | git get-tar-commit-id
#  gunzip -c dyninst-docs-8.0.tar.gz | git get-tar-commit-id
Source0: %{name}-%{version}.tar.gz
Source1: %{name}-docs-%{version}.tar.gz
Patch5: dyninst-unused_vars.patch
BuildRequires: libdwarf-devel >= 20111030
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

%package doc
Summary: Documentation for using the Dyninst API
Group: Documentation
%description doc
dyninst-doc contains API documentation for the Dyninst libraries.

%package devel
Summary: Header files for the compiling programs with Dyninst
Group: Development/System
Requires: dyninst = %{version}-%{release}
Requires: boost-devel
%description devel
dyninst-devel includes the C header files that specify the Dyninst user-space
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

pushd dyninst
%patch5 -p1 -b .unused
popd

%build

cd dyninst

%configure
make %{?_smp_mflags} \
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

%dir %{_libdir}/dyninst
%{_libdir}/dyninst/*.so.*

%doc dyninst/COPYRIGHT
%doc dyninst/LGPL

%config(noreplace) /etc/ld.so.conf.d/*

%files doc
%defattr(-,root,root,-)
%doc dynC_API.pdf
%doc DyninstAPI.pdf
%doc InstructionAPI.pdf
%doc ParseAPI.pdf
%doc PatchAPI.pdf
%doc ProcControlAPI.pdf
%doc stackwalk/stackwalker.pdf
%doc SymtabAPI.pdf

%files devel
%defattr(-,root,root,-)
%{_includedir}/dyninst
%{_libdir}/dyninst/*.so

%files static
%defattr(-,root,root,-)
%{_libdir}/dyninst/*.a

%changelog
* Mon Nov 19 2012 Josh Stone <jistone@redhat.com> 8.0-1
- Update to release 8.0.
- Updated "%files doc" to reflect renames.
- Drop the unused BuildRequires libxml2-devel.
- Drop the 7.99.x version-munging patch.

* Fri Nov 09 2012 Josh Stone <jistone@redhat.com> 7.99.2-0.29
- Rebase to git e99d7070bbc39c76d6d528db530046c22681c17e

* Mon Oct 29 2012 Josh Stone <jistone@redhat.com> 7.99.2-0.28
- Bump to 7.99.2 per abi-compliance-checker results

* Fri Oct 26 2012 Josh Stone <jistone@redhat.com> 7.99.1-0.27
- Rebase to git dd8f40b7b4742ad97098613876efeef46d3d9e65
- Use _smp_mflags to enable building in parallel.

* Wed Oct 03 2012 Josh Stone <jistone@redhat.com> 7.99.1-0.26
- Rebase to git 557599ad7417610f179720ad88366c32a0557127

* Thu Sep 20 2012 Josh Stone <jistone@redhat.com> 7.99.1-0.25
- Rebase on newer git tree.
- Bump the fake version to 7.99.1 to account for ABI differences.
- Enforce the minimum libdwarf version.
- Drop the upstreamed R_PPC_NUM patch.

* Wed Aug 15 2012 Karsten Hopp <karsten@redhat.com> 7.99-0.24
- check if R_PPC_NUM is defined before using it, similar to R_PPC64_NUM

* Mon Jul 30 2012 Josh Stone <jistone@redhat.com> 7.99-0.23
- Rebase on newer git tree.
- Update license files with upstream additions.
- Split documentation into -doc subpackage.
- Claim ownership of %{_libdir}/dyninst.

* Fri Jul 27 2012 William Cohen <wcohen@redhat.com> - 7.99-0.22
- Correct requires for dyninst-devel.

* Wed Jul 25 2012 Josh Stone <jistone@redhat.com> - 7.99-0.21
- Rebase on newer git tree
- Update context in dyninst-git.patch
- Drop dyninst-delete_array.patch
- Drop dyninst-common-makefile.patch

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.99-0.20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 William Cohen <wcohen@redhat.com> - 7.99-0.19
- Patch common/i386-unknown-linux2.4/Makefile to build.

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
