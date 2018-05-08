                           DISK CLEAN UP (Written on by MySQL DB) and MYSQL Archive DB

1. The Script is run from cron - see file crontab
   Verify the cro setting - (https://crontab.guru/#0_6_*_*_5)

2. I have a Fortinet FAZ, which writes to Fortinet DB at the real time and archives data to its Archive DB called Fortinet_Archive
   Since, The Data is real time and is about internet hits and guest hits, it eats up the disk in just over a week's time 
   My Disk is 1TiB (so, for me it takes just over a week to get it full)

3. THIS IS A PYTHON 3 script (Syntax is of Python 3.x - Refer https://www.python.org/doc/)
 
