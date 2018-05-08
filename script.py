#!/usr/bin/python3
############ START Of File ##########################################################################################
# Author: Sulabh Chaturvedi
# Build Date: 4/16/2018
# Revision By: Sulabh Chaturvedi and Date: May 8, 2018
  # Revision Description :
    # Handled Script execution
        #if script run date is less than 7
        #if script run date is less than 7 and onth is January
        #if script run date is less than 7 and Its a New year
        #Script runs every 7 days in cron, so days to be checked are 7 instead of 5
# Task Description: This script cleans up Fortinet Archive DB and MySQL Disk by dropping tables that are older than a week
#####################################################################################################################
import glob
import os
import time
import re
import smtplib
import calendar
####### MySQL Connection ##################
import pymysql.cursors
import pymysql
##########################################

######## Python Logging ######################################################################
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',filename='/var/log/ds3_ds3_FortinetArchiveCleanup.log',filemode='w')
##############################################################################################
connection = pymysql.connect(host='localhost',user='root',password='',db='Fortinet_Archive',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
#find today's date and get a date 7 days before
year = (time.strftime('%Y'))
month = (time.strftime('%m'))
day = (time.strftime('%d'))
day = int(day) - 7
month = int(month)
year = int(year)
############### Handling of dates less than and equal to 7th, In this case dates need to traverse a month before the current ######################
lastDayOfPreviousMonth = calendar.monthrange(int(year),int(month) - 1)[1]
if day == 0:
    day = lastDayOfPreviousMonth
    if month == 1: # If Month is Jan and date is 5, we need to clean up previous year files of Dec month
        month = 12
        year-=1
    else:
        month-=1
elif day < 0:
    day+=lastDayOfPreviousMonth
    if month == 1:
        month = 12
        year-=1
    else:
        month-=1
###############################################################
logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Drop Tables from 01:'+str(month)+':'+str(year)+'until '+str(day)+':'+str(month)+':'+str(year))

# Logic #####################################################################################
#     1. find date 7 days before with format 'YYYYMMDD' as this is how tables are named in DB
#     2. loop through the 1st of the month till date as above
#     3. Outfile for each day - /tmp/dropQueries_FortinetArchive"+year+month+day+".sql
##################################################################################################################
for i in range(1,day+1):
    j = str(i)
    if(len(j) == 1):
        j = '0'+j
    fstr = str(year)+'0'+str(month)+j
    logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Generating out file for filename '+fstr)
    sql = "SELECT CONCAT('DROP TABLE ', TABLE_NAME , ';') FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%"+fstr+"%' INTO OUTFILE '/tmp/dropQueries_FortinetArchive"+fstr+".sql'"
    try:
        cursor.execute(sql)
        connection.commit()
    except:
        logging.error('Unable to execute sql, please contact administrator')
        logging.debug('Unable to execute sql, please contact administrator')
        os.system("mailx -s [CRITICAL]01app07-Fortinet_Archive_Cleanup_[UN]Successfull schaturvedi@networks.com")
        exit()

## Logic #####################################################################################
#     1. Goto Dir /tmp/dropQueries_FortinetArchive/ and find all .sql files
#     2. Run the SQL queries in the files on mysqlDB, this will delete the tables from Fortinet Archive DB and clean up the Disk
#################################################################################################################################
os.chdir(r'/tmp')
for filename in glob.iglob('dropQueries_FortinetArchive*.sql'):
    os.system(r"sed -i 's/DROP TABLE /DROP TABLE `/g' "+filename)
    os.system(r"sed -i 's/;/`;/g' "+filename)
    with open(filename,'r') as file:
        for line in file:
            try:
                cursor.execute(line)
                connection.commit()
            except pymysql.err.InternalError as e:
                code, msg = e.args
                if code == 1051:
                    logging.debug(msg)
    file.close()
    logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Dropped Tables for OutFile = /tmp/'+filename)

# Close DB Connections
logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Closing MySQL Connections')
cursor.close()
connection.close()
logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Closed MySQL Connections')

#Notify
SERVER = "localhost"
FROM = "01APP07"
TO = ["Team@yourdomain.com"]
SUBJECT = "Task Completion Notification - DS3 Fortinet Archive DB and Disk Cleanup Successfull"
TEXT = "LOGFILE = /var/log/ds3_FortinetArchiveCleanup.log"
message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
server = smtplib.SMTP('mailhost')
server.set_debuglevel(3)
server.sendmail(FROM, TO, message)
server.quit()
logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'Notified SDO')

#Clean /tmp dir
os.system(r'rm -rf /tmp/dropQueries_FortinetArchive*')
logging.debug(time.strftime('%Y:%m:%d:%H:%M:%S')+'/tmp dir clean up complete, exit')
#End of File

