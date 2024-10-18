import random
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models_db import User, Word, User_word


DSN = "postgresql://postgres:postgres@localhost:5432/english_card"
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()


# Добавляем пользователя
def add_user(cid):
    user = User(cid = cid)
    session.add(user)
    session.commit()
    print(f'Добавлен пользователь id: {cid}')
    for word_id in get_words_id_list():
        session.add(User_word(user_id=get_user_id(cid), word_id=word_id))
    session.commit()


# Получаем cid пользователя
def get_user_cid(cid):
    q = session.query(User).filter(User.cid == cid)
    for k in q:
        return k.cid


#Получаем id пользователя
def get_user_id(cid):

    q = session.query(User).filter(User.cid == cid)
    for k in q:
        return k.user_id


#Получаем список стартовых слов для передачу в user_words
def get_words_id_list():
    words_id_list = [w.word_id for w in session.query(Word).all()]
    print(words_id_list)
    return words_id_list


#Получаем  случайное целевое слово и 4 случайных неверных слов для вопросов бота, а также длину списка слов для пользователя
def get_target_translate_other(user_id):
    words_list = session.query(Word.english_word,Word.russian_word).select_from(User_word).join(Word).filter(User_word.user_id == user_id).all()
    target_translate_word = random.choice(words_list)
    target_word = target_translate_word[0]
    translate = target_translate_word[1]
    words_list.remove(target_translate_word)
    words_list_random = random.sample(words_list, 4)
    other_words = [w[0] for w in words_list_random]
    result = [target_word,translate, other_words, len(words_list)]
    print(result)
    return result

# Функция удаления слова из user_words
def delete_word_user_db(user_id, delete_word):
    word_id_table_word = session.query(Word).filter(Word.english_word == delete_word)
    for w in word_id_table_word:
        word_id = w.word_id
        session.query(User_word).filter(User_word.user_id == user_id).filter(User_word.word_id == word_id).delete()
        session.commit()


# Добавляем в таблицу user_words новое слово
def add_word_user_db(user_id, new_word):
    new_word_table_word = Word(russian_word = new_word[1], english_word = new_word[0])
    session.add(new_word_table_word)
    session.commit()
    print(new_word_table_word.word_id)
    new_word_table_user_word = User_word(user_id = user_id, word_id = new_word_table_word.word_id)
    session.add(new_word_table_user_word)
    session.commit()

# Функция получения списка слов из таблицы words
def get_words_list():
    words_list = [w.english_word for w in session.query(Word).all()]
    print(words_list)
    return words_list




