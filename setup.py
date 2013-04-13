from distutils.core import setup

VERSION = "0.3"

setup( 
    name = "logscan", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/logscan",
    download_url = "https://github.com/downloads/thomst/logscan/logscan-{version}.tar.gz".format(version=VERSION),
    description = 'Command-line-tool to get time-specific access to log-files.',
    long_description = "logscan is a command-line-tool to get time-specific access to logfiles. It can handle rotated and gzipped logfiles or reads from stdin. The log is automatically checked for different timecodes.",
    py_modules = ["logscanlib"],
    package_dir = {'' : 'src'},
    scripts = ["src/logscan"],
    data_files = [('etc', ['src/logscan.conf'])],
install_requires = ['timeparse'],
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
