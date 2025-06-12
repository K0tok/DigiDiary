from .models import *
from datetime import datetime
from playhouse.shortcuts import model_to_dict


def add_bell(lesson_name, time_start, time_end, is_saturday = False):   # Добавление звонков
    try:
        with db:
            bell = Timetable(lesson_name = lesson_name, time_start = time_start, time_end = time_end, is_saturday = is_saturday)
            bell.save()

    except Exception as e:
        print('add_bell error:\n', e)


def add_user(tgId, name = None, created_at = datetime.now()):           # Создание пользователя
    try:
        with db:
            user = User(tgId = tgId, name = name, created_at = created_at)
            user.save()

    except Exception as e:
        print('add_user error:\n', e)

def select_users_tgId():                                                # Список всех tgId пользователей
    try: 
        with db:
            Rows = []
            for u in User.select():
                Rows.append(u.tgId)
            return Rows
    except Exception as e:
        print('select_users_tgId error:\n', e)
        return []

def select_user(tgId):                                                  # Поиск пользователя
    try:
        with db:
            return model_to_dict(User.get(User.tgId == tgId))
    except Exception as e:
        print('select_user error:\n', e)
        return []

def update_user(tgId, name = None):                                     # Обновление имени пользователя
    try:
        with db:
            user = User.get(User.tgId == tgId)
            user.name = name
            user.save()

    except Exception as e:
        print('update_user error:\n', e)

def delete_user(tgId):                                                  # Удаление пользователя
    try:
        with db:
            user = User.get(User.tgId == tgId)
            user.delete_instance()
            return f"Пользователь {tgId} удалён."
    except Exception as e:
        print("delete_user error:\n", e)
        return ''

def add_user_to_union(user_id, union_id):                               # Привязка пользователя к объединению
    try:
        with db:
            unionMember = UnionMember(user_id = user_id, union_id = union_id)
            unionMember.save()
    except Exception as e:
        print('add_user_to_union error:\n', e)  

def select_user_unions(user_id):                                        # Список объединений пользователя
    try:
        with db:
            user_unions = UnionMember.select().where(UnionMember.user_id == user_id).dicts()
            return user_unions

    except Exception as e:
        print('select_user_unions error:\n', e)  
        return [] 
         
def select_user_groups(user_id):                                        # Список групп пользователя
    try:
        with db:
            user_unions = UnionMember.select().where(UnionMember.user_id == user_id).dicts()
            user_groups = []

            for u in user_unions:
                union_groups = UnionGroup.select().where(UnionGroup.union_id == u['union_id']).dicts()

                for g in union_groups:
                    user_groups.append(g['group_id'])
            return user_groups

    except Exception as e:
        print('select_user_groups error:\n', e)  
        return []    


def create_group(name):                                                 # Создание группы
    try:
        with db:
            group = Group(name = name)
            group.save()

    except Exception as e:
        print('create_group error:\n', e)

def select_group(id):                                                   # Поиск группы
    try:
        with db:
            return model_to_dict(Group.get(Group.id == id))
    except Exception as e:
        print('select_group error:\n', e)
        return []
    
def select_group_by_name(name):                                         # Поиск группы по названию
    try:
        with db:
            return model_to_dict(Group.get(Group.name == name))
    except Exception as e:
        print('select_group_by_name error:\n', e)
        return []
    
def select_groups():                                                    # Список всех групп
    try: 
        with db:
            groups = [group for group in Group.select().dicts()]
            return groups
    except Exception as e:
        print('select_groups error:\n', e)
        return []
    

def create_union(tgId, name, created_by_id):                            # Создание объединения
    try: 
        with db:
            union = Union(tgId = tgId, name = name, created_by_id = created_by_id)
            union.save()
        return True
    except Exception as e:
        print('create_union error:\n', e)
        return False
    
def update_union(tgId, name = None):                                     # Обновление имени пользователя
    try:
        with db:
            union = Union.get(Union.tgId == tgId)
            union.name = name
            union.save()

    except Exception as e:
        print('update_union error:\n', e)

def select_union(tgId):                                                  # Поиск объединения
    try:
        with db:
            return model_to_dict(Union.get(Union.tgId == tgId))
    except Exception as e:
        print('select_union error:\n', e)
        return []

def select_unions_tgId():                                               # Список tgId всех объединений
    try: 
        with db:
            Rows = []
            for u in Union.select():
                Rows.append(u.tgId)
            return Rows
    except Exception as e:
        print('select_unions_tgId error:\n', e)
        return []
    
def select_union_groups(union_id):                                      # Список групп объединения
    try:
        with db:
            user_groups = []
            union_groups = UnionGroup.select().where(UnionGroup.union_id == union_id).dicts()
            for g in union_groups:
                user_groups.append(g['group_id'])
            return user_groups

    except Exception as e:
        print('select_union_groups error:\n', e)  
        return []

def add_union_to_group(union_id, group_id):                             # Привязка группы к объединению
    try:
        with db:
            unionGroup = UnionGroup(union_id = union_id, group_id = group_id)
            unionGroup.save()
    except Exception as e:
        print('add_union_to_group error:\n', e)  

def delete_union_from_group(union_id, group_id):                        # Отвязка группы от объединения
    try:
        with db:
            unionGroup = UnionGroup.get(UnionGroup.union_id == union_id, UnionGroup.group_id == group_id)
            unionGroup.delete_instance()
            unionGroup.save()
    except Exception as e:
        print('delete_union_from_group error:\n', e)  

def select_union_users(union_id):                                        # Список пользователей в объединении
    try:
        with db:
            union_users = UnionMember.select().where(UnionMember.union_id == union_id).dicts()
            return union_users

    except Exception as e:
        print('select_union_users error:\n', e)  
        return [] 
    

def create_homework(user_id, subject, due_date, description):           # Создание домашнего задания
    try:
        with db:
            homework = Homework(user_id = user_id, subject = subject, due_date = due_date, description = description)
            homework.save()
            return homework.id
    except Exception as e:
        print('create_homework error:\n', e)
        return ''

def select_homework(id):
    try:
        with db:
            return model_to_dict(Homework.get(Homework.id == id))

    except Exception as e:
        print('select_homework error:\n', e)
        return []