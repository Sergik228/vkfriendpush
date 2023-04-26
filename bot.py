import asyncio
import vk_api
import logging

from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token='токенботатг', parse_mode='HTML')
dp = Dispatcher(bot)

vk_session = vk_api.VkApi(token='токенвкаккаунта')
vk = vk_session.get_api()

friend_ids = [1234, 1234, 1234, 1234, 1234]
friend_statuses = {}

admin_id = 1234

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("https://t.me/+hDc6HaNkf5Q3NzNi")

@dp.message_handler(commands=['status'])
async def status_command_handler(message: types.Message):
    await get_friends_status()

async def get_user_name(user_id):
    user = vk.users.get(user_ids=user_id)
    return user[0]['first_name'] + ' ' + user[0]['last_name']

async def send_notification(user_id: int, status: str):
    user_info = vk.users.get(user_ids=user_id)[0]
    message = f"👤 <a href='vk.com/id{user_id}'>{user_info['first_name']} {user_info['last_name']}</a> {status} в <code>{datetime.now().strftime('%H:%M')}</code>"
    await bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML', disable_web_page_preview=True)

async def check_friends_status():
    while True:
        friends = vk.friends.getOnline()
        for friend_id in friend_ids:
            if friend_id not in friend_statuses:
                friend_statuses[friend_id] = {'status': 'offline', 'last_seen': datetime.now()}
            if friend_id in friends and friend_statuses[friend_id]['status'] == 'offline':
                await send_notification(friend_id, 'появился в сети')
                friend_statuses[friend_id] = {'status': 'online', 'last_seen': datetime.now()}
            elif friend_id not in friends and friend_statuses[friend_id]['status'] == 'online':
                await send_notification(friend_id, 'вышел из сети')
                friend_statuses[friend_id] = {'status': 'offline', 'last_seen': datetime.now()}
        await asyncio.sleep(20)


async def get_friends_status():
    message = ''
    for friend_id in friend_ids:
        if friend_statuses.get(friend_id):
            user_info = vk.users.get(user_ids=friend_id, fields='last_seen,first_name,last_name,online')[0]
            if 'last_seen' in user_info:
                if user_info['online']:
                    status = "<code>Онлайн</code>"
                else:
                    last_seen = datetime.fromtimestamp(user_info['last_seen']['time']).strftime('[%Y-%m-%d | %H:%M]')
                    status = f"<code>Оффлайн</code>\n<b>Был(а) в сети:</b> <code>{last_seen}</code>"
                message += f"👤 <a href='vk.com/id{friend_id}'>{user_info['first_name']} {user_info['last_name']}</a>\n<b>Статус:</b> {status}\n\n"
            else:
                message += f"👤 <a href='vk.com/id{friend_id}'>{user_info['first_name']} {user_info['last_name']}</a>\n<b>Статус:</b> не доступен\n\n"
        else:
            message += f"Пользователь id{friend_id}: не отслеживается\n"
    await bot.send_message(chat_id=admin_id, text=message, disable_web_page_preview=True)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_friends_status())
    executor.start_polling(dp, skip_updates=True)
    loop.run_forever()