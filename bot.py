import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters.command import Command
import asyncio
import aiohttp
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = '6871242633:AAFtDye810ejtYdZDxEUc5ABxBXhQTho3Fo'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class SurveyStates(StatesGroup):
    experience = State()
    instrument = State()
    additional_skills = State()
    singing = State()
    lyrics = State()
    composing = State()
    mixing = State()
    live_sound = State()
    demo_link = State()

def create_keyboard(buttons):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button)] for button in buttons],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите вариант",
        is_persistent=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет Давайте соберем информацию о вашем музыкальном опыте.")
    await ask_experience(message, state)

async def ask_experience(message: types.Message, state: FSMContext):
    buttons = ["Только начал", "Меньше 5 лет", "Больше 5 лет", "Всю жизнь"]
    keyboard = create_keyboard(buttons)
    await message.answer("Сколько времени вы занимаетесь музыкой?", reply_markup=keyboard)
    await state.set_state(SurveyStates.experience)

@dp.message(SurveyStates.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await ask_instrument(message, state)

async def ask_instrument(message: types.Message, state: FSMContext):
    buttons = ["Клавиши", "Электро-гитара", "Акустическая гитара", "Бас гитара", "Барабаны", "Другой",
               "Могу петь голосом"]
    keyboard = create_keyboard(buttons)
    await message.answer("На чем вы играете?", reply_markup=keyboard)
    await state.set_state(SurveyStates.instrument)

@dp.message(SurveyStates.instrument)
async def process_instrument(message: types.Message, state: FSMContext):
    await state.update_data(instrument=message.text)
    await ask_additional_skills(message, state)

async def ask_additional_skills(message: types.Message, state: FSMContext):
    await message.answer("Что вы умеете еще помимо основного инструмента?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.additional_skills)

@dp.message(SurveyStates.additional_skills)
async def process_additional_skills(message: types.Message, state: FSMContext):
    await state.update_data(additional_skills=message.text)
    await ask_singing(message, state)

async def ask_singing(message: types.Message, state: FSMContext):
    buttons = ["Да, пою как Jad/Taya с Hillsong", "Нет, никогда не пел, слон на ухо наступил"]
    keyboard = create_keyboard(buttons)
    await message.answer("Вы поете?", reply_markup=keyboard)
    await state.set_state(SurveyStates.singing)

@dp.message(SurveyStates.singing)
async def process_singing(message: types.Message, state: FSMContext):
    await state.update_data(singing=message.text)
    await ask_lyrics(message, state)

async def ask_lyrics(message: types.Message, state: FSMContext):
    buttons = ["Да, пишутся на раз-два", "Нет, даже не знаю с чего начать", "Мечтаю завтра же начать писать альбомы"]
    keyboard = create_keyboard(buttons)
    await message.answer("Вы пишете тексты песен?", reply_markup=keyboard)
    await state.set_state(SurveyStates.lyrics)

@dp.message(SurveyStates.lyrics)
async def process_lyrics(message: types.Message, state: FSMContext):
    await state.update_data(lyrics=message.text)
    await ask_composing(message, state)

async def ask_composing(message: types.Message, state: FSMContext):
    buttons = ["Никогда ранее, Не пробовал (мало опыта)", "Пишу песни как нейронки по 2 в минуту"]
    keyboard = create_keyboard(buttons)
    await message.answer("Вы сочиняете музыку?", reply_markup=keyboard)
    await state.set_state(SurveyStates.composing)

@dp.message(SurveyStates.composing)
async def process_composing(message: types.Message, state: FSMContext):
    await state.update_data(composing=message.text)
    await ask_mixing(message, state)

async def ask_mixing(message: types.Message, state: FSMContext):
    buttons = ["Никогда не нравилось ковыряться в пульте", "Всегда мечтал попробовать и научиться", "Другой ответ"]
    keyboard = create_keyboard(buttons)
    await message.answer("Умеете ли вы сводить готовые дорожки новых песен в аудиоредакторах на постпродакшне?",
                         reply_markup=keyboard)
    await state.set_state(SurveyStates.mixing)

@dp.message(SurveyStates.mixing)
async def process_mixing(message: types.Message, state: FSMContext):
    if message.text == "Другой ответ":
        await message.answer("Пожалуйста, введите ваш ответ:")
        return
    await state.update_data(mixing=message.text)
    await ask_live_sound(message, state)

async def ask_live_sound(message: types.Message, state: FSMContext):
    buttons = ["Да", "Нет", "Другой ответ"]
    keyboard = create_keyboard(buttons)
    await message.answer("Любите ли вы настраивать живой звук на еженедельных оффлайн собраниях/онлайн-трансляциях?",
                         reply_markup=keyboard)
    await state.set_state(SurveyStates.live_sound)

@dp.message(SurveyStates.live_sound)
async def process_live_sound(message: types.Message, state: FSMContext):
    if message.text == "Другой ответ":
        await message.answer("Пожалуйста, введите ваш ответ:")
        return
    await state.update_data(live_sound=message.text)
    await ask_demo_link(message, state)

async def ask_demo_link(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, направьте ссылку на любой сервис, демонстрирующий ваши музыкальные навыки (например, демо песни/альбома).",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.demo_link)

@dp.message(SurveyStates.demo_link)
async def process_demo_link(message: types.Message, state: FSMContext):
    await state.update_data(demo_link=message.text)

    # Получаем все данные
    data = await state.get_data()

    # Формируем итоговое сообщение
    result = "Спасибо за участие в опросе Вот собранная информация:\n\n"
    for key, value in data.items():
        result += f"{key}: {value}\n"

    await message.answer(result)
    await state.clear()

    # Добавляем последний вопрос
    await message.answer(
        "Опрос завершен! Спасибо за уделенное время, и в качестве приятного бонуса предлагаю сгенерировать свою песню в нейросети https://SUNO.COM (переходи по ссылке) и, в помощь, следуй краткой инструкции по генерации https://cpa.rip/services/suno-ai/?ysclid=ly4p8kk8fc852675696#Kak_sozdat_muzyku_s_pomosu_nejroseti, и не забудь порадовать своих друзей новым творением 🙂")

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())
