import telebot

TELEGRAM_TOKEN = 'xxxxxxxxxx:xxx'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

from build_date_func import *
from static import *
from task_func import *
from ydb_func import *
from all_keyboards import *

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if 'main_menu' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Проекты:', reply_markup=build_projects_markup(call.from_user.id))
    elif 'task_' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = build_task_text(call.message.chat.id, data = call.data), reply_markup=build_task_markup(call.from_user.id, data = call.data))
    elif 'switch_month_' in call.data:
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=build_days(call.data))
    elif 'day_' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите час:', reply_markup=build_hours(call.data))
    elif 'hour_' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите минуты:', reply_markup=build_minutes(call.data))
    elif 'date_' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=set_deadline(call.message.chat.id, call.data), reply_markup=build_task_markup(call.message.chat.id))
    elif 'set_deadline' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите день:', reply_markup=build_days())
    elif 'status_' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите задачу:', reply_markup=build_task_headers(call.message.chat.id, call.data))
        # если пользователь выбрал к какому проекту будет относиться задача
    elif 'create_task_project_id' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=create_task(call.message.chat.id, data = call.data, project_id_flag = True))
        return
    elif ('project_id_' in call.data) or ('role_manager_' in call.data) or ('role_executor_' in call.data):
        markup = build_task_status_markup(call.message.chat.id, call.data)
        if markup is None:
            bot.answer_callback_query(call.id, 'Нет прав руководителя')
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Задачи:', reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, call.data)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.text == 'Создать задачу':
        create_task(message.chat.id)
        bot.send_message(message.chat.id, create_task_text)
        return
    elif message.text == 'Главное меню':
        bot.send_message(message.chat.id, 'Проекты:', reply_markup=build_projects_markup(message.chat.id))
        return

    # если пользователь ранее решил создать задачу и есть отметка в ydb, забираем его сообщение в качестве текста задачи
    user_task_id, user_full_name, user_role, user_create_task_flag = ydb_get_user_data(message.chat.id)
    print(user_create_task_flag)
    if user_create_task_flag == True:
        ydb_update_user_data(message.chat.id, user_create_task_flag=False)
        create_task(message.chat.id, data = message.text)
        bot.send_message(message.chat.id, 'Выберите проект, к которому относится данная задача:', reply_markup=build_task_projects_markup(message.chat.id))
        return
    else: 
        bot.send_message(message.chat.id, 'О, это ты? Привет!', reply_markup=main_reply_keyboard())
        return

bot.infinity_polling()

