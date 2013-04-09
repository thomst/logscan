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
        self._lines = None
        self._start = None
        self._end = None

    _timecode = None
    @classmethod
    def _set_timecode(cls, timecode):
        cls._timecode = timecode
        for code in CODEMAP: timecode = timecode.replace(code, CODEMAP[code])
        cls._regexp = re.compile(timecode)

    @classmethod
    def reset_timecode(cls):
        cls._timecode = None

    def _detect_timecode(self, line):
        for timecode in TIMECODES:
            self._set_timecode(timecode)
            try: time = self._get_linetime(line)
            except: continue
            else: return
        raise TimeCodeError("no proper timecode was found...")

    def _get_first_line(self):
        if self._lines: return self.lines[-1]
        self._fileobj.seek(0)   #TODO: do this work with stdin?
        return self._fileobj.readline()

    def _get_last_line(self):
        # gzip.seek don't support seeking from end on
        if self._lines or isinstance(self._fileobj, GzipFile):
            return self.lines[-1]
        self._fileobj.seek(-400, 2)
        return self._fileobj.readlines()[-1]

    def _get_linetime(self, line):
        """Get the logtime of a line.
        """
        if not self._timecode: self._detect_timecode(line)
        match = self._regexp.search(line)
        if not match: raise TimeCodeError("%s doesn't fit" % self._timecode)

        if self._timecode == 'timestamp':
            time = datetime.datetime.fromtimestamp(float(match.group()))
        else:
            time = datetime.datetime.strptime(match.group(), self._timecode)

            if time.year == 1900:   #TODO: maybe find a more elegant solution
                today = datetime.datetime.today()
                time = time.replace(year=today.year)
                if time > today: time = time.replace(year=today.year - 1)

        return time

    @property
    def name(self):
        return self._name

    @property
    def start(self):
        "time the log starts with"
        if not self._start:
            first_line = self._get_first_line()
            self._start = self._get_linetime(first_line)
        return self._start

    @property
    def end(self):
        "time the log ends with"
        if not self._end:
            last_line = self._get_last_line()
            self._end = self._get_linetime(last_line)
        return self._end

    @property
    def lines(self):
        "all lines of the log"
        if not self._lines:
            self._fileobj.seek(0)
            self._lines = self._fileobj.readlines()
        return self._lines

    def get_section(self, start, end):
        "Get loglines between two specified datetimes."

        if start > self.end or end < self.start: return list()
        if start <= self.start and end >= self.end: return self.lines

        lines = []
        got = False
        for line in self.lines:
            time = self._get_linetime(line)
            if time >= end: break
            if time >= start: got = True
            if got: lines.append(line)

        return lines

        #TODO: check if this is more perfomant
#        lines = []
#        got = start <= self.start
#        toend = end > self.end
#        for line in self.lines:
#            time = self._get_linetime(line)
#            if time:
#                if not got and time >= start: got = True
#                if not toend and time >= end: break
#                if got: lines.append(line)

    def close(self):
        self._fileobj.close()


class RotatedLogs():
    """Get time-specific access to rotated logfiles.
    """
    def __init__(self, fileobj, timecode=None, timecodes=list()):
        self._name = fileobj.name
        self._files = [Log(fileobj, timecode)]
        if self.name != '<stdin>': self._rotate()

        global TIMECODES
        TIMECODES += [c for c in timecodes if not c in TIMECODES]

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
        return self._name

    @property
    def quantity(self):
        return len(self._files)

    @property
    def start(self):
        return self._files[0].start

    @property
    def end(self):
        return self._files[-1].end

    @property
    def lines(self):
        lines = list()
        for file in self._files: lines += file.lines
        return lines

    def get_section(self, start, end):
        #TODO: support for start and end as None
        if start > self.end or end < self.start: return list()
        if start <= self.start and end >= self.end: return self.lines

        files = self._files
        files.reverse()
        lines = list()
        for file in files:
            if end  <= file.start: continue
            else: lines = file.get_section(start, end) + lines
            if start >= file.start: break

        return lines

    def close(self):
        for file in self._files: file.close()



