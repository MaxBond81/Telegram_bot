import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()


# Создаем таблицу пользователей
class User(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    cid = sq.Column(sq.BigInteger, unique=True)
    words = relationship('User_word', backref='user')

    def __str__(self):
        return f'{self.user_id}: {self.cid}'


# Создаем таблицу общих стартовых слов
class Word(Base):
    __tablename__ = "words"
    word_id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String, nullable=False)
    english_word = sq.Column(sq.String, nullable=False)
    users = relationship('User_word', backref='word')

    def __str__(self):
        return f'{self.word_id}: {self.russian_word}'


# Создаем таблицу слов для конкретных пользователей
class User_word(Base):
    __tablename__ = "user_words"

    user_words_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"), nullable=False)
    word_id = sq.Column(sq.Integer, sq.ForeignKey("words.word_id"), nullable=False)


def create_tables(engine):
    Base.metadata.create_all(engine)