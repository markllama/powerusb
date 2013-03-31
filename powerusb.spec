Summary: Control PowerUSB power strips
Name: powerusb
Version: 1.4
Release: 1
Source0: %{name}-%{version}.tar.gz
License: Apache License 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Mark Lamourine <markllama@gmail.com>
Url: http://github.com/markllama/powerusb

%description

Library and CLI tools to Control PowerUSB power strips.

This version only controls Basic power strips.  Watchdog, IO and Smart
features TBD.


%prep
%setup -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/lib/udev/rules.d
cp 99-powerusb.rules $RPM_BUILD_ROOT/lib/udev/rules.d

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Create a group which will be given permission to manage the strips
groupadd --system powerusb
%end

%postun
# remove the powerusb management group
groupdel powerusb
%end

%files -f INSTALLED_FILES
%defattr(-,root,root)
/lib/udev/rules.d/99-powerusb.rules
