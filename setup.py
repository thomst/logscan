from distutils.core import setup

VERSION = "0.3.1"

setup( 
    name = "logscan", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/logscan",
    download_url = "https://pypi.python.org/packages/source/l/logscan/logscan-{version}.tar.gz".format(version=VERSION),
    description = 'Command-line-tool to get time-specific access to log-files.',
    long_description = open('README.rst').read(),
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
