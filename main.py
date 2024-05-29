import asyncio
import sqlite3

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from db import db

db = db.SQLither(config.DB_NAME)

print(config.ADMINS_ID)


class check_user(BaseMiddleware):
    def __init__(self):
        self.users = {}
        super().__init__()

    async def on_pre_process_message(self, message: Message, *kwargs):
        await self.create_user(message)
        await self.check_username(message)

    async def on_pre_process_callback_query(self, call: CallbackQuery, *kwargs):
        await self.create_user(call)
        await self.check_username(call)

    async def create_user(self, message):
        if not db.get_user(message.from_user.id):
            db.create_user(message.from_user.id, message.from_user.mention, message.from_user.first_name,
                           message.from_user.last_name, 0)

    async def check_username(self, message):
        user_data = db.get_user(message.from_user.id)
        print(user_data['user_name'])
        if user_data:
            if message.from_user.username != user_data["user_name"]:
                db.set_information_user(message.from_user.id, 'user_name', message.from_user.username)
            if message.from_user.first_name != user_data["first_name"]:
                db.set_information_user(message.from_user.id, 'first_name', message.from_user.first_name)
            if message.from_user.last_name != user_data["last_name"]:
                db.set_information_user(message.from_user.id, 'last_name', message.from_user.last_name)


# bot = Bot(token=API_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML', )
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(check_user())


# dp.include_router(router)
# await bot.delete_webhook(drop_pending_updates=True)
# await dp.start_polling(bot,allowed_updates=dp.resolve_used_update_types())


def format(value) -> str:
    try:
        if isinstance(value, float):
            if 0 < value < 1:
                formatted_value = '{:.5f}'.format(value)
            else:
                value = round(value, 2)
                formatted_value = '{:,.2f}'.format(value)
        else:
            formatted_value = '{:,.0f}'.format(value)
        return formatted_value.replace(',', ' ')
    except:
        return value


def is_admin(user_id):
    if user_id in config.ADMINS_ID:
        return True
    return False


@dp.callback_query_handler(text="profile_callback")
# @dp.callback_query_handler(text="profile_callback")
async def profile_callback(call: CallbackQuery):
    await call.message.edit_text(await info_profile(call.from_user.id),
                                 reply_markup=await generate_profile_keyboard(call))
    await call.answer()


async def generate_profile_keyboard(call):
    keyboard = InlineKeyboardMarkup(row_width=3)

    keyboard.add(
        InlineKeyboardButton(text="🏆 Рейтинг", callback_data="top_button")
    )
    return keyboard


async def info_profile(user_id: int):
    user = db.get_user(user_id)
    print(user)
    return (
        f"👤  Profile  <code>{user['user_name']}</code>\n"
        f"🆔  User ID:  <code>{user['user_id']}</code>\n\n"
        f"<b>⭐️Информация:</b>\n"
        f"<b>╰➣🎖 Очки:</b> <code>{format(user['point'])}</code>\n"
    )


@dp.message_handler(commands=['профиль', 'игра', 'start', 'menu', 'меню', 'bot'])
async def profile(message: Message):
    await message.reply(await info_profile(message.from_user.id),
                        reply_markup=await generate_profile_keyboard(message))


@dp.message_handler(commands=['очко'])
async def give_point(message: Message):
    if is_admin(message.from_user.id):
        msg = message.reply_to_message
        args = message.get_args().split()
        try:
            if msg:
                args_user, args_value = msg.from_user.username, args[0]
            else:
                args_user, args_value = args[0][1:], args[1]
        except:
            return await message.reply(f"⭕️  /очко [юзер] [значение]")

        try:
            int(args_value)
        except ValueError:
            return await message.reply(f"⭕️  Значение должно быть числом")

        user = db.get_user_by_user_name(args_user)
        if user is None:
            return await message.reply(f"⭕️  Пользователь не найден")

        db.update_information_user(user['user_id'], "point", args_value)
        last_name_str = user['last_name'] if user['last_name'] is not None else ""

        user_link = f'<a href="tg://user?id={user["user_id"]}">{user["first_name"]} {last_name_str}</a>'

        await message.reply(
            f"✅ Вы успешно выдали пользователю {user_link} -> <code>{args_value}</code> очков.")


@dp.message_handler(commands=['банк', 'рейтинг', 'топ', 'bank', 'rating', 'top', 'leaders', 'лидеры'])
async def get_top(message: Message):
    await message.reply(f"🏆Используйте кнопки ниже🏆", reply_markup=await generate_top_keyboard())


@dp.callback_query_handler(text="top_button")
async def open_case(call: CallbackQuery):
    await call.message.edit_text("🏆Используйте кнопки ниже🏆", reply_markup=await generate_top_keyboard())


async def generate_top_keyboard():
    buttons = [
        InlineKeyboardButton(text="Очки", callback_data="top_point"),
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text="⚙️ Меню", callback_data="profile_callback"))
    return keyboard


async def generate_top_page(attribute, start_index=0):
    users = db.get_users()
    top = ""
    for idx, user in enumerate(users[start_index:start_index + 30]):

        rank = start_index + idx + 1
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        else:
            medal = ""

        icon = ""
        last_name_str = user['last_name'] if user['last_name'] is not None else ""
        user_link = f'<a href="tg://user?id={user["user_id"]}">{user["first_name"]} {last_name_str}</a>'

        top += f"✯ {rank} {medal} {user_link} ➞ <b>{format(user['point'])}</b> очков{icon}\n"
    return top


@dp.callback_query_handler(lambda call: call.data.startswith("top_"))
async def show_top_for_attribute(call: CallbackQuery):
    attribute = call.data.split('_')[1]
    top_text = await generate_top_page(attribute)
    total_users = len(db.get_users())
    keyboard = await generate_pagination_keyboard(attribute, 0, total_users)
    await call.message.edit_text(top_text, reply_markup=keyboard)


async def generate_pagination_keyboard(attribute, start_index, total_users):
    page_size = 30
    current_page = start_index // page_size + 1

    navigation_buttons = []
    if start_index - page_size >= 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"previous_{attribute}_{current_page - 1}"))

    navigation_buttons.append(InlineKeyboardButton(text=f" {current_page}", callback_data="page_number"))

    if start_index + page_size < total_users:
        navigation_buttons.append(
            InlineKeyboardButton(text="Далее ➡️", callback_data=f"next_{attribute}_{current_page + 1}"))

    game_button = [InlineKeyboardButton(text="🏆 Рейтинг", callback_data="top_button")]

    keyboard = InlineKeyboardMarkup()
    keyboard.row(*navigation_buttons)
    keyboard.row(*game_button)

    return keyboard


@dp.callback_query_handler(lambda call: call.data.startswith(("previous_", "next_")), state='*')
async def paginate_top_players(call: CallbackQuery):
    action, attribute, current_page = call.data.split('_')
    current_page = int(current_page)

    page_size = 30
    start_index = page_size * (current_page - 1) if action == "next" else page_size * (current_page - 1)

    top_text = await generate_top_page(attribute, start_index)
    total_users = len(db.get_users())
    print("aa", total_users)
    keyboard = await generate_pagination_keyboard(attribute, start_index, total_users)
    await call.message.edit_text(top_text, reply_markup=keyboard)


async def on_startup(dp, ):
    print("Bot Started")
    loop = asyncio.get_event_loop()


if __name__ == '__main__':
    aiogram.utils.executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
