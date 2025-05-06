import requests
import json
from datetime import datetime 

NUMERATOR_DATES = ["2025-04-07", "2025-04-21", "2025-05-05", "2025-05-19"]
def is_numerator(current_date):
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

def get_schedule(url, group_name, today_only=False):
    try:
        # Выполняем GET-запрос к указанному URL
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if group_name not in data:
                return f"Группа '{group_name}' не найдена."
            
            schedule = data[group_name]
            days_of_week = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
            current_day = days_of_week[datetime.now().weekday()]
            current_date = datetime.now()
            result = []

            week_index = 0 if is_numerator(current_date) else 1

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
    
