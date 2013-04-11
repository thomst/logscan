import unittest
import datetime
import argparse
from argparse import ArgumentError

from timeparse import DeltaDateTime
from timeparse import AppendDateTimeOrTime
from timeparse import ParseDateTimeOrTime
from timeparse import ParseDateTime
from timeparse import ParseTimeDelta
from timeparse import ParseDate
from timeparse import ParseTime


class DeltaDateTimeTests(unittest.TestCase, DeltaDateTime):
    def setUp(self):
        self.option_strings = ["foo"]

    def test_string_to_date(self):
        today = datetime.date.today()

        self.assertEqual(datetime.date(2013, 10, 20), self.string_to_date('201013'))
        self.assertEqual(datetime.date(2013, 4, 20), self.string_to_date('20.4.13'))

        # depends on actual date...
        self.assertEqual(datetime.date(today.year, 10, 20), self.string_to_date('2010'))
        self.assertEqual(datetime.date(today.year, today.month, 6), self.string_to_date('6'))

    def test_string_to_time(self):
        self.assertEqual(datetime.time(20, 4, 46), self.string_to_time('20:04:46'))
        self.assertEqual(datetime.time(20, 4, 46), self.string_to_time('200446'))
        self.assertEqual(datetime.time(20, 4), self.string_to_time('20:4'))
        self.assertEqual(datetime.time(20), self.string_to_time('20'))

    def test_string_to_delta(self):
        self.dest = "weeks"
        self.assertEqual(datetime.timedelta(weeks=20, days=4, hours=46), self.string_to_delta('20 04 46'))

        self.dest = "days"
        self.assertEqual(datetime.timedelta(days=20, hours=4, minutes=46), self.string_to_delta('20 04 46'))
        self.assertEqual(datetime.timedelta(days=20, hours=4, minutes=46), self.string_to_delta('20,04,46'))
        self.assertEqual(datetime.timedelta(days=20, hours=4, minutes=46), self.string_to_delta('20 04,46'))
        self.assertEqual(datetime.timedelta(days=0, hours=0, minutes=46), self.string_to_delta('0 0 46'))

        self.dest = "minutes"
        self.assertEqual(datetime.timedelta(minutes=46), self.string_to_delta('46 0'))
        self.assertEqual(datetime.timedelta(minutes=1), self.string_to_delta('1,0'))

        self.dest = "days"
        self.assertRaisesRegexp(ArgumentError, '20w 1', self.string_to_delta, '20w 1')
        self.assertRaisesRegexp(ArgumentError, '20 1o', self.string_to_delta, '20 1o')
        self.assertRaisesRegexp(ArgumentError, '20_1', self.string_to_delta, '20_1')
        self.assertRaisesRegexp(ArgumentError, '0_1', self.string_to_delta, '0_1')
        self.assertRaisesRegexp(ArgumentError, 'abc def', self.string_to_delta, 'abc def')
        self.assertRaisesRegexp(ArgumentError, '3 abc', self.string_to_delta, '3 abc')


class TestTimeParser(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()

    def test_ParseTimeDelta(self):
        self.parser.add_argument(
            '--weeks',
            action=ParseTimeDelta,
            nargs='+',
            )
        self.assertEqual(datetime.timedelta(weeks=-20, hours=-4), self.parser.parse_args('--weeks -20 0 -4'.split()).weeks)

    def test_ParseTime(self):
        self.parser.add_argument(
            '--time',
            action=ParseTime,
            nargs='+',
            )
        self.assertEqual(datetime.time(10, 45, 22), self.parser.parse_args('--time 104522'.split()).time)

    def test_ParseDate(self):
        self.parser.add_argument(
            '--date',
            action=ParseDate,
            nargs='+',
            )
        self.assertEqual(datetime.date(2013, 4, 22), self.parser.parse_args('--date 22.4.13'.split()).date)
        self.assertEqual(datetime.date(2013, 4, 22), self.parser.parse_args('--date 220413'.split()).date)
        self.assertEqual(datetime.date(2013, 4, 22), self.parser.parse_args('--date 22042013'.split()).date)

    def test_ParseDateTime(self):
        self.parser.add_argument(
            '--datetime',
            action=ParseDateTime,
            nargs='+',
            )
        self.assertEqual(
            datetime.datetime(2013, 4, 22, 22, 3, 16),
            self.parser.parse_args('--datetime 22.4 220316'.split()).datetime
            )

    def test_ParseDateTimeOrTime(self):
        self.parser.add_argument(
            '--datetime',
            action=ParseDateTimeOrTime,
            nargs='+',
            )
        self.assertEqual(
            datetime.datetime(2013, 4, 22, 22, 3, 16),
            self.parser.parse_args('--datetime 22.4 220316'.split()).datetime
            )
        self.assertEqual(
            datetime.time(22, 3, 16),
            self.parser.parse_args('--datetime 220316'.split()).datetime
            )

    def test_AppendDateTimeOrTime(self):
        self.parser.add_argument(
            '--datetime',
            action=AppendDateTimeOrTime,
            nargs='+',
            )
        self.assertEqual(
            [datetime.time(22, 3, 16), datetime.time(13, 3)],
            self.parser.parse_args('--datetime 220316 --datetime 1303'.split()).datetime
            )


from logscanlib import Log
from logscanlib import RotatedLogs

class LogTestBase:
    def tearDown(self):
        self.log.close()

    def test_base_functionality(self):
        self.assertIsInstance(self.log.start, datetime.datetime)
        self.assertIsInstance(self.log.end, datetime.datetime)
        self.assertGreater(self.log.end, self.log.start)
        self.assertIsInstance(self.log.lines, list)

    def section(self, start, end):
        lines = self.log.get_section(start, end)
        if not lines: return

        first = self.get_linetime(lines[0])
        last = self.get_linetime(lines[-1])
        index1 = self.log.lines.index(lines[0])
        index2 = self.log.lines.index(lines[-1])
        self.assertEqual(lines, self.log.lines[index1:index2+1])
        if start: self.assertTrue(start <=first)
        if end: self.assertTrue(end > last)
        if index1 > 0:
            preceed = self.get_linetime(self.log.lines[index1-1])
            self.assertTrue(preceed < start <= first)
        if index2 + 1 < len(self.log.lines):
            succeed = self.get_linetime(self.log.lines[index2+1])
            self.assertTrue(last < end <= succeed)

    def test_get_section(self):

        delta = datetime.timedelta(minutes=3)

        self.assertEqual(self.log.lines, self.log.get_section())

        self.section(None, None)
        self.section(None, self.log.end)
        self.section(self.log.start, None)
        self.section(self.log.start, self.log.end)
        self.section(self.log.start - delta, self.log.end + delta)
        self.section(self.log.start + delta, self.log.end - delta)
        self.section(self.log.end, None)
        self.assertFalse(self.section(self.log.end, self.log.start))


class LogTest(unittest.TestCase, LogTestBase):
    def setUp(self):
        self.log = Log(open('/var/log/syslog', 'rb'))
        self.get_linetime = self.log._get_linetime


class GzipLogTest(unittest.TestCase, LogTestBase):
    def setUp(self):
        self.log = Log(open('/var/log/syslog.6.gz', 'rb'))
        self.get_linetime = self.log._get_linetime


class RotatedLogsTest(unittest.TestCase, LogTestBase):
    def setUp(self):
        self.log = RotatedLogs(open('/var/log/syslog','rb'))
        self.get_linetime = self.log._files[0]._get_linetime







if __name__ == '__main__':
    unittest.main()
