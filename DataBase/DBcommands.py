from .models import *
from datetime import datetime, date

def add_user(tgId, name = None, created_at = datetime.now()):
    try:
        with db:
            user = User(tgId = tgId, name = name, created_at = created_at)
            user.save()

    except Exception as e:
        print('add_user error:\n', e)

def select_users():
    try: 
        with db:
            Users = User.select()
            for u in Users:
                print( u.id, u.tgId, u.name, u.created_at)
    except Exception as e:
        print('select_users error:\n', e)

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