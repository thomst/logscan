import unittest
import datetime

from timeparse import DeltaDateTime


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


if __name__ == '__main__':
    unittest.main()
