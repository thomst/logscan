logscan
=========

logscan is a command-line-tool to get time-specific access to logfiles.
It can handle rotated and gzipped logfiles or reads from stdin. The log
is automatically checked for different timecodes.


Latest Version
--------------
The latest version of this project can be found at : http://github.com/thomst/logscan.


Installation
------------
* Option 1 : Install via pip ::

    pip install logscan

* Option 2 : If you have downloaded the source ::

    python setup.py install


Documentation
-------------
logscan --help ::

    usage: 
      logscan -h
      logscan [LOGFILE] [OPTIONS]

    description:
      Get time-specific access to logfiles.

      logscan is able to handle rotated and/or gzipped logfiles or to read stdin.
      It supports several formats for time-information in the log, and checks the
      logfiles automatically for them. You can also specify further formats in
      logscan.conf.


    positional argument:
      LOGFILE                   If LOGFILE is missing or '-' stdin is read instead.

    optional arguments:
      -h, --help                print this help message and exit
      -i, --info                print the number of files, the start-time and end-time
      -c, --timecode TIMECODE   use TIMECODE to parse the log-times (e.g. "%Y-%m-%d %H:%M:%S")
      -g, --grep PATTERN        print only lines where PATTERN was found
      -d, --date DATE           print all log-entries of DATE

    arguments for times:
      -d, --date DATE           print all log-entries of DATE
      -t, --time [DATE] TIME    specify a point of time; use it twice to specify
                                a start- and end-time

    argruments for durations:
      -p, --plus [WEEKS] [DAYS] [HOURS] [MINUTES] [SECONDS]
      -m, --minus [WEEKS] [DAYS] [HOURS] [MINUTES] [SECONDS]


    times (DATE and TIME):
      DATE and TIME could be in any format. Logscan tries hard to interpret the input
      as valid date or time.
      If DATE is omitted for --time logscan uses the date of the last log-entry.
      If DATE is incomplete logscan completes it with the year or the year and month
      of the actual date.


    durations:
      To specify a positive duration use --plus, for a negative use --minus.
      All values are interpreted as weeks, days, hours, minutes or seconds -in this
      order starting with days. Alternatively you can flag the values with letters
      matching those keywords.
      So to specify a positive duration of 3 days and 4 minutes you can either do
      "--plus 3 0 4" or --plus 3d 4m.


    Which period to print is defined as follows:
      no times and no duration:         from start to eof
      one time and no duration:         from time to eof
      two times and no duration:        from time-one to time-two
      no times and positive duration:   form start to end of duration
      no times and negative duration:   from begin of duration to eof
      one time and positive duration:   from time to end of duration
      one time and negative duration:   from begin of duration to time


    time-code-formats:
      logscan checks a log-file automatically for these formats:
      %Y-%m-%d %H:%M:%S
      %b %d %X %Y
      %b %d %X
      Also a timestamp as total amount of seconds since epoche (1970-01-01 00:00:00 UTC)
      is supported. logscan expects for it a ten-digit decimal with three decimal-places.
      To specify further format-codes use logscan.conf. logscan uses either the first
      format that fits or an explicitly with --timecode given format.
      A list of all available format-codes can be recieved from 'date --help'.


Contribution
------------
Every kind of feedback is very welcome.


Reporting Bugs
--------------
Please report bugs at github issue tracker:
https://github.com/thomst/timeparse/issues


Author
------
thomst <thomaslfuss@gmx.de>
Thomas Leichtfuß

* http://github.com/thomst
