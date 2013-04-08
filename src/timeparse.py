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
digs = re.compile('(?<!\d)([-+]?\d+)(?![-+\d])')
delta_keys = ('weeks', 'days', 'hours', 'minutes', 'seconds')


class DeltaDateTime:
    """Gives Methods to convert strings to datetime-objects.
    """
    def string_to_delta(self, string):
        """Convert a string to a timedelta-object of the datetime-class.
        """
        delta = [int(x) for x in digs.findall(string)]
        delta = dict(zip(delta_keys[delta_keys.index(self.dest):], delta))
        try: delta = datetime.timedelta(**delta)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as timedelta'.format(string)
        )
        return delta

    def string_to_time(self, string):
        """Convert a string to a time-object of the datetime-class.
        """
        time = [int(x) for x in two.findall(one.sub('0\g<0>', string))]
        try: time = datetime.time(*time)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as time'.format(string)
        )
        return time

    def string_to_date(self, string):
        """Convert a string to a date-object of the datetime-class.
        """
        today = datetime.date.today()
        date = two.findall(one.sub('0\g<0>', string))
        lenght = len(date)
        if lenght == 4: date = date[:2] + [''.join(date[2:])]
        elif lenght == 3: date[2] = (str(today.year)[:2] + date[2])
        elif lenght == 2: date.append(today.year)
        elif lenght == 1: date = date + [today.month, today.year]
        date = [int(x) for x in date]
        date.reverse()
        try: date = datetime.date(*date)
        except: raise ArgumentError(
            self,
            '{0} could not be parsed as date'.format(string)
        )
        return date

    def strings_to_datetime(self, datestring, timestring):
        """Convert two string to a datetime-object of the datetime-class.
        """
        date = self.string_to_date(datestring)
        time = self.string_to_time(timestring)
        return datetime.datetime.combine(date, time)



class ParseDateTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        date_time = self.strings_to_datetime(values[0], values[1])
        setattr(namespace, self.dest, date_time)


class ParseDate(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.date-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        date = self.string_to_date(values)
        setattr(namespace, self.dest, date)


class ParseTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.time-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        time = self.string_to_time(values)
        setattr(namespace, self.dest, date)


class ParseTimeDelta(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime.timedelta-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        delta = self.string_to_delta(values)
        setattr(namespace, self.dest, delta)


class ParseDateTimeOrTime(argparse.Action, DeltaDateTime):
    """Parse an argument to either a timedelta-, time or datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1: obj = self.string_to_time(values[0])
        elif len(values) == 2: obj = self.strings_to_datetime(values[0], values[1])
        setattr(namespace, self.dest, obj)



