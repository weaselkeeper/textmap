Name:           textmap
Version:        0.1
Release:        0
Summary:        A few python scripts for yum repo clone/copy/assemble
License:        GPLv2
URL:            https://github.com/weaselkeeper/textmap
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python
Requires:       rpm-python
Requires:       python-argparse
Requires:       python-simplejson

%description
simple script that takes an 8bit ascii file, and presents a graphical
visualization of symbol frequency in the supplied text

%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/textmap
cp -r ./*.py %{buildroot}%{_bindir}/

%files
%{_bindir}/*.py

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Sun Aug 04 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.
