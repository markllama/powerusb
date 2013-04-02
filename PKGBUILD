# $Id$
# Maintainer: Mark Lamourine <markllama@gmail.com>

pkgname('python-powerusb', 'python2-powerusb')
pkgver=1.4
pkgrel=1
pkgdesc="Library and CLI tools to Control PowerUSB power strips."
url="http://pwrusb.com"
arch="any"
license="Apache"
makedepends=("python", "python2")
source=(http://github.com/markllama/powerusb)

package_python-powerusb() {
  depends=('python')

  cd "$srcdir/powerusb-$pkgver"
  python setup.py build
  python setup.py install --prefix=/usr --root="$pkgdir"

}

package_python2-powerusb() {
  depends=('python2')


  cd "$srcdir/powerusb-$pkgver"
  python2 setup.py build
  python2 setup.py install --prefix=/usr --root="$pkgdir"

}
