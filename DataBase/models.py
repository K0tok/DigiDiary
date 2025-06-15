import peewee as pw
import datetime

db = pw.SqliteDatabase("DataBase/DB.db", pragmas={'journal_mode': 'wal'})

class User(pw.Model):               # Пользователи
    id = pw.AutoField()
    tgId = pw.IntegerField(unique=True)
    name = pw.CharField(60)
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        db_table = "users"


class Group(pw.Model):             # Группы
    id = pw.PrimaryKeyField()
    name = pw.CharField()

    class Meta:
        database = db
        db_table = "groups"

class Union(pw.Model):             # Объединения
    id = pw.PrimaryKeyField()
    tgId = pw.IntegerField(unique=True)
    name = pw.CharField(60)
    created_by = pw.ForeignKeyField(User)

    class Meta:
        database = db
        db_table = "unions"

class Homework(pw.Model):            # Домашние задания
    id = pw.PrimaryKeyField()
    user_id = pw.ForeignKeyField(User)
    subject = pw.CharField()
    due_date = pw.DateTimeField()
    description = pw.CharField()
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        db_table = "homeworks"

class HomeworkStatus(pw.Model):
    homework_id = pw.ForeignKeyField(Homework, backref='statuses')
    user_id = pw.ForeignKeyField(User)
    is_done = pw.BooleanField(default=False)
    is_archived = pw.BooleanField(default=False)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        db_table = "homework_status"

class UnionHomeworks(pw.Model):       # Связи ДЗ и объединений
    union_id = pw.ForeignKeyField(Union)
    homework_id = pw.ForeignKeyField(Homework)
    class Meta:
        database = db
        db_table = "unionHomeworks"

class Teacher(pw.Model):              # Преподаватели
    id = pw.PrimaryKeyField()
    name = pw.CharField(60)

    class Meta:
        database = db
        db_table = "teachers"

class Timetable(pw.Model):            # Расписание звонков
    lesson_number = pw.PrimaryKeyField()
    lesson_name = pw.CharField(10)
    time_start = pw.TimeField()
    time_end = pw.TimeField()
    is_saturday = pw.BooleanField(default=False)

    class Meta:
        database = db
        db_table = "timetable"


class Lesson(pw.Model):                # Пары
    id = pw.PrimaryKeyField()
    group_id = pw.ForeignKeyField(Group)
    day_of_week = pw.CharField(20)
    subject = pw.CharField()
    teacher_id = pw.ForeignKeyField(Teacher)
    room = pw.CharField()
    lesson_number = pw.ForeignKeyField(Timetable)

    class Meta:
        database = db
        db_table = "lessons"

class UnionMember(pw.Model):            # Связи объединений и пользователей
    union_id = pw.ForeignKeyField(Union)
    user_id = pw.ForeignKeyField(User)

    class Meta:
        database = db
        db_table = "unionMembers"

class UnionGroup(pw.Model):            # Связи объединений и групп
    union_id = pw.ForeignKeyField(Union)
    group_id = pw.ForeignKeyField(Group)

    class Meta:
        database = db
        db_table = "unionGroups"
