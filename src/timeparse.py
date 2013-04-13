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
digs = re.compile('(?<!\w)([-+]?\w+)(?![-+\w])')
delta_keys = ('weeks', 'days', 'hours', 'minutes', 'seconds')


class DeltaDateTime:
    """Convert strings to datetime-objects.
    """
    def string_to_delta(self, string):
        """Convert a string to a timedelta-object.
        """
        try: delta = [int(x) for x in digs.findall(string)]
        except: raise ArgumentError(
            self,
            "couldn't parse '{0}' as timedelta".format(string)
            )
        delta = dict(zip(delta_keys[delta_keys.index(self.dest):], delta))
        delta = datetime.timedelta(**delta)
        return delta

    def string_to_time(self, string):
        """Convert a string to a time-object.
        """
        time = [int(x) for x in two.findall(one.sub('0\g<0>', string))]
        try: time = datetime.time(*time)
        except: raise ArgumentError(
            self,
            "couldn't parse '{0}' as time".format(string)
        )
        return time

    def string_to_date(self, string):
        """Convert a string to a date-object.
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
            "couldn't parse '{0}' as date".format(string)
        )
        return date

    def strings_to_datetime(self, datestring, timestring):
        """Convert two string to a datetime-object.
        """
        date = self.string_to_date(datestring)
        time = self.string_to_time(timestring)
        return datetime.datetime.combine(date, time)



class ParseDate(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a date-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        date = self.string_to_date(values)
        setattr(namespace, self.dest, date)


class ParseTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a time-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        time = self.string_to_time(values)
        setattr(namespace, self.dest, time)


class ParseTimeDelta(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a timedelta-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = ' '.join(list(values))
        delta = self.string_to_delta(values)
        setattr(namespace, self.dest, delta)


class ParseDateTime(argparse.Action, DeltaDateTime):
    """Parse a commandline-argument to a datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        date_time = self.strings_to_datetime(values[0], values[1])
        setattr(namespace, self.dest, date_time)


class ParseDateTimeOrTime(argparse.Action, DeltaDateTime):
    """Parse one string to a time-object or two strings to a datetime-object.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1: obj = self.string_to_time(values[0])
        elif len(values) == 2: obj = self.strings_to_datetime(values[0], values[1])
        setattr(namespace, self.dest, obj)

class AppendDateTimeOrTime(ParseDateTimeOrTime):
    """Save parsed time or datetime-objects as list.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1: obj = self.string_to_time(values[0])
        elif len(values) == 2: obj = self.strings_to_datetime(values[0], values[1])
        if getattr(namespace, self.dest): getattr(namespace, self.dest).append(obj)
        else: setattr(namespace, self.dest, [obj])



