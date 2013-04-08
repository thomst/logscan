"""
    logscanlib
    ~~~~~~~~~~
"""

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import time, os, re, gzip, sys
from datetime import datetime

TIME_MAP = {
    '%Y' : '(?P<Y>\d{4})',
    '%m' : '(?P<m>\d{2})',
    '%d' : '(?P<d>[ |\d]\d)',
    '%H' : '(?P<H>\d{2})',
    '%M' : '(?P<M>\d{2})',
    '%S' : '(?P<S>\d{2})',
    '%a' : '(?P<a>[a-zA-Z]{3})',
    '%A' : '(?P<A>[a-zA-Z]{6,9})',
    '%b' : '(?P<b>[a-zA-Z]{3})',
    '%B' : '(?P<B>[a-zA-Z]{3,9})',
    '%c' : '(?P<c>([a-zA-Z]{3} ){2} \d{1,2} (\d{2}:){2}\d{2}) \d{4}',
    '%I' : '(?P<I>\d{2})',
    '%j' : '(?P<j>\d{3})',
    '%p' : '(?P<p>[A-Z]{2})',
    '%U' : '(?P<U>\d{2})',
    '%W' : '(?P<W>\d{2})',
    '%w' : '(?P<w>\d{1})',
    '%y' : '(?P<y>\d{2})',
    '%x' : '(?P<x>(\d{2}/){2}\d{2})',
    '%X' : '(?P<X>(\d{2}:){2}\d{2})',
    '%%' : '%',
    'timestamp' : '(?P<S>\d{10}\.\d{3})',
#    '%s' : '(?P<s>\d{10})',    # TODO: not yet tested
}
CONFPATHS = (
    '/usr/local/etc/logscan.conf',
    '/usr/etc/logscan.conf',
    os.path.join(os.getenv('HOME', '.'), '.logscan.conf'),
    'logscan.conf',
)
FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%b %d %X %Y',
    '%b %d %X',
    'timestamp',
]
confpaths = [p for p in CONFPATHS if os.path.exists(p)]
for path in confpaths:
    with open(path) as file
        formats = [f.rstrip('\n') for f in file if not re.match('[#\n ]+', f)]
        FORMATS += [f for f in formats if f not in FORMATS]


class Log():
    """Get time specific access to a logfile.
    """
    _codes = [
    '%Y-%m-%d %H:%M:%S',
    '%b %d %X %Y',
    '%b %d %X',
    'timestamp',
        ]
    @classmethod
    def add_time_codes(cls, codes):
        """Add time-codes as list.
        """
        cls._codes += codes

    def __init__(self, path, strf=None, pattern=None):
        self.path = path
        self.strf = strf
        self.pattern = pattern
        self.isopen = False
        self.lines = None
        self.first_line = None
        self.last_line = None
        self.start = None
        self.end = None
        if not self.pattern: self.get_pattern()

    def period(self):
        if self.start: return
        self.get_first_and_last_line()
        self.start = self.linetime(self.first_line)
        self.end = self.linetime(self.last_line)

    def get_pattern(self):
        """Build a regex-pattern out of the format for the time.
        """
        if self.strf: self.build_pattern()
        else: self.check_formats()

    def build_pattern(self):
        pattern = self.strf
        for format in TIME_MAP:
            pattern = pattern.replace(format, TIME_MAP[format])
        self.pattern = re.compile(pattern)

    def check_formats(self):
        """Find out which time-format fits for the logfile.
        """
        self.get_first_line()
        for format in FORMATS:
            self.strf = format
            self.get_pattern()
            if self.linetime(self.first_line): break
        if not self.pattern:
            print "could not find a fitting format"
            sys.exit(1)

    def open(self):
        """Open gziped and normal Logfiles.
        """
        if self.isopen: return
        if re.match('.*?\.gz$', self.path): self.file = gzip.open(self.path, 'r')
        else: self.file = open(self.path, 'r')
        self.isopen = True

    def close(self):
        """Close the Logfile.
        """
        self.file.close()
        self.isopen = False

    def get_first_line(self):
        self.open()
        if not self.first_line: self.first_line = self.file.readline()

    def get_first_and_last_line(self):
        self.open()
        if not self.first_line: self.first_line = self.file.readline()
        try:
            self.file.seek(-250, 2)
            self.last_line = self.file.readlines()[-1]
        except:
            self.lines = self.get_all_lines()
            self.last_line = self.lines[-1]

    def get_all_lines(self):
        """Get all lines of the file.
        """
        if self.lines: return self.lines
        self.open()
        self.file.seek(0, 0)
        self.lines = self.file.readlines()
        self.close()
        return self.lines

    def linetime(self, line):
        """Get the logtime of a line.
        """
        match = self.pattern.search(line)
        if not match: return None
        if self.strf == 'timestamp':
            time = datetime.fromtimestamp(float(match.group()))
        else:
            time = datetime.strptime(match.group(), self.strf)
        if time.year == 1900:
            today = datetime.today()
            time = time.replace(year=today.year)
            if time > today: time = time.replace(year=today.year - 1)
        return time

    def section(self, start_time=None, end_time=None):
        """Get loglines between two specified datetimes.
        """
        start_time = start_time or self.start
        end_time = end_time or self.end
        if end_time < self.start or start_time > self.end: return []
        elif not self.lines: self.lines = self.get_all_lines()
        if end_time >= self.end and start_time <= self.start: return self.lines

        lines = []
        matched = start_time <= self.start
        till_end = end_time > self.end
        for l in self.lines:
            time = self.linetime(l)
            if not time: continue
            if not matched and time > start_time: matched = True
            if not till_end and time > end_time: break
            if matched: lines.append(l)

        self.close()
        return lines

class Logs():
    """Get time-specific access to rotated logfiles using Log as parent-class.
    """
    def __init__(self, path, strf=None):
        self.path = path
        self.strf = strf
        self.pattern = None
        self.files = []
        self.rotate()

    def rotate(self):
        """Collect all rotated logfile-paths in self.files.
        """
        c = 1
        path = self.path
        while os.path.isfile(path) or os.path.isfile(path+'.gz'):
            if os.path.isfile(path+'.gz'): path = path+'.gz'
            self.files.append(Log(path, self.strf, self.pattern))
            if not self.pattern: self.get_pattern()
            path = '{0}.{1}'.format(self.path, c)
            c += 1
        self.number_files = len(self.files)

    def get_pattern(self):
        self.pattern = self.files[0].pattern
        self.strf = self.files[0].strf

    def period(self):
        self.files[0].period()
        self.end = self.files[0].end
        self.files[-1].period()
        self.start = self.files[-1].start

    def section(self, start_time=None, end_time=None):
        """Get a section of all lines of all files.
        """
        if not start_time and not end_time: return self.get_all_lines()
        self.period()
        if end_time < self.start or start_time > self.end: return []
        if end_time >= self.end and start_time <= self.start:
            return self.get_all_lines()

        lines = []
        for f in self.files:
            f.period()
            if end_time < f.start: continue
            else: lines = f.section(start_time, end_time) + lines
            if start_time >= f.start: break

        return lines

    def get_all_lines(self):
        lines = []
        for f in self.files: lines = f.get_all_lines() + lines
        return lines

    def close(self):
        for f in self.files:
            try: f.close()
            except: pass


