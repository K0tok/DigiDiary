from models import *

TABLES = [User, Group, Union, Subject, Homework, Teacher, Timetable, Lesson, UnionMember, UnionGroup]
with db:
    db.drop_tables(TABLES)
    db.create_tables(TABLES)

    # u1 = User(tgId = 23434,name = 'qwerty',created_at = "2023-05-24")

    # u1.save()