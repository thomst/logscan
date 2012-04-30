from distutils.core import setup

VERSION = "0.2.3"

setup( 
    name = "logscan", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/logscan",
    download_url = "https://github.com/downloads/thomst/logscan/logscan-{version}.tar.gz".format(version=VERSION),
    description = 'Command-line-tool to get time-specific access to log-files.',
    long_description = "This is a command-line-tool to get time-specific access to log-files, while rotated logfiles that are counted up (e.g. logfile.log, logfile.log.1, logfile.log.2.gz ...) are automatically taken together -also gzipped files are processed. Different date-time-formats are supported, inclusive simple timestamps as a huge number of seconds with three decimal-places, e.g. 123456789.123. Individual formats can be specified.",
    py_modules = ["logscanlib", "timeparse"],
    package_dir = {'' : 'src'},
    scripts = ["src/logscan"],
    data_files = [('etc', ['src/logscan.conf'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
