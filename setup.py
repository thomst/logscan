from distutils.core import setup
import os

VERSION = "0.5.1"

setup( 
    name = "logscan", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/logscan",
    download_url = "https://pypi.python.org/packages/source/l/logscan/logscan-{version}.tar.gz".format(version=VERSION),
    description = 'Command-line-tool to get time-specific access to log-files.',
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["logscanlib"],
    scripts = ["logscan"],
    data_files = [('etc', ['logscan.conf'])],
    install_requires = [
        'timeparser',
        'argparse',
        'daytime',
        'timeparse'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Topic :: System :: Logging',
    ],
    license='GPL',
    keywords='logfile logfiles log time-specific access rotated scan',
)
