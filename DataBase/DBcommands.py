from .models import *
from datetime import datetime
from playhouse.shortcuts import model_to_dict


def add_bell(lesson_name, time_start, time_end, is_saturday = False):
    try:
        with db:
            bell = Timetable(lesson_name = lesson_name, time_start = time_start, time_end = time_end, is_saturday = is_saturday)
            bell.save()

    except Exception as e:
        print('add_bell error:\n', e)


def add_user(tgId, name = None, created_at = datetime.now()):
    try:
        with db:
            user = User(tgId = tgId, name = name, created_at = created_at)
            user.save()

    except Exception as e:
        print('add_user error:\n', e)

def select_users_tgId():
    try: 
        with db:
            Rows = []
            for u in User.select():
                Rows.append(u.tgId)
            return Rows
    except Exception as e:
        print('select_users_tgId error:\n', e)
        return []

def select_user(tgId):
    try:
        with db:
            return model_to_dict(User.get(User.tgId == tgId))
    except Exception as e:
        print('select_user error:\n', e)
        return []

def update_user(tgId, name = None):
    try:
        with db:
            user = User.get(User.tgId == tgId)
            user.name = name
            user.save()

    except Exception as e:
        print('update_user error:\n', e)

def delete_user(tgId):
    try:
        with db:
            user = User.get(User.tgId == tgId)
            user.delete_instance()
            return f"Пользователь {tgId} удалён."
    except Exception as e:
        print("delete_user error:\n", e)
        return ''
    
def create_group(name):
    try:
        with db:
            group = Group(name = name)
            group.save()

    except Exception as e:
        print('create_group error:\n', e)

def select_group(id):
    try:
        with db:
            return model_to_dict(Group.get(Group.id == id))
    except Exception as e:
        print('select_group error:\n', e)
        return []
    
def select_group_by_name(name):
    try:
        with db:
            return model_to_dict(Group.get(Group.name == name))
    except Exception as e:
        print('select_group_by_name error:\n', e)
        return []
    
def select_groups():
    try: 
        with db:
            groups = [group for group in Group.select().dicts()]
            return groups
    except Exception as e:
        print('select_users_tgId error:\n', e)
        return []
    

def select_unions_tgId():
    try: 
        with db:
            Rows = []
            for u in Union.select():
                Rows.append(u.tgId)
            return Rows
    except Exception as e:
        print('select_unions_tgId error:\n', e)
        return []
    

def create_union(tgId, name, created_by_id):
    try: 
        with db:
            union = Union(tgId = tgId, name = name, created_by_id = created_by_id)
            union.save()
        return True
    except Exception as e:
        print('create_union error:\n', e)
        return False
    

def select_union_groups(union_id):
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


def add_union_to_group(union_id, group_id):
    try:
        with db:
            unionGroup = UnionGroup(union_id = union_id, group_id = group_id)
            unionGroup.save()
    except Exception as e:
        print('add_union_to_group error:\n', e)  


def delete_union_from_group(union_id, group_id):
    try:
        with db:
            unionGroup = UnionGroup.get(UnionGroup.union_id == union_id, UnionGroup.group_id == group_id)
            unionGroup.delete_instance()
            unionGroup.save()
    except Exception as e:
        print('delete_union_from_group error:\n', e)  


def add_user_to_union(user_id, union_id):
    try:
        with db:
            unionMember = UnionMember(user_id = user_id, union_id = union_id)
            unionMember.save()
    except Exception as e:
        print('add_user_to_union error:\n', e)  


def select_user_groups(user_id):
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