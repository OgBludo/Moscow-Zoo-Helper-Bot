from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import logging

router = Router()


class FeedbackStates(StatesGroup):
    waiting_feedback = State()


@router.message(F.text == "💬 Оставить отзыв")
async def ask_feedback(msg: types.Message, state: FSMContext):
    await msg.answer("Пожалуйста, напиши свой отзыв. Мы ценим твое мнение! ✨")
    await state.set_state(FeedbackStates.waiting_feedback)


@router.message(FeedbackStates.waiting_feedback)
async def save_feedback(msg: types.Message, state: FSMContext):
    try:
        user_feedback = msg.text
        user = msg.from_user
        with open("feedback.txt", "a", encoding="utf-8") as f:
            f.write(f"{user.id} ({user.full_name}): {user_feedback}\n")

        logging.info(f"Feedback received from {user.id}: {user_feedback}")
        await msg.answer("Спасибо за отзыв! 😊")
        await state.clear()
    except Exception as e:
        logging.exception("Ошибка при сохранении отзыва")
        await msg.answer("Произошла ошибка при сохранении отзыва.")
