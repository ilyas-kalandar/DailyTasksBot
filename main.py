import settings
import logging
import asyncio
import time

from aiogram.types import Message, ContentTypes
from aiogram import Bot, Dispatcher
from keyboards import tasks_keyboard, tasks_keyboard_for_delete, settings_keyboard
from dbcontroller import DBController
from settings import SLEEP_TIME

logging.basicConfig(level=logging.INFO)
bot = Bot(settings.TOKEN)
dispatcher = Dispatcher(bot)
db = DBController(settings.DB_FILENAME)


@dispatcher.message_handler(commands=['start'])
async def say_hello(message: Message):
    await message.answer_sticker(open("stickers/hello.webp", 'rb'))
    await message.answer("Привет, <b>{}</b>! Меня зовут Daily Tasks!\nЯ помогу тебе контролировать твой день!".format
                         (message.from_user.first_name),
                         parse_mode='html')

    if not db.get_user(message.from_user.id):
        await bot.send_message(message.chat.id, "✅ Вы успешно добавлены в базу данных!")
        db.add_account(message.from_user.id)

    text = "Команды бота.\n/list - <b>Вывести список задач</b>\n"
    text += "/delete - <b>Вывести список задач, кликнув по соответсвующей задаче можно ее удалить.</b>\n"
    text += "/settings - <b>Меню настроек</b>\n"
    text += "Для добавления задачи на сегодня, просто <b>отправьте ее название!</b>\n\n"
    text += "Также доступны уведомления о присутствующих задачах каждые 4 часа,"
    text += "их вы можете <b>включить в настройках</b>\n\n"
    text += "В 12 часов ночи, все ваши задачи будут удалены, а незавершенные, будут перенесены.\n"
    text += "Вы можете отрегулировать это поведение в настройках!\n"

    await bot.send_message(message.chat.id, text, parse_mode='html')


@dispatcher.message_handler(commands=['list', 'tasks'])
async def show_tasks(message: Message):
    tasks = db.get_tasks(message.from_user.id)
    if tasks:
        await message.reply("Ваши задания на сегодня!", reply_markup=tasks_keyboard(db.get_tasks(message.from_user.id)))
    else:
        await message.reply("У вас нет задач! Наберите текст задачи и отправьте для добавление, или же отдыхайте :3")


@dispatcher.message_handler(commands='settings')
async def settings(message: Message):
    await message.reply("Вот ваши настройки!",
                        reply_markup=settings_keyboard(db.get_user(message.from_user.id)))


@dispatcher.message_handler(commands=['delete'])
async def show_tasks(message: Message):
    tasks = db.get_tasks(message.from_user.id)
    if tasks:
        await message.reply("Список задач, нажмите на задачу чтобы удалить ее",
                            reply_markup=tasks_keyboard_for_delete(db.get_tasks(message.from_user.id)))
    else:
        await message.reply("Лол, у вас даже задач нет 🤨")


@dispatcher.message_handler(content_types=ContentTypes.TEXT)
async def add_task(message: Message):
    if not message.is_command():
        task = db.get_task(message.from_user.id, message.text)
        if not task:
            db.add_task(message.from_user.id, message.text)
            await message.answer("✅ Новая задача на сегодняшний день успешно добавлена!")
        else:
            await message.answer("Такая задача уже есть, помечу ее невыполненной! 🚩")
            if task.is_completed:
                db.change_task_status(message.from_user.id, message.text)
    else:
        await message.answer("❌ Я не знаю такой команды!")


@dispatcher.callback_query_handler(lambda call: call.data.split()[0] == 'h')
async def handle_task(call):
    message = call.message
    user_id = message.reply_to_message.from_user.id
    task = db.get_task(user_id, call.data[2::])
    if task:
        db.change_task_status(user_id, call.data[2::])
        await bot.edit_message_text(message.text, message.chat.id, message.message_id,
                                    reply_markup=tasks_keyboard(db.get_tasks(user_id)))


@dispatcher.callback_query_handler(lambda call: call.data.split()[0] == 'd')
async def handle_task(call):
    message = call.message
    user_id = message.reply_to_message.from_user.id
    try:
        db.remove_task(user_id, call.data[2::])
    except TypeError:
        await bot.send_message(message.chat.id, "❌ Такой задачи не существует, давайте не будем :3")

    tasks = db.get_tasks(user_id)
    if tasks:
        await bot.edit_message_text(message.text, message.chat.id, message.message_id,
                                    reply_markup=tasks_keyboard_for_delete(db.get_tasks(user_id)))
    else:
        await bot.delete_message(message.chat.id, message.message_id)


@dispatcher.callback_query_handler(lambda call: call.data.startswith("upd_"))
async def update_settings(call):
    message = call.message
    user_id = message.reply_to_message.from_user.id
    if call.data == 'upd_notifies':
        db.change_notifies_status(user_id)

    elif call.data == 'upd_extend':
        db.change_extend_status(user_id)

    await bot.edit_message_text(message.text, message.chat.id, message.message_id,
                                reply_markup=settings_keyboard(db.get_user(user_id)))


async def notify():
    while True:
        for user in db.get_all_users():
            if user.notifies:
                tasks = db.get_tasks(user.user_id)
                for task in tasks:
                    if not task.is_completed:
                        await bot.send_message(user.user_id,
                                               "Привет, у тебя есть нерешенные задачи, я верю что ты сможешь :3")
                        break

        await asyncio.sleep(SLEEP_TIME)  # wait 4 hours


async def delete_all_tasks():
    while True:
        t = time.localtime()
        if t.tm_hour == 12:
            for user in db.get_all_users():
                if user.extend_task:
                    for task in db.get_tasks(user.user_id):
                        if task.is_completed:
                            db.remove_task(user.user_id, task.name)
                else:
                    db.delete_all_tasks(user.user_id)

                await bot.send_message(user.user_id, "Хэй, новый день начался! Пора решать новые задачи!")
                if user.extend_task:
                    await bot.send_message(
                        user.user_id,
                        "Все невыполненные задачи вчерашнего дня перенесены на сегодня, на забывайте!")

        await asyncio.sleep(600)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notify())
    loop.create_task(delete_all_tasks())
    loop.run_until_complete(dispatcher.start_polling())
