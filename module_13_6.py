# Задача "Ещё больше выбора"

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ]
    ], resize_keyboard=True
)

choise_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="Calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="Formulas")]
    ], resize_keyboard=True
)


class UserState(StatesGroup):
    sex = State()
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.reply(
        'Привет! Я бот, помогающий твоему здоровью. Нажми кнопку "Рассчитать", чтобы узнать сколько ккал в день тебе нужно употреблять',
        reply_markup=start_menu)

@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Ничего тебе не расскажу)))')
@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию: ', reply_markup=choise_menu)
@dp.callback_query_handler(text='Formulas')
async def get_formulas(call):
    await call.message.answer(
        'Расчет по формуле Миффлина-Сан Жеора для мужчин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст + 5,\n '
        'Расчет по формуле Миффлина-Сан Жеора для женщин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст - 161')
    await call.answer()


@dp.callback_query_handler(text='Calories', state=None)
async def sex_form(call):
    await call.message.answer('Введите свой пол: ')
    await UserState.sex.set()
    await call.answer()


@dp.message_handler(state=UserState.sex)
async def set_age(message: types.Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await message.reply('Введите свой возраст:')
    await UserState.age.set()


# Функция для установки роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply('Введите свой рост (в см):')
    await UserState.growth.set()


# Функция для установки веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply('Введите свой вес (в кг):')
    await UserState.weight.set()


# Функция для расчета и отправки нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    sex = str(data['sex'])
    if sex == 'мужской':
        # Расчет по формуле Миффлина-Сан Жеора для мужчин
        calories = int(10 * weight + 6.25 * growth - 5 * age + 5)
    elif sex == 'женский':
        calories = int(10 * weight + 6.25 * growth - 5 * age - 161)

    await message.reply(f"Ваша норма калорий: {calories} ккал в день")
    await state.finish()



@dp.message_handler()  #этот хендлер лучше ставить в самый конец, иначе он будет перехватывать все остальные
async def all_messages(message):
    print('Получено новое сообщение')
    await message.answer('Введите команду \start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
