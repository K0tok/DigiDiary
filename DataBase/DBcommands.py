from .models import *
from datetime import datetime, date
from playhouse.shortcuts import model_to_dict

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