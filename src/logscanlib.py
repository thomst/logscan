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

import time
import os
import re
import sys
import datetime
from gzip import GzipFile

CODEMAP = {
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
TIMECODES = [
    '%Y-%m-%d %H:%M:%S',
    '%b %d %X %Y',
    '%b %d %X',
    'timestamp',
    ]
def add_timecodes(timecodes):
    global TIMECODES
    TIMECODES += [c for c in timecodes if not c in TIMECODES]

class TimeCodeError(Exception):
    "raise this when timecodes don't fit"
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class Log():
    """Get time specific access to a logfile.
    """
    def __init__(self, fileobj, timecode=None):
        if timecode: self._set_timecode(timecode)
        self._name = fileobj.name
        if self.name.endswith('.gz'): fileobj = GzipFile(fileobj=fileobj)
        self._fileobj = fileobj
        if self.name == sys.stdin.name: self._lines = self._fileobj.readlines()
        else: self._lines = None
        self._start = None
        self._end = None

    _timecode = None
    @classmethod
    def _set_timecode(cls, timecode):
        cls._timecode = timecode
        for code in CODEMAP: timecode = timecode.replace(code, CODEMAP[code])
        cls._regexp = re.compile(timecode)

    @classmethod
    def _detect_timecode(cls, line):
        """Try to find a matching timecode.
        """
        for timecode in TIMECODES:
            cls._set_timecode(timecode)
            try: time = cls._get_linetime(line)
            except: continue
            else: return time
        cls._timecode = None
        raise TimeCodeError("...no proper timecode was found")

    @classmethod
    def _get_linetime(cls, line):
        """Get the logtime of a line.
        """
        if not cls._timecode: return cls._detect_timecode(line)
        match = cls._regexp.search(line)
        if not match: raise TimeCodeError("invalid timecode: '%s'" % cls._timecode)

        if cls._timecode == 'timestamp':
            time = datetime.datetime.fromtimestamp(float(match.group()))
        else:
            time = datetime.datetime.strptime(match.group(), cls._timecode)

            if time.year == 1900:   #TODO: maybe find a more elegant solution
                today = datetime.datetime.today()
                time = time.replace(year=today.year)
                if time > today: time = time.replace(year=today.year - 1)

        return time

    def _get_first_line(self):
        if self._lines: return self.lines[0]
        self._fileobj.seek(0)
        return self._fileobj.readline()

    def _get_last_line(self):
        # gzip.seek don't support seeking from end on
        if self._lines or isinstance(self._fileobj, GzipFile):
            return self.lines[-1]
        self._fileobj.seek(-400, 2)
        return self._fileobj.readlines()[-1]

    def _get_index(self, time, index=0):
        if not time: return None
        if time <= self.start: return 0
        if time > self.end: return len(self.lines)
        i = index or 0
        while time > self._get_linetime(self.lines[i]):
            i += 1
            if i == len(self.lines): break
        return i

    @property
    def name(self):
        """filename
        """
        return self._name

    @property
    def start(self):
        """start-time of the log
        """
        if not self._start:
            first_line = self._get_first_line()
            self._start = self._get_linetime(first_line)
        return self._start

    @property
    def end(self):
        """end-time of the log
        """
        if not self._end:
            last_line = self._get_last_line()
            self._end = self._get_linetime(last_line)
        return self._end

    @property
    def lines(self):
        """all lines of the log
        """
        if not self._lines:
            self._fileobj.seek(0)
            self._lines = self._fileobj.readlines()
        return self._lines

    def get_section(self, start=None, end=None):
        "Get loglines between two specified datetimes."
        if start and start > self.end: return list()
        if end and end <= self.start: return list()
        
        index1 = self._get_index(start)
        index2 = self._get_index(end, index1)
        return self.lines[index1:index2]

    def close(self):
        """Close the fileobject.
        """
        self._fileobj.close()


class RotatedLogs():
    """Get time-specific access to rotated logfiles.
    """
    def __init__(self, fileobj, timecode=None):
        self._name = fileobj.name
        self._files = [Log(fileobj, timecode)]
        if self.name != sys.stdin.name: self._rotate()

    def _rotate(self):
        i = 1
        name = self.name
        insert = lambda name: self._files.insert(0, Log(open(name, 'rb')))

        while 1:
            name = '%s.%s' % (self.name, i)
            if os.path.isfile(name): insert(name)
            elif os.path.isfile(name + '.gz'): insert(name + '.gz')
            else: break
            i += 1

    @property
    def name(self):
        """filename
        """
        return self._name

    @property
    def quantity(self):
        "number of rotated logfiles"
        return len(self._files)

    @property
    def start(self):
        """start-time of the log
        """
        return self._files[0].start

    @property
    def end(self):
        """end-time of the log
        """
        return self._files[-1].end

    @property
    def lines(self):
        """lines of all logfiles
        """
        lines = list()
        for file in self._files: lines += file.lines
        return lines

    def get_section(self, start=None, end=None):
        """Get loglines between two specified datetimes.
        """
        if start and start > self.end: return list()
        if end and end <= self.start: return list()
        if not (start or end): return self.lines

        files = self._files[:]
        files.reverse()
        lines = list()
        for file in files:
            if end and end  <= file.start: continue
            else: lines = file.get_section(start, end) + lines
            if start and start >= file.start: break

        return lines

    def close(self):
        """Close all logfiles.
        """
        for file in self._files: file.close()



