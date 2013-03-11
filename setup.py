from distutils.core import setup

setup(name="powerusb",
      version="1.0",
      description="Control PowerUSB power strips",
      author="Mark Lamourine",
      author_email="markllama@gmail.com",
      license="Apache License 2.0",
      url="http://github.com/markllama/powerusb",
      packages=["powerusb"],
      scripts=["bin/powerusb"]
      )
