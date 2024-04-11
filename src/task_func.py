import uuid
from ydb_func import *

from datetime import datetime

#создание задачи
def create_task(user_id, data=None, project_id_flag = False):
    # если пользователь только начал создавать задачу
    if (data == None) and (project_id_flag == False):
        # вносим отметку что юзер создает задачу
        ydb_update_user_data(user_id, user_create_task_flag = True)
        return
    
    # если пользователь внес текст задачи
    elif (data != None) and (project_id_flag == False):
        start = 0
        end = data.find('//')
        task_header = data[start:end]
        
        start = end + 2
        end = len(data)
        task_body = data[start:end]
        task_body = task_body.lstrip()
        task_id = uuid.uuid4()
        task_id = str(task_id)
        ydb_update_user_data(user_id, user_task_id = task_id)
        ydb_update_task_data(task_id, task_owner_id = user_id, task_header = task_header, task_body = task_body)

    # если пользователь выбрал проект, в котором будет находиться задача
    elif project_id_flag == True:
        start = len('create_task_project_id_')
        end = len(data)
        project_id = data[start:end]
        user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
        task_id = user_task_id
        status = 'backlog'
        ydb_update_task_data(task_id, task_project_id = project_id, task_status = status)
        text = 'Задача успешно создана и помещена в "Нераспределённые задачи" выбранного проекта'
        return text


# текст задачи
def build_task_text(user_id, data = None, task_id = None):
    text = ''

    if data != None:
        start = len('task_id_')
        end = len(data)
        task_id = data[start:end]
    
    ydb_update_user_data(user_id, task_id = task_id)
    
    user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
    
    result = ydb_get_task_data(task_id, task_header = True, task_body = True, task_executor_id = True, task_deadline = True, task_urgent_flag = True)
    for item in result:
        task_header = item['task_header']
        task_body = item['task_body']
        task_executor_id = item['task_executor_id']
        task_deadline = item['task_deadline']
        task_urgent_flag = item['task_urgent_flag']
        

    # если роль пользователя Руководитель
    if user_role == 'manager':
        
        text = task_header + '\n\n' 

        if task_urgent_flag == True:
            text = text + 'Внимание, задача срочная! 🚩\n\n'

        text = text + task_body 

        if task_deadline != None:
            deadline_text = deadline_calculator(task_deadline)
            text = text + '\n\n' + deadline_text 

        if task_executor_id != None:
            user_full_name = ydb_get_user_data(task_executor_id)
            text = text + '\n\n' + 'Исполнитель: ' + user_full_name

    # если роль пользователя Исполнитель 
    elif user_role == 'executor':
        deadline_text = deadline_calculator(task_deadline)
        text = task_header + '\n\n' 
        if task_urgent_flag == True:
            text = text + 'Внимание, задача срочная! 🚩\n\n'
        text = text + task_body + '\n\n' + deadline_text

    return text

def deadline_calculator(task_deadline):
    result = datetime.strptime(task_deadline, '%Y-%m-%dT%H:%M:%SZ')
    unix = result.timestamp()
    print(unix)

    date_now = datetime.now()
    unix2 = date_now.timestamp()
    seconds = unix-unix2
    
    task_date = datetime.fromtimestamp(unix).strftime('%d.%m.%Y %H:%M')

    text = 'Выполнить до: ' + task_date + '\n'

    if seconds < 0:
        seconds = abs(seconds)
        text = text + 'Просрочено на: '
    elif seconds > 0:
        text = text + 'Осталось: '  

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24) 
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)

    if days != 0:
        text = text + str(days) + ' д '
    if hours != 0:
        text = text + str(hours) + ' ч '
    text = text + str(minutes) + ' мин'
    return text






def set_deadline(user_id, data):
    start = len('date_')
    end = start + 4
    data_year = data[start:end]

    start = end+1
    end = data.find('_', start)
    data_month = data[start:end]
    if int(data_month) < 10:
        data_month = '0' + str(data_month)

    start = end+1
    end = data.find('_', start)
    data_day = data[start:end]
    if int(data_day) < 10:
        data_day = '0' + str(data_day)

    start = end+1
    end = data.find('_', start)
    data_hour = data[start:end]

    start = end+1
    end = len(data)
    data_minute = data[start:end]

    deadline  = data_year + '-' + data_month + '-' + data_day + 'T' + data_hour + ':' + data_minute + ':00Z'

    user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
    task_id = user_task_id
    ydb_update_task_data(task_id, task_deadline = deadline)
    
    text = build_task_text(user_id, task_id = task_id)
    return text
