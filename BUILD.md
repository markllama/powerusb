The PowerUSB software can be packaged in one of several forms.

The versioning is managed using Tito, so the first package should be an RPM
using Tito.  This will update the powerusb.spec file with the current version.

    tito build --rpm [--test]

Once the versioning is set you can create a Python egg:

    python setup.py bdist

And if you have the python-stdeb package installed, you can create a .deb

    python setup.py --command-packages=stdeb.command bdist_deb
