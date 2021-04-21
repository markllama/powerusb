from distutils.core import setup

setup(name="powerusb",
      version="1.7",
      description="Control PowerUSB power strips",
      long_description="""
Library and CLI tools to Control PowerUSB power strips.

This version only controls Basic power strips.  Watchdog, IO and Smart
features TBD.
""",
      author="Mark Lamourine",
      author_email="markllama@gmail.com",
      license="Apache License 2.0",
      url="http://github.com/markllama/powerusb",
      packages=["powerusb"],
#      install_requires=["Cython",
#                        "lxml"
#                        "hidapi",
#                        "pyusb"],
      scripts=["bin/powerusb"],
      data_files=[("/lib/udev/rules.d", ["99-powerusb.rules"])]
      )
