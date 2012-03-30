"""
    timeparse
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

import re, argparse, datetime
from argparse import ArgumentError

one = re.compile('(?<!\d)(\d)(?!\d)')
two = re.compile('(\d{2})')
digs = re.compile('(?<!\d)(\d+)(?!\d)')
date_keys = ('year', 'month', 'day')
time_keys = ('hour', 'minute', 'second')
delta_keys = ('weeks', 'days', 'hours', 'minutes', 'seconds')
datetime_keys = date_keys + time_keys

class DeltaDateTime:
    """Gives Methods to convert strings to datetime-objects.
    """
    def delta(self, string):
        """Convert a string to a timedelta-object of the datetime-class.
        """
        if re.match("[+-]", string): sign = string[0]
        else: sign = ''
        if self.dest in delta_keys: index = delta_keys.index(self.dest)
        else: index = 2
        delta = [int(sign + x) for x in digs.findall(string)]
        delta = dict(zip(delta_keys[index:], delta))
        try: delta = datetime.timedelta(**delta)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as timedelta'.format(string)
        )
        return delta

    def time(self, string):
        """Convert a string to a time-object of the datetime-class.
        """
        time = [int(x) for x in two.findall(one.sub('0\g<0>', string))]
        time = dict(zip(time_keys, time))
        try: time = datetime.time(**time)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as time'.format(string)
        )
        return time

    def date(self, string, no_future=False):
        """Convert a string to a date-object of the datetime-class.
        """
        today = datetime.date.today()
        date = two.findall(one.sub('0\g<0>', string))
        l = len(date)
        if l == 4: date = [''.join(date[:2])] + date[2:]
        elif l == 3: date[0] = (str(today.year)[:2] + date[0])
        elif l == 2: date.insert(0, today.year)
        elif l == 1: date = [today.year, today.month] + date
        date = [int(x) for x in date]
        date = dict(zip(date_keys, date))
        try: date = datetime.date(**date)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as date'.format(string)
        )
        if no_future and date > today:
            if l == 2: date = date.replace(year=today.year -1)
            elif l == 1:
                month = today.month -1
                if month == 0: date = date.replace(year=today.year -1, month=12)
                else: date = date.replace(month=month)
        return date

    def date_time(self, date_string, time_string):
        """Convert two string to a datetime-object of the datetime-class.
        """
        date = self.date(date_string)
        time = self.time(time_string)
        return datetime.datetime.combine(date, time)

class ParseDateTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        date_time = self.date_time(values[0], values[1])
        setattr(namespace, self.dest, date_time)

class ParseDate(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.date-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        date = self.date(values)
        setattr(namespace, self.dest, date)

class ParseTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.time-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        time = self.time(values)
        setattr(namespace, self.dest, date)

class ParseTimeDelta(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.timedelta-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        delta = self.delta(values)
        setattr(namespace, self.dest, delta)

class ParseDateTimeDelta(argparse.Action, DeltaDateTime):
    """Parse an argument to either a timedelta-, time or datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if re.match('[-+]', values[0]):
            delta = self.delta(' '.join(values))
            setattr(namespace, self.dest, delta)
        elif len(values) == 1:
            time = self.time(values[0])
            setattr(namespace, self.dest, time)
        elif len(values) == 2:
            date_time = self.date_time(values[0], values[1])
            setattr(namespace, self.dest, date_time)

class ParseNofDateTimeDelta(argparse.Action, DeltaDateTime):
    """Parse an argument to either a timedelta-, time or datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if re.match('[-+]', values[0]):
            delta = self.delta(' '.join(values))
            setattr(namespace, self.dest, delta)
        elif len(values) == 1:
            time = self.time(values[0])
            setattr(namespace, self.dest, time)
        elif len(values) == 2:
            date = self.date(values[0], no_future=True)
            time = self.time(values[1])
            date_time = datetime.datetime.combine(date, time)
            setattr(namespace, self.dest, date_time)

