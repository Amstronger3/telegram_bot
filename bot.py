from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import config
from SQLighter import SQLighter
from main import list_currencies_from_response_json, make_request_to_convert, \
    check_valid_currency_name, make_request_to_get_graph_for_7_day, get_graph_for_7_day, \
    delete_graph_img_from_local_store

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
db = SQLighter('users')


@dp.message_handler(commands=['list'])
async def get_list_currency(message: types.Message):
    if not db.exist_user(message.from_user.id):
        print(1)
        db.save_person_data(message.from_user.id, list_currencies_from_response_json)
        await message.answer("\n".join(list_currencies_from_response_json))

    else:
        if db.is_update_currency_or_not(message.from_user.id):
            print(2)
            db.update_last_request_data(message.from_user.id, list_currencies_from_response_json)
            await message.answer("\n".join(list_currencies_from_response_json))
        else:
            print(3)
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
    await message.answer('Exchange mode closed.')


@dp.message_handler(commands=['exchange'])
async def exchange_currency(message: types.Message):
    await Form.exchange_currency_from.set()
    await message.answer('Please, enter what currency FROM do you want to change (example: USD, EUR, UAH).')


@dp.message_handler(state=Form.exchange_currency_from)
async def process_currency_to(message: types.Message, state: FSMContext):
    if check_valid_currency_name(message.text):
        print('not curr_from')
        await message.answer(check_valid_currency_name(message.text))
    else:
        print('curr_from')
        async with state.proxy() as data:
            data['currency_from'] = message.text.upper()
        await Form.next()
        await message.answer('Please, enter how much do you want to change?')


@dp.message_handler(state=Form.amount)
async def process_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        print('not amount')
        await message.answer('Please, enter number.')
    else:
        print('amount')
        async with state.proxy() as data:
            data['amount'] = message.text
        await Form.next()
        await message.answer('Please, enter what currency TO do you want to change (example: USD, EUR, UAH).')


@dp.message_handler(state=Form.exchange_currency_to)
async def process_exchange(message: types.Message, state: FSMContext):
    if check_valid_currency_name(message.text):
        await message.answer(check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['currency_to'] = message.text.upper()
            print(2)
            response_from_api = make_request_to_convert(currency_to=data['currency_to'], amount=data['amount'],
                                                        currency_from=data['currency_from'])
            await message.answer(f"{response_from_api} {message.text.upper()}")
        await state.finish()


@dp.message_handler(commands=['history'])
async def history_currency_graph(message: types.Message):
    await Form.base_currency_graph.set()
    await message.answer('Please, enter base currency for graph (example: USD, EUR, UAH).')


@dp.message_handler(state=Form.base_currency_graph)
async def process_base_currency_graph(message: types.Message, state: FSMContext):
    if check_valid_currency_name(message.text):
        await message.answer(check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['base_currency_graph'] = message.text
            await Form.next()
            await message.answer('Please, enter required currency for graph (example: USD, EUR, UAH).')


@dp.message_handler(state=Form.req_currency_graph)
async def process_req_currency_graph(message: types.Message, state: FSMContext):
    if check_valid_currency_name(message.text):
        await message.answer(check_valid_currency_name(message.text))
    else:
        async with state.proxy() as data:
            data['req_currency_graph'] = message.text.upper()
            print(2)
            response_from_api = make_request_to_get_graph_for_7_day(
                base_currency_graph=data['base_currency_graph'],
                req_currency_graph=data['req_currency_graph'])

            name_graph_currency = get_graph_for_7_day(response_from_api)
            await message.answer_photo(photo=open(f"graphs_img/{name_graph_currency}.png", 'rb'))
            await state.finish()
            delete_graph_img_from_local_store(name_graph_currency)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
