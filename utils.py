#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import datetime
import bizdays
import csv


def get_ultima_data_disponivel_base(path_file_base):
    with open(path_file_base, 'r', encoding='utf8') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data in ['Data', 'dt_referencia']:
                return datetime.date(2010, 1, 1)
            return datetime.datetime.strptime(data[0:10], '%Y-%m-%d').date()


def get_calendar():
    holidays = bizdays.load_holidays('ANBIMA.txt')
    return bizdays.Calendar(holidays, ['Sunday', 'Saturday'])


def isbizday(dt_referencia):
    cal = get_calendar()
    return cal.isbizday(dt_referencia)
