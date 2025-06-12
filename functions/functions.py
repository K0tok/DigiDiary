import requests
import json
from datetime import datetime 
from DataBase import select_group, select_user, select_union, select_user_unions, select_union_groups, select_group

NUMERATOR_DATES = ["2025-04-07", "2025-04-21", "2025-05-05", "2025-05-19"]
def is_numerator(current_date = datetime.now()):
    return current_date.strftime("%Y-%m-%d") in NUMERATOR_DATES

def get_groups(url):
    try:
        # Выполняем GET-запрос к указанному URL
        response = requests.get(url)
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            # Парсим JSON-ответ
            data = response.json()
            
            # Извлекаем названия групп (ключи верхнего уровня)
            group_names = list(data.keys())
            return group_names
        else:
            print(f"Ошибка при запросе: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        return []

def get_schedule(url, group_id, isNumerator, today_only=False):
    try:
        # Выполняем GET-запрос к указанному URL
        response = requests.get(url)
        
        group_name = select_group(group_id)['name']

        if response.status_code == 200:
            data = response.json()
            
            if group_name not in data:
                return f"Группа '{group_name}' не найдена."
            
            schedule = data[group_name]
            days_of_week = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
            current_day = days_of_week[datetime.now().weekday()]
            result = []

            if isNumerator == -1:
                if is_numerator():
                    week_index = 0
                else:
                    week_index = 1
            elif isNumerator == 1:
                week_index = 1
            elif isNumerator == 0:
                week_index = 0

            if today_only:
                result.append(f"Расписание для группы <b>'{group_name}'</b> на <i>{current_day}</i>:")
                if current_day in schedule[week_index]:
                    day_schedule = schedule[week_index][current_day]
                    result.append(f"<blockquote><i>{current_day}</i>:")
                    for num, lessons in day_schedule.items():
                        result.append(f"<b>{num}</b>:")
                        for lesson in lessons:
                            result.append(f"  - {lesson['n']} (ауд. <b>{lesson['a']}</b>, преп. <b>{lesson['p']}</b>)")
                    result.append(f"</blockquote>")

                else:
                    result.append("\nСегодня нет пар!")
            else:
                result.append(f"Расписание для группы <b>'{group_name}'</b> на неделю ({'<i>числитель</i>' if week_index == 0 else '<i>знаменатель</i>'}):")
                for day_of_week, day_schedule in schedule[week_index].items():
                    result.append(f"<blockquote expandable><i>{day_of_week}</i>:")
                    for num, lessons in day_schedule.items():
                        result.append(f"<b>{num}</b>:")
                        for lesson in lessons:
                            result.append(f"  - {lesson['n']} (ауд. <b>{lesson['a']}</b>, преп. <b>{lesson['p']}</b>)")
                    result.append(f"</blockquote>")
            
            return "\n".join(result)
        else:
            return f"Ошибка при запросе: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Произошла ошибка при выполнении запроса: {e}"
    
def create_user_name(first_name, last_name, username):
    user_first_name = first_name if first_name != None else ""
    user_last_name = last_name if last_name != None else ""
    user_name = user_first_name + user_last_name if user_first_name + user_last_name != "" else username
    return user_name

def create_profile_message(tgId):
    if tgId > 0:
        user = select_user(tgId)
        result = ["👤 Ваш профиль\n", ]
        result.append(f"├ 🆔ID: {tgId}")
        result.append(f"├ Имя: {user['name']}")
        result.append(f"└ Дата регистрации: {user['created_at']}")

        result.append("\nВаши объединения:")
        user_unions = select_user_unions(tgId)
        if len(user_unions) == 0:
            result.append("У вас нет объединений")
        else:
            for u in user_unions:
                union_groups = []
                for g in select_union_groups(u['id']):
                    union_groups.append(select_group(g)['name'])
                result.append(f" - {select_union(u['union_id'])['name']}: {', '.join(union_groups)}")

        return "\n".join(result)
    else:
        union = select_union(tgId)
        result = ["👤 Профиль группы"]
        result.append(f"├ 🆔ID: {tgId}")
        result.append(f"├ Название: {union['name']}")
        result.append(f"└ Создатель: {union['created_by']['name']}")

        result.append("\nГруппы:")
        union_groups = []
        for g in select_union_groups(union['id']):
            union_groups.append(select_group(g)['name'])
        if union_groups:
            result.append(f" - {', '.join(union_groups)}")
        else:
            result.append(f" - Объединение пока что не закреплено за группой")

        return "\n".join(result)
    
def homework(user_id = None, subject = None, due_date = None, description = None):
    homework = {
        "user_id" : user_id,
        "subject" : subject,
        "due_date" : due_date,
        "description" : description
    }
    return homework

def is_valid_date(date_str):
    formats = {
        "%Y-%m-%d": "YYYY-MM-DD",
        "%d.%m.%Y": "DD.MM.YYYY",
        "%Y/%m/%d": "YYYY/MM/DD",
        "%d/%m/%Y": "DD/MM/YYYY",
        "%d-%m-%Y": "DD-MM-YYYY",
        "%Y.%m.%d": "YYYY.MM.DD"
    }

    for fmt in formats:
        try:
            due_date = datetime.strptime(date_str, fmt).date()  # Получаем только дату
            if due_date < datetime.now().date():
                return False, "Дата не может быть раньше сегодняшней."
            return True, due_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    supported = ", ".join(set(formats.values()))
    return False, f"Неверный формат даты. Используйте один из: {supported}"