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
        return None

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
            return True
    except Exception as e:
        print('add_user_to_union error:\n', e)  
        return False

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
    
def select_union_by_id(id):                                             # Поиск объединения
    try:
        with db:
            return model_to_dict(Union.get(Union.id == id))
    except Exception as e:
        print('select_union_by_id error:\n', e)
        return []

def select_union_by_name(name):                                             # Поиск объединения
    try:
        with db:
            return model_to_dict(Union.get(Union.name == name))
    except Exception as e:
        print('select_union_by_name error:\n', e)
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

def get_union_group_names(union_id):
    try:
        group_ids = select_union_groups(union_id) 
        if not group_ids:
            return ["Без группы"]

        group_names = [select_group(g)['name'] for g in group_ids]
        return group_names
    except Exception as e:
        print("get_union_group_names error:\n", e)
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
    
def remove_user_from_union(user_id, union_id):
    try:
        with db:
            # Находим запись в UnionMember
            member = UnionMember.get((UnionMember.user_id == user_id) & (UnionMember.union_id == union_id))
            member.delete_instance()
            return True
    except UnionMember.DoesNotExist:
        print(f"Пользователь {user_id} не состоит в объединении {union_id}")
        return False
    except Exception as e:
        print("remove_user_from_union error:\n", e)
        return False


def create_homework(user_id, subject, due_date, description, union_id):           # Создание домашнего задания
    try:
        with db:
            homework = Homework(user_id = user_id, subject = subject, due_date = due_date, description = description)
            homework.save()
            unionHomework = UnionHomeworks(union_id = union_id, homework_id = homework.id)
            unionHomework.save()
            return homework.id
    except Exception as e:
        print('create_homework error:\n', e)
        return None

def select_homework(id):
    try:
        with db:
            return model_to_dict(Homework.get(Homework.id == id))

    except Exception as e:
        print('select_homework error:\n', e)
        return None
    
def select_homeworks_by_user(user_id, is_archived=False):
    try:
        with db:
            # Получаем объединения пользователя
            user_unions = [u.union_id for u in UnionMember.select().where(UnionMember.user_id == user_id)]
            if not user_unions:
                return []

            # Получаем ID всех домашних заданий из этих объединений
            homework_relations = UnionHomeworks.select().where(UnionHomeworks.union_id.in_(user_unions))
            homework_ids = [hw.homework_id for hw in homework_relations]
            if not homework_ids:
                return []

            # Получаем статусы выполнения и архивации для пользователя
            statuses = HomeworkStatus.select().where(
                (HomeworkStatus.user_id == user_id)
            )

            status_dict = {status.homework_id: status for status in statuses}

            filtered_homeworks = []
            for homework_id in homework_ids:
                status = status_dict.get(homework_id, None)

                # Если статуса нет — считаем, что задание не архивировано
                if status:
                    if status.is_archived == is_archived:
                        filtered_homeworks.append(homework_id)
                else:
                    # Новых заданий может не быть в архиве
                    if is_archived == False:
                        filtered_homeworks.append(homework_id)

            # Выбираем только подходящие задания
            if not filtered_homeworks:
                return []

            homeworks = list(Homework.select().where(Homework.id.in_(filtered_homeworks)).dicts())
            homeworks_sorted = sorted(homeworks, key=lambda x: x["due_date"])
            return homeworks_sorted
    except Exception as e:
        print('select_homeworks_by_user error:\n', e)
        return []
    
def get_homework_groups(homework_id):
    try:
        relations = UnionHomeworks.select().where(UnionHomeworks.homework_id == homework_id)
        group_names = []
        for rel in relations:
            union_groups = UnionGroup.select().where(UnionGroup.union_id == rel.union_id)
            for ug in union_groups:
                group = Group.get_by_id(ug.group_id) 
                if group:
                    group_names.append(group.name)
        return list(set(group_names)) 
    except Exception as e:
        print('get_homework_groups error:\n', e)
        return []
    
def get_homework_unions(homework_id):
    try:
        with db:
            hw_relations = UnionHomeworks.select().where(UnionHomeworks.homework_id == homework_id)
            union_ids = [r.union_id for r in hw_relations]

            if not union_ids:
                return []

            unions = list(Union.select().where(Union.id.in_(union_ids)).dicts())
            return unions
    except Exception as e:
        print("get_homework_unions error:\n", e)
        return []

def select_homeworks_by_union(union_id, user_id=None, is_archived=False):
    try:
        with db:
            # Получаем все ДЗ из объединения
            relations = UnionHomeworks.select().where(UnionHomeworks.union_id == union_id)
            homework_ids = [r.homework_id for r in relations]
            if not homework_ids:
                return []

            # Если указан пользователь → фильтруем по его статусу
            if user_id:
                statuses = HomeworkStatus.select().where(
                    (HomeworkStatus.homework_id.in_(homework_ids)) &
                    (HomeworkStatus.user_id == user_id) &
                    (HomeworkStatus.is_archived == is_archived)
                )
                filtered_ids = [s.homework_id for s in statuses]
                homeworks = list(Homework.select().where(Homework.id.in_(filtered_ids)).dicts())
            else:
                homeworks = list(Homework.select().where(Homework.id.in_(homework_ids)).dicts())

            homeworks_sorted = sorted(homeworks, key=lambda x: x["due_date"])
            return homeworks_sorted
    except Exception as e:
        print('select_homeworks_by_union error:\n', e)
        return []

def get_homework_relations_by_union(union_id):
    try:
        with db:
            relations = UnionHomeworks.select().where(UnionHomeworks.union_id == union_id).dicts()
            return list(relations)
    except Exception as e:
        print("get_homework_relations_by_union error:\n", e)
        return []
    
def delete_homework(homework_id):
    try:
        with db:
            UnionHomeworks.delete().where(UnionHomeworks.homework_id == homework_id).execute()
            
            homework = Homework.get_or_none(Homework.id == homework_id)
            if homework:
                homework.delete_instance()
                return True
            else:
                print(f"Задание с ID {homework_id} не найдено.")
                return False
    except Exception as e:
        print('delete_homework error:\n', e)
        return False
    
def set_homework_status(homework_id, user_id, is_done):
    try:
        with db:
            status, created = HomeworkStatus.get_or_create(
                homework_id=homework_id,
                user_id=user_id,
                defaults={'is_done': is_done}
            )
            if not created:
                status.is_done = is_done
                status.updated_at = datetime.now()
                status.save()
            return True
    except Exception as e:
        print('set_homework_status error:\n', e)
        return False

def get_homework_status(homework_id, user_id):
    try:
        with db:
            status = HomeworkStatus.get_or_none((HomeworkStatus.homework_id == homework_id) & (HomeworkStatus.user_id == user_id))
            return status.is_done if status else False
    except Exception as e:
        print('get_homework_status error:\n', e)
        return False
    
def archive_homework(homework_id, user_id, is_archived=True):
    try:
        with db:
            status = HomeworkStatus.get((HomeworkStatus.homework_id == homework_id) & (HomeworkStatus.user_id == user_id))
            status.is_archived = is_archived
            status.save()
            return True
    except HomeworkStatus.DoesNotExist:
        print("Статус домашнего задания не найден.")
        return False
    except Exception as e:
        print("archive_homework error:\n", e)
        return False