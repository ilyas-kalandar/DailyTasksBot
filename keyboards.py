from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def gen_keyboard(tasks, callback_data):
    """Generate keyboard with your callback_data"""
    keyboard = InlineKeyboardMarkup()

    for task in tasks:
        keyboard.add(
            InlineKeyboardButton(
                ('✅ ' if task.is_completed else '❌ ') + task.name,
                callback_data=callback_data + ' ' + task.name
            )
        )

    return keyboard


def tasks_keyboard(tasks):
    """Return a InlineKeyboard object for show tasks"""
    return gen_keyboard(tasks, 'h')


def tasks_keyboard_for_delete(tasks):
    """ Return a InlineKeyboard object for deleting..."""
    return gen_keyboard(tasks, 'd')


def settings_keyboard(user):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "🔕 Выключить уведомления" if user.notifies else "🔔 Включить уведомления",
        callback_data="upd_notifies"
    ))

    keyboard.add(InlineKeyboardButton(
        "❌ Выключить перенос невыполненных задач" if user.extend_task else "🔄 Включить перенос невыполненных задач",
        callback_data="upd_extend"
    ))

    return keyboard
