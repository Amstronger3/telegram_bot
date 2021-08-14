from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import config
from SQLighter import SQLighter
import services

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
db = SQLighter('users.db')


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    await message.answer(
        "Hello, I`m Exchange currency bot!\n"
        "I can convert and show history currency for the last 7 days.\n"
        "My commands: /list, /exchange and /history.\n"
        "If you want to stop anything operation - enter /cancel.\n"
        "If you need remind commands - enter /help")


@dp.message_handler(commands=['help'])
async def greeting(message: types.Message):
    await message.answer(
        "/list - Get list currency\n"
        "/exchange - Exchange\n"
        "/history - Get history for the last 7 days\n"
        "/cancel - Cancel current operation\n"
        "/help - Remind commands")


@dp.message_handler(commands=['list'])
async def get_list_currency(message: types.Message):
    if not db.exist_user(message.from_user.id):
        db.save_person_data(message.from_user.id, services.get_list_available_currency())
        await message.answer("\n".join(services.get_list_available_currency()))

    else:
        if db.is_update_currency_or_not(message.from_user.id):
            db.update_last_request_data(message.from_user.id, services.get_list_available_currency())
            await message.answer("\n".join(services.get_list_available_currency()))
        else:
            list_currency_from_user = db.get_list_currency(message.from_user.id)
            db.update_last_request_data(message.from_user.id)
            await message.answer(list_currency_from_user)


class Form(StatesGroup):
    exchange_currency_from = State()
    amount = State()
    exchange_currency_to = State()
    base_currency_graph = State()
    req_currency_graph = State()


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Current operation closed.')


@dp.message_handler(commands=['exchange'])
async def exchange_currency(message: types.Message):
    await Form.exchange_currency_from.set()
    await message.answer('Please, enter what currency FROM do you want to change (Example: UAH)?')


@dp.message_handler(state=Form.exchange_currency_from)
async def process_currency_to(message: types.Message, state: FSMContext):
    if services.check_valid_currency_name(message.text):
        await message.answer(services.check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['currency_from'] = message.text.upper()
        await Form.next()
        await message.answer('Please, enter how much do you want to change?')


@dp.message_handler(state=Form.amount)
async def process_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Please, enter number.')
    else:
        async with state.proxy() as data:
            data['amount'] = message.text
        await Form.next()
        await message.answer('Please, enter what currency TO do you want to change (Example: UAH)?')


@dp.message_handler(state=Form.exchange_currency_to)
async def process_exchange(message: types.Message, state: FSMContext):
    if services.check_valid_currency_name(message.text):
        await message.answer(services.check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['currency_to'] = message.text.upper()
            response_from_api = services.make_request_to_convert(currency_to=data['currency_to'], amount=data['amount'],
                                                                 currency_from=data['currency_from'])
            await message.answer(f"{response_from_api} {message.text.upper()}")
        await state.finish()


@dp.message_handler(commands=['history'])
async def history_currency_graph(message: types.Message):
    await Form.base_currency_graph.set()
    await message.answer('Please, enter base currency for graph (Example: UAH).')


@dp.message_handler(state=Form.base_currency_graph)
async def process_base_currency_graph(message: types.Message, state: FSMContext):
    if services.check_valid_currency_name(message.text):
        await message.answer(services.check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['base_currency_graph'] = message.text
            await Form.next()
            await message.answer('Please, enter required currency for graph (Example: UAH).')


@dp.message_handler(state=Form.req_currency_graph)
async def process_req_currency_graph(message: types.Message, state: FSMContext):
    if services.check_valid_currency_name(message.text):
        await message.answer(services.check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['req_currency_graph'] = message.text.upper()
            response_from_api = services.make_request_to_get_graph_for_7_day(
                base_currency_graph=data['base_currency_graph'],
                req_currency_graph=data['req_currency_graph'])

            name_graph_currency = services.get_graph_for_7_day(*response_from_api)
            await message.answer_photo(photo=open(f"graphs_img/{name_graph_currency}.png", 'rb'))
            await state.finish()
            services.delete_graph_img_from_local_store(name_graph_currency)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
