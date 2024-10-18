
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models_db import create_tables, Word

DSN = "postgresql://postgres:postgres@localhost:5432/english_card"
engine = sqlalchemy.create_engine(DSN)

def insert_table_words(engine):
    words = (('Красный', 'Red'),
			('Зеленый', 'Green'),
			('Черный', 'Black'),
		    ('Синий', 'Blue'),
		    ('Желтый', 'Yellow'),
		    ('Знать', 'Know'),
		    ('Бежать', 'Run'),
		    ('Посылать', 'Send'),
		    ('Спать', 'Sleep'),
		    ('Писать', 'Write'),
		    ('Я', 'I'),
		    ('Ты', 'You'),
		    ('Он', 'He'),
		    ('Она', 'She'),
		    ('Мы', 'We')
    )
    create_tables(engine)

    for word in words:
        session.add(Word(russian_word=word[0], english_word=word[1]))
    session.commit()

Session = sessionmaker(bind=engine)
session = Session()

insert_table_words(engine)

session.close()



