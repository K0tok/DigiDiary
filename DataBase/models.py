import peewee as pw

db = pw.SqliteDatabase("DB.db")

class User(pw.Model):               # Пользователи
    id = pw.PrimaryKeyField()
    tgId = pw.IntegerField()
    name = pw.CharField(60)
    created_at = pw.DateTimeField()

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
    tgId = pw.IntegerField()
    name = pw.CharField(60)
    created_by = pw.ForeignKeyField(User)
    invite_code = pw.CharField(100)

    class Meta:
        database = db
        db_table = "unions"


class Subject(pw.Model):            # Предметы
    id = pw.PrimaryKeyField()
    name = pw.CharField(60)

    class Meta:
        database = db
        db_table = "subjects"

class Homework(pw.Model):            # Домашние задания
    id = pw.PrimaryKeyField()
    user_id = pw.ForeignKeyField(User)
    subject_id = pw.ForeignKeyField(Subject)
    due_date = pw.DateTimeField()
    description = pw.CharField()
    created_at = pw.DateTimeField()

    class Meta:
        database = db
        db_table = "homeworks"

class Teacher(pw.Model):              # Преподаватели
    id = pw.PrimaryKeyField()
    name = pw.CharField(60)

    class Meta:
        database = db
        db_table = "teachers"

class Timetable(pw.Model):            # Расписание звонков
    lesson_number = pw.PrimaryKeyField()
    lesson_name = pw.CharField(10)
    time_start = pw.TimestampField()
    time_end = pw.TimestampField()

    class Meta:
        database = db
        db_table = "timetable"


class Lesson(pw.Model):                # Пары
    id = pw.PrimaryKeyField()
    group_id = pw.ForeignKeyField(Group)
    day_of_week = pw.CharField(20)
    subject_id = pw.ForeignKeyField(Subject)
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
    group_if = pw.ForeignKeyField(Group)

    class Meta:
        database = db
        db_table = "unionGroups"
