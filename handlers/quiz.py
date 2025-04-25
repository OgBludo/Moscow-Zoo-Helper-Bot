# handlers/quiz.py
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import SENDER_EMAIL, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT, SENDER_PASSWORD
from data.animals_data import animal_profiles
from data.quiz_data import quiz

from keyboards.inline import get_result_buttons
from utils.scoring import get_result
from keyboards.inline import get_answer_buttons

router = Router()


class QuizStates(StatesGroup):
    in_quiz = State()
    answering = State()


@router.message(F.text == "🐾 Начать викторину")
async def start_quiz(msg: types.Message, state: FSMContext):
    await state.update_data(user=msg.from_user.username or msg.from_user.full_name)
    await state.update_data(current=0, scores={})
    question = quiz[0]
    text = f"Вопрос 1:\n{question['question']}\n"
    for i, opt in enumerate(question['options'], start=1):
        text += f"{i}. {opt}\n"
    await msg.answer(text, reply_markup=get_answer_buttons(0))
    await state.set_state(QuizStates.answering)


# Новая функция генерации текста вопроса с прогрессом и эмодзи
def format_question_text(index: int, question_data: dict, total: int) -> str:
    emojis = ["🦁", "🐼", "🐘", "🦉", "🐬", "🦓", "🐢"]
    emoji = random.choice(emojis)
    text = f"{emoji} Вопрос {index + 1} из {total}:\n{question_data['question']}\n\n"
    for i, opt in enumerate(question_data['options'], start=1):
        text += f"{i}. {opt}\n"
    return text


@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    _, q_index, option_index = callback.data.split(":")
    q_index = int(q_index)
    option_index = int(option_index)

    data = await state.get_data()
    current = data['current']
    scores = data['scores']
    question = quiz[current]

    # Сохраняем очки
    for animal, points in question['scores'][option_index].items():
        scores[animal] = scores.get(animal, 0) + points

    current += 1
    await callback.answer(text=random.choice([
        "Интересный выбор! 🐾", "Ты знаешь толк в зверях! 🦁", "Отличный ответ! 🐻"
    ]))

    if current < len(quiz):
        await state.update_data(current=current, scores=scores)
        next_q = quiz[current]

        # Перемешиваем варианты
        shuffled = list(zip(next_q['options'], next_q['scores']))
        random.shuffle(shuffled)
        options, scores_list = zip(*shuffled)
        next_q['options'] = options
        next_q['scores'] = scores_list

        text = format_question_text(current, next_q, len(quiz))
        await callback.message.edit_text(text, reply_markup=get_answer_buttons(current))
    else:
        await state.set_state(None)
        await callback.message.edit_text("Спасибо за прохождение! 🐾 Считаем результат...")
        await show_result(callback.message, scores)


async def show_result(msg: types.Message, scores: dict):
    result = get_result(scores)
    profile = animal_profiles.get(result.lower(), {
        "desc": "Это удивительное существо заслуживает внимания и заботы!",
        "care_info": "Ты можешь стать его опекуном и помочь зоопарку."
    })
    try:
        photo = types.FSInputFile(f"images/{result}.jpg")
    except:
        photo = None
    text = (
        f"🎉 Твое тотемное животное — {result.capitalize()}! 🎉\n\n"
        f"{profile['desc']}\n\n"
        f"{profile['care_info']}\n\n"
        f"Узнай больше о программе опеки на нашем сайте или свяжись с нами — мы всегда рады помочь!"
    )
    if photo:
        await msg.answer_photo(photo, caption=text, reply_markup=get_result_buttons(result))

    else:
        await msg.answer(text, reply_markup=get_result_buttons(result))


@router.callback_query(lambda c: c.data == "restart")
async def restart_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(current=0, scores={})
    question = quiz[0]
    text = f"Вопрос 1:\n{question['question']}\n"
    for i, opt in enumerate(question['options'], start=1):
        text += f"{i}. {opt}\n"
    await callback.message.answer(text, reply_markup=get_answer_buttons(0))
    await state.set_state(QuizStates.answering)
    await callback.answer()


# Функция для отправки email
def send_email(subject, body):
    try:
        # Создаем объект сообщения
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject

        # Добавляем текстовое содержимое
        msg.attach(MIMEText(body, "plain"))

        # Настройка SMTP-соединения
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Шифрование
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Логинимся
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())  # Отправляем
        print("Email отправлен успешно!")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")


# Обработчик callback для "Связаться с сотрудником"
@router.callback_query(lambda c: c.data == "contact")
async def contact_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get("user", "Неизвестно")
    scores = data.get("scores", {})
    result = get_result(scores)

    # Создаем текст письма
    subject = f"Результат викторины от пользователя @{user}"
    body = (
        f"Ваш результат: {result.capitalize()}.\n"
        f"(Пользователь: @{user})"
    )

    # Отправляем email
    send_email(subject, body)

    # Ответ пользователю в Telegram
    await callback.message.answer(
        f"Мы отправили информацию на почту!\n Наши сотрудники скоро свяжутся с вами 😊\n"
        f"Также вы сами можете связаться с сотрудником по адресу: zoofriends@moscowzoo.ru\n"
    )
    await callback.answer()


@router.message(F.text == "🌐 Перейти на сайт")
async def go_to_website(msg: types.Message):
    # Ссылка на сайт, который вы хотите отправить
    website_url = "https://moscowzoo.ru"  # Замените на нужную ссылку

    # Отправляем пользователю сообщение с кнопкой, чтобы он мог перейти на сайт
    await msg.answer(
        f"Перейдите по ссылке: {website_url}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти на сайт", url=website_url)]
            ]
        )
    )


@router.message(F.text == "ℹ️ Общая информация")
async def general_info(msg: types.Message):
    # Текст с общей информацией
    info_text = (
        "Добро пожаловать в Московский зоопарк! 🌿\n\n"
        "Здесь вы можете узнать о наших животных, участвовать в викторинах, а также стать опекуном одного из наших питомцев.\n\n"
        "Вы можете:\n"
        "1. Узнать ваше тотемное животное 🐾\n"
        "2. Стать опекуном животного 🤝\n"
        "3. Посетить наш сайт 🌐\n"
        "4. Оставить отзыв 💬\n\n"
        "Если у вас есть вопросы или предложения, мы всегда рады услышать от вас!"
    )

    # Отправляем информацию пользователю
    await msg.answer(
        info_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🌐 Перейти на сайт", url="https://moscowzoo.ru"),
                ]
            ]
        )
    )
