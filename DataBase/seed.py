from .models import *
from Functions import get_groups
from .DBcommands import create_group, add_bell
from datetime import time


TABLES = [User, Group, Union, Subject, Homework, Teacher, Timetable, Lesson, UnionMember, UnionGroup]

bells = [
        {
            'lesson_name': 'I',
            'time_start': time(9, 0),
            'time_end': time(10, 20),
            'is_saturday': False
        },
        {
            'lesson_name': 'II',
            'time_start': time(10, 30),
            'time_end': time(11, 50),
            'is_saturday': False
        },
        {
            'lesson_name': 'III',
            'time_start': time(12, 20),
            'time_end': time(13, 40),
            'is_saturday': False
        },
        {
            'lesson_name': 'IV',
            'time_start': time(14, 10),
            'time_end': time(15, 30),
            'is_saturday': False
        },
        {
            'lesson_name': 'V',
            'time_start': time(15, 40),
            'time_end': time(17, 0),
            'is_saturday': False
        },
        {
            'lesson_name': 'VI',
            'time_start': time(18, 0),
            'time_end': time(19, 20),
            'is_saturday': False
        },
        {
            'lesson_name': 'VII',
            'time_start': time(19, 30),
            'time_end': time(20, 50),
            'is_saturday': False
        },
        {
            'lesson_name': 'I',
            'time_start': time(19, 30),
            'time_end': time(20, 50),
            'is_saturday': True
        },
        {
            'lesson_name': 'II',
            'time_start': time(19, 30),
            'time_end': time(20, 50),
            'is_saturday': True
        },
        {
            'lesson_name': 'III',
            'time_start': time(19, 30),
            'time_end': time(20, 50),
            'is_saturday': True
        },
        {
            'lesson_name': 'IV',
            'time_start': time(19, 30),
            'time_end': time(20, 50),
            'is_saturday': True
        }
    ]

with db:
    db.drop_tables(TABLES)
    db.create_tables(TABLES)

    for i in get_groups("https://nti.urfu.ru/api/schedule/nti/1/1/4"):
        create_group(i)

    for bell in bells:
        add_bell(bell['lesson_name'], bell['time_start'], bell['time_end'], bell['is_saturday'])