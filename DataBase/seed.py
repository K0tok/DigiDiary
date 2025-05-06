from models import *

TABLES = [User, Group, Union, Subject, Homework, Teacher, Timetable, Lesson, UnionMember, UnionGroup]
with db:
    db.drop_tables(TABLES)
    db.create_tables(TABLES)
