import unittest
import datetime

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
