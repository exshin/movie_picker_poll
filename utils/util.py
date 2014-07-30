#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    main.py
    ~~~~~~~

    Main application

    :copyright: (c) 2012 by Eugene
    :license: see LICENSE for more details.
"""

import time
import re
import os
from datetime import date
from math import floor
from dateutil import parser
from datetime import datetime

timelog = []
def timefunc(funcname, printing=False):
    """
    usage:
        @timefunc("function name")
    """
    def decorator(f):
        def inner(*args, **kwargs):
            def _log(label, t):
                if printing:
                    print((funcname, label, t))
                timelog.append((funcname, label, t))

            time_start = time.time()
            _log("start", time_start)
            x = f(*args, **kwargs)
            time_end = time.time()
            ttime = time_end - time_start
            _log("finish", ttime)
            return x
        return inner
    return decorator

def utf_fix(word):
    r"""utf_fix takes a word of type str and ignores non-utf-8 characters

    usage:
        >>> utf_fix('example')
        'example \xce\x9b'
    """
    if not word:
        return ''

    try:
        w = word.decode('ascii','ignore')
    except UnicodeEncodeError as e:
        w = word.encode('ascii','ignore').decode('ascii','ignore')

    try:
        w = w.encode('utf-8', 'ignore')
        w = w.decode('latin-1','ignore').encode('utf-8')
    except UnicodeDecodeError as e:
        pass
        
    return w

def float_to_date(floatYear):
    """
    Takes a year as a float and converts it to a date formatted string type
    
    Usage:
        >>> float_to_date(2013.083333333)
        '1/1/2013'
        
    """

    try:
        if floatYear is None:
            return ''
        
        try:
            floatYear = float(floatYear)
        except ValueError as e:
            if floatYear == '':
                pass
            else:
                print("Warning - float_to_date: Can't convert to float", floatYear)
            return ''

        if floatYear == 0:
            return ''

        m = floatYear % 1
        if m == 0:
            return str(int(floor(floatYear)))
        
        monthNum = round(m*12)
        date = str(int(monthNum))+'/1/'+str(int(floor(floatYear)))

        return date
    except TypeError as e:
        print("Warning - float_to_date: TypeError" % floatYear)
        return ''
    

def numbers_only(s):
    """remove non-numeric characters
    
    use cases:
    - normalize phone numbers

    usage:
        >>> numbers_only('+1 (203)-272-2474')
        '12032722474'
    """
    return re.sub("\D", "", s)

def normalize(word):
    """Riviera standard normalization of words

    usage:
        >>> normalize('(foo) bar Inc.;')
        'bar inc.'
    """
    def delsubstr(word, s, e):
        si = word.find(s)
        ei = word.find(e)
        si = 0 if si < 0 else si
        ei = 0 if ei < 0 else ei + len(e)
        return word[:si] + word[ei:]

    word = word.lower()    
    cases = [('&amp;', lambda word, x: word.replace(x, '&')),
             ('  ',    lambda word, x: word.replace(x, ' ')),
             ('\n',    lambda word, x: word.replace(x, '')),
             ('(',     lambda word, x: delsubstr(word, x, ')')),
             ('[',     lambda word, x: delsubstr(word, x, ')')),
             (':',     lambda word, x: word.split(':')[:1][0]),
             (';',     lambda word, x: word.split(';')[:1][0]),
             (',',     lambda word, x: word.split(',')[:1][0])]
    
    for (case, modify) in cases:
        if word.find(case):
            word = modify(word, case)
    return word.strip()

def normurl(url):
    """normalized urls into a standard form:

    usage:
        >>> normurl("http://www.google.com/")
        'google.com'
        >>> normurl("https://www.google.com/")
        'google.com'
        >>> normurl("http://google.com")
        'google.com'
    """
    return str(url).replace('https://','').replace('http://','')\
        .replace('www.','').strip(' ').strip('/')

def get_username():
    """
    finds and returns username of current user
    """

    path = os.getcwd()
    userDict = {'eugene':['eugene','chinveeraphan'],
                'kcaravelli':['kyle','caravelli'],
                'nwesterman':['nick','westerman'],
                'sandy':['sandy'],
                'xcervantes':['ximena','cervantes'],
                'jyeo':['johnny','yeo'],
                'jyim':['josh','yim']
                }

    for user in userDict:
        for username in userDict[user]:
            if username in path:
                u = user
                break

    if u:
        return u
    else:
        return None

def import_log(filename,pathDIR,newNumber,updatePeople,updateEmployment,userName):
    filePath = pathDIR + userName + '_' + 'log.txt'
    with open(filePath, "a") as myfile:
        myfile.write("\n%s|%s|%s|%s|%s" % (filename, str(newNumber), str(updatePeople), str(updateEmployment), str(date.today())))

def fix_duration(duration_string):
    # clean and change duration string to int
    d = duration_string.lower()

    try:
        month = int(re.findall('[0-9]+?',re.findall('[0-9]+? m',d)[0])[0])
        month = month/12.0
    except:
        month = 0.0

    try:
        year = int(re.findall('[0-9]+?',re.findall('[0-9]+? y',d)[0])[0])
    except:
        year = 0.0

    duration = year + month

    return duration

def convert_string_to_date(datestring):
    # converts a date string to a datetime object
    year_pattern = re.compile('[0-9]{4}')
    if '02/' in datestring and len(datestring) == 7:
        datestring = datestring.replace('02/','02/01/')
    if 'present' in datestring.lower():
        date_value = datetime.today()
    elif year_pattern.findall(datestring) and len(datestring) == 4:
        date_value = datetime(int(datestring),1,1)
    else:
        try:
            date_value = parser.parse(datestring)
        except Exception as error:
            print error
            date_value = None
    return date_value

def get_duration(start_date,end_date,display_order=None):
    # get duration (in years) from employment start and end dates
    if display_order:
        if display_order == 1 and not end_date:
            end_date = 'present'
    if start_date and end_date:
        s = convert_string_to_date(start_date)
        e = convert_string_to_date(end_date)
        if s and e:
            dd = e-s
            duration = dd.days/365.0
            return abs(duration)
        else:
            return None
    else:
        return None

if __name__ == "__main__":
    import doctest
    doctest.testmod()
