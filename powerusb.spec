Summary: Control PowerUSB power strips
Name: python-powerusb
Version: 2.0
Release: 2
Source0: %{name}-%{version}.tar.gz
License: Apache License 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Mark Lamourine <markllama@gmail.com>
Url: http://github.com/markllama/powerusb
Requires: python3
Requires: pythoni3-lxml
Requires: libusb
Requires: libhid
Requires: hidapi
Requires: hidapi-devel

%description

Library and CLI tools to Control PowerUSB power strips.

This version only controls Basic power strips.  Watchdog, IO and Smart
features TBD.


%prep
%setup -n %{name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/lib/udev/rules.d
cp 99-powerusb.rules $RPM_BUILD_ROOT/lib/udev/rules.d

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Create a group which will be given permission to manage the strips
groupadd --system powerusb

%files -f INSTALLED_FILES
%defattr(-,root,root)
/lib/udev/rules.d/99-powerusb.rules
