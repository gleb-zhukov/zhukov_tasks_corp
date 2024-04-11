from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from ydb_func import *

# клавиатура выбора проекта к которому относится задача (при создании задачи)
def build_task_projects_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    project_id, project_name = ydb_get_projects_by_owner_id(user_id)
    
    for i in range(0, len(project_id)):
        callback = 'create_task_project_id_' + project_id[i]
        markup.add(InlineKeyboardButton(project_name[i], callback_data=callback))
    return markup

# клавиатура задачи
def build_task_markup(user_id, data = None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    # если task_id можно вытащить из callback data - вытаскиваем, иначе - берём из строки юзера в ydb
    if data == None:
        user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
        task_id = user_task_id
    elif data != None:
        start = len('task_id_')
        end = len(data)
        task_id = data[start:end]
        user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
    
    
    task_header, task_body, task_executor_id, task_deadline, task_urgent_flag, task_status, task_project_id, task_owner_id = ydb_get_task_data(task_id)

    # если роль пользователя Руководитель
    if user_role == 'manager':
        if task_status == 'backlog':
            # добавляем клавишу отправки исполнителю только если есть исполнитель и дедлайн
            if (task_executor_id != None) and (task_deadline != None):
                markup.add(InlineKeyboardButton('Отправить исполнителю', callback_data='set_status_todoNext'))
                markup.add(InlineKeyboardButton('Отправить исполнителю (срочное)', callback_data='set_status_todoUrgent'))
            markup.add(InlineKeyboardButton('Назначить дедлайн', callback_data='set_deadline'))
            markup.add(InlineKeyboardButton('Назначить исполнителя', callback_data='set_executor'))
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'todoNext') or (task_status == 'todoUrgent'):
            markup.add(InlineKeyboardButton('Напомнить исполнителю', callback_data='send_notification_to_executor'))
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'inProgress'):
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'readyToRewiew'):
            markup.add(InlineKeyboardButton('Задача выполнена', callback_data='set_status_done'))
            markup.add(InlineKeyboardButton('Отправить на обсуждение', callback_data='set_status_discuss'))
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'discuss'):
            markup.add(InlineKeyboardButton('Задача выполнена', callback_data='set_status_done'))
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'blocked'):
            markup.add(InlineKeyboardButton('Отправить исполнителю', callback_data='set_status_todoNext'))
            markup.add(InlineKeyboardButton('Отправить исполнителю (срочное)', callback_data='set_status_todoUrgent'))
            markup.add(InlineKeyboardButton('Удалить задачу', callback_data='delete_task'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))

    # если роль пользователя Исполнитель        
    elif user_role == 'executor':
        if (task_status == 'todoNext') or (task_status == 'todoUrgent'):
            markup.add(InlineKeyboardButton('Взять в работу', callback_data='set_status_inProgress'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'inProgress'):
            markup.add(InlineKeyboardButton('Задача готова к ревью', callback_data='set_status_readyToRewiew'))
            if task_urgent_flag == False:
                callback == 'set_status_todoNext'
            elif task_urgent_flag == True:
                callback == 'set_status_todoUrgent'
            markup.add(InlineKeyboardButton('Задача не в работе', callback_data=callback))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'readyToRewiew') or (task_status == 'discuss'):
            markup.add(InlineKeyboardButton('Забрать на доработку', callback_data='set_status_inProgress'))
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))
        elif (task_status == 'blocked'):
            callback = 'status_' + task_status + '_' + task_project_id
            markup.add(InlineKeyboardButton('Назад', callback_data=callback))

    return markup

def main_reply_keyboard():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
    markup.add(KeyboardButton("Главное меню"),KeyboardButton("Создать задачу"))
    return markup


# клавиатура выбора проекта (главное меню)
def build_projects_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    project_id, project_name = ydb_get_projects_by_user_id(user_id)
    
    for i in range(0, len(project_id)):
        callback = 'project_id_' + project_id[i]
        markup.add(InlineKeyboardButton(project_name[i], callback_data=callback))
    return markup

