import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from Garbage import get_results_photo2
from Video_moment import extract_frames, save_video
import cv2

TOKEN = "7084278045:AAF2Nc-mLlUz-Noz-9l6DtlA-GhwV9WhhIg"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_data = {}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "photo": None,
            "video": None
        }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Поменять фото")
    btn2 = types.KeyboardButton("Результат фото")
    btn3 = types.KeyboardButton("Поменять видео")
    btn4 = types.KeyboardButton("Результат видео")
    markup.add(btn1, btn3, btn2, btn4)
    await message.answer(f"Привет, {message.from_user.first_name}! Жду от тебя фото или видео qr-кода :)", reply_markup=markup)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    photo = await message.photo[-1].download(f'photo_{user_id}.jpg')
    user_data[user_id]["photo"] = photo
    await message.answer('Фотография сохранена')

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    video = await message.video.download(f'video_{user_id}.mp4')
    user_data[user_id]["video"] = video
    await message.answer('Видео сохранено')

@dp.message_handler(text="Поменять фото")
async def change_photo(message: types.Message):
    await message.answer("Жду от тебя фото qr-кода :)")

@dp.message_handler(text="Поменять видео")
async def change_video(message: types.Message):
    await message.answer("Жду от тебя видео qr-кода :)")

@dp.message_handler(text="Результат видео")
async def result_video(message: types.Message):
    user_id = message.from_user.id
    video_path = f'video_{str(user_id)}.mp4'
    result =  await extract_frames(video_path)
    frames, fps, size, fourcc = result
    output_path = f'9999_{user_id}.mp4'
    await save_video(frames, output_path, fps, size, fourcc)
    with open(output_path, 'rb') as video:
        await message.answer_video(video)

@dp.message_handler(text="Результат фото")
async def result_photo(message: types.Message):
    user_id = message.from_user.id
    photo_path = f'photo_{str(user_id)}.jpg'
    result = await get_results_photo2(cv2.imread(photo_path))
    answers, img = result
    height, width = img.shape[:2]
    img = cv2.resize(img, (width // 2, height // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'image_to_show_{user_id}.jpg', img)
    with open(f'image_to_show_{user_id}.jpg', 'rb') as img_file:
        await message.answer_photo(img_file)
    await message.answer(str(answers[:]))

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())