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
      logscan [OPTIONS] [LOGFILE]

    description:
      Get time-specific access to logfiles.

      logscan is able to handle rotated and/or gzipped logfiles or to read stdin.
      It supports several formats for time-information in the log, and checks the
      logfiles automatically for them. You can also specify further formats in
      logscan.conf.


    positional arguments:
      LOGFILE                   If LOGFILE is missing or '-' stdin is read instead.

    optional arguments:
      -h, --help                print this help message and exit
      -i, --info                print the number of files, the start-time and end-time
      -c, --timecode TIMECODE   use TIMECODE to parse the log-times (e.g. "%Y-%m-%d %H:%M:%S")
      -g, --grep PATTERN        print only lines where PATTERN was found
      -d, --date DATE           print all log-entries of DATE

    argument for times:
      -t, --time [DATE] TIME    specify a point of time

    argruments for durations:
      -W, --weeks WEEKS [DAYS [HOURS [MINUTES [SECONDS]]]]
      -D, --days DAYS [HOURS [MINUTES [SECONDS]]]
      -H, --hours HOURS [MINUTES [SECONDS]]
      -M, --minutes MINUTES [SECONDS]
      -S, --seconds SECONDS


    times (DATE and TIME):
      If Date is omitted the date of the last log-entry will be taken. The generic
      format for the daytime is HHMMSS. You could also use an arbitrary seperator
      (e.g. HH:MM:SS). Doing so you don't need two- digit-values. Seconds or seconds
      and minutes are not obliging. 0322 will be 03:22:00h or just 3 will be
      03:00:00h. The generic format for the date is DDMM[YY]YY. As well you can use
      a seperator and one- digit-values. Also the year or the year and the month
      could be missing. In that case the date will be completed by the actual year
      and month. Use this option twice to specify two points of time.


    durations:
      durations are specified with all upper-case-letter-options (-W, -D, -H,-M, -S),
      while all specifications are taken together, so that '-D 3 0 25' is the same
      as '-D 3 -M 25'. To specify a retrograde duration use a minus for all values
      (e.g. -D -4 -3 -2).


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


    Please report bugs at https://github.com/thomst/logscan/issues


Reporting Bugs
--------------
Please report bugs at github issue tracker:
https://github.com/thomst/timeparse/issues


Author
------
thomst <thomaslfuss@gmx.de>
Thomas Leichtfuß

* http://github.com/thomst