# клавиатура выбора статуса задач
def build_task_status_markup(user_id, data):

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    if 'role_manager_' in data:
        start = len('role_manager_')
        end = len(data)
        project_id = data[start:end]
        project_name, project_owner_id = ydb_get_project_data(project_id)
        if project_owner_id == user_id:
            user_role = 'manager'
            ydb_update_user_data(user_id, user_role=user_role)
        else:
            return

    elif 'role_executor_' in data:
        start = len('role_executor_')
        end = len(data)
        project_id = data[start:end]
        user_role = 'executor'
        ydb_update_user_data(user_id, user_role=user_role)

    elif 'project_id_' in data:
        start = len('project_id_')
        end = len(data)
        project_id = data[start:end]
        user_role = 'executor'
        ydb_update_user_data(user_id, user_role=user_role)

    # если роль пользователя Руководитель
    if user_role == 'manager':
        callback = 'status_backlog_' + project_id
        markup.add(InlineKeyboardButton('Нераспределённые 🌐', callback_data=callback))
        callback = 'status_todoNext_' + project_id
        markup.add(InlineKeyboardButton('Не начатые 📩', callback_data=callback))
        callback = 'status_urgent_' + project_id
        markup.add(InlineKeyboardButton('Не начатые срочные 🚩', callback_data=callback))
        callback = 'status_inProgress_' + project_id
        markup.add(InlineKeyboardButton('В работе 🧬', callback_data=callback))
        callback = 'status_RTR_' + project_id
        markup.add(InlineKeyboardButton('Готовые к ревью ☑️', callback_data=callback))
        callback = 'tatus_discuss_' + project_id
        markup.add(InlineKeyboardButton('На обсуждении ⚖️', callback_data=callback))
        callback = 'status_blocked_' + project_id
        markup.add(InlineKeyboardButton('На паузе ⏸', callback_data=callback))
        callback = 'status_done_' + project_id
        markup.add(InlineKeyboardButton('Архив', callback_data=callback))
        callback = 'role_executor_' + project_id
        markup.add(InlineKeyboardButton('Меню исполнителя', callback_data=callback))
        callback = 'main_menu'
        markup.add(InlineKeyboardButton('Назад', callback_data=callback))

    # если роль пользователя Исполнитель        
    elif user_role == 'executor':
        callback = 'status_todoNext_' + project_id
        markup.add(InlineKeyboardButton('Новые 📩', callback_data=callback))
        callback = 'status_urgent_' + project_id
        markup.add(InlineKeyboardButton('Новые срочные 🚩', callback_data=callback))
        callback = 'status_inProgress_' + project_id
        markup.add(InlineKeyboardButton('В работе 🧬', callback_data=callback))
        callback = 'status_RTR_' + project_id
        markup.add(InlineKeyboardButton('Готовые к ревью ☑️', callback_data=callback))
        callback = 'status_discuss_' + project_id
        markup.add(InlineKeyboardButton('На обсуждении ⚖️', callback_data=callback))
        callback = 'status_blocked_' + project_id
        markup.add(InlineKeyboardButton('На паузе ⏸', callback_data=callback))
        callback = 'status_done_' + project_id
        markup.add(InlineKeyboardButton('Архив', callback_data=callback))
        callback = 'role_manager_' + project_id
        markup.add(InlineKeyboardButton('Меню руководителя', callback_data=callback))
        callback = 'main_menu'
        markup.add(InlineKeyboardButton('Назад', callback_data=callback))
    return markup

def build_task_headers(user_id, data):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    start = len('status_')
    end = data.find('_', start)
    status = data[start:end]

    start = end + 1
    end = len(data)
    project_id = data[start:end]

    user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(user_id)
    if user_role == 'executor':
        task_id, task_header = ydb_get_tasks_by_status_project_and_executor(task_executor_id = user_id, task_status = status, task_project_id = project_id)
    elif user_role == 'manager':
        task_id, task_header = ydb_get_tasks_by_status_project_and_owner(task_owner_id = user_id, task_status = status, task_project_id = project_id)

    for i in range(0, len(task_id)):
        callback = 'task_id_' + task_id[i]
        markup.add(InlineKeyboardButton(task_header[i], callback_data=callback))
    callback = 'project_id_' + project_id
    markup.add(InlineKeyboardButton('Назад', callback_data=callback))
    return markup
