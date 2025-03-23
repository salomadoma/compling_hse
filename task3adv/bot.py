# Бот обрабатывает faq.json

!wget -O faq.json https://raw.githubusercontent.com/vifirsanova/compling/refs/heads/main/tasks/task3/faq.json

import json

with open('faq.json', 'r') as file:
    data = json.load(file)

print(data)

2. Бот выбирает наиболее подходящий ответ на вопросы пользователя на основе оценки семантического сходства

# Загружаем библиотеки для векторизации и оценки косинусного сходства
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Списки вопросов
faq_questions = []
for pares in data.values():
    for pare in pares:
        faq_questions.append(pare['question'])

faq_answers = []
for pares in data.values():
    for pare in pares:
        faq_answers.append(pare['answer'])

# TF-IDF преобразование
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(faq_questions)


def tfidfvectorizer(query):
    # Преобразуем запрос в вектор
    query_vec = vectorizer.transform([query])
    # Вычисляем косинусное сходство
    similarities = cosine_similarity(query_vec, tfidf_matrix)
    # Ищем индекс наиболее близкого вопроса на основе косинусного сходства
    best_match_idx = similarities.argmax()
    best_answer = faq_answers[best_match_idx]
    return best_answer

# Загрузка Word2Vec из Gensim
import gensim
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Подгружаем Word2Vec
sentences = [q.split() for q in faq_questions]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Функция для усреднения векторов слов в вопросе
def sentence_vector(sentence, model):
    words = sentence.split()
    vectors = [model.wv[word] for word in words if word in model.wv]
    return np.mean(vectors, axis=0) # Берем среднее значение по всем векторам, чтобы одно предложение представлял один вектор

# Векторизуем вопросы
faq_vectors = np.array([sentence_vector(q, model) for q in faq_questions])

def word2vec(query):
    query_vector = sentence_vector(query, model).reshape(1, -1)
    # Оценка косинусного сходства
    similarities = cosine_similarity(query_vector, faq_vectors)
    best_match_idx = similarities.argmax()
    best_answer = faq_answers[best_match_idx]
    return best_answer

3. Кнопки "О компании" и "Пожаловаться"

!pip install aiogram -q

# Импортируем необходимые модули
from aiogram import Bot, Dispatcher, types  # Основные классы для работы с ботом
import logging  # Логирование для отслеживания работы бота
import asyncio  # Модуль для работы с асинхронным кодом
import sys  # Используется для работы с системными вызовами
from aiogram.filters import Command # Модуль для определения команд
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # Модули для кнопок

# Настраиваем логирование, чтобы видеть информацию о работе бота в консоли
logging.basicConfig(level=logging.INFO)
# Создаем объект диспетчера, который управляет входящими сообщениями и командами
dp = Dispatcher()
bot = Bot(token='7566298370:AAFH0dScGj4oS01j0d6wtsXJgkde3_14AM8') # Токен API бота (его нужно заменить на реальный токен, полученный у BotFather)

# Создаём список кнопок для клавиатуры
kb = [
    [
        KeyboardButton(text="О компании"), # Кнопка для запроса информации о компании
        KeyboardButton(text="Пожаловаться")  # Кнопка для отправки жалобы
    ]
]

# Создаём объект клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=kb, # Передаём список кнопок
    resize_keyboard=True, # Уменьшаем клавиатуру под размер экрана
    input_field_placeholder="Выберите действие" # Текст-подсказка в поле ввода
    )


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот, который может отвечать на частые вопросы.", reply_markup=keyboard) # Отправляем сообщение с клавиатурой в команду start

# Обрабатываем нажатие кнопки "О компании"
@dp.message(lambda message: message.text == "О компании") # Фильтр для сообщений с текстом "О компании"
async def about_bot(message: types.Message):
    await message.answer("Наша компания занимается доставкой товаров по всей стране.")

# Обрабатываем нажатие кнопки "Пожаловаться"
@dp.message(lambda message: message.text == "Пожаловаться") # Фильтр для сообщений с текстом "Пожаловаться"
async def about_bot(message: types.Message):
    await message.answer("Пожалуйста, пришлите фотографию.")

# Обрабатываем все входящие сообщения
@dp.message()
async def answers(message: types.Message):
    question = message.text
    tfidf = tfidfvectorizer(question)
    word2vec = word2vec(question)
    await message.answer(f"TF-IDF: {tfidf}\nWord2Vec: {word2vec}")

# Обрабатываем входящие изображения
@dp.message(lambda message: message.photo) # Проверяем, является ли сообщение фотографией
async def get_photo(message: types.Message):
    document = message.photo[-1].file_id
    photo = await bot.get_file(document)
    name = photo.file_path.split("/")[-1]
    size = message.photo[-1].file_size
    await message.answer(f'Название файла: {name}\nРазмер файла: {size} байт.\nВаш запрос передан специалисту.')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()
