# coding=utf-8

import os
from sqlalchemy import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

books_authors = Table("book_author",
    Base.metadata,
    Column("fk_book", Integer, ForeignKey("books.id")),
    Column("fk_author", Integer, ForeignKey("authors.id")),
)

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    isbn = Column(String)
    title = Column(String)
    year = Column(String)

    authors = relationship(
        "Author",
        backref="books",
        secondary=books_authors
    )

    reviews = relationship("Review", backref="books")

    def __init__(self, isbn, title, year):
        self.isbn = isbn
        self.title = title
        self.year = year

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

class User(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True)
    full_name = Column(String)
    password = Column(String)
    reviews = relationship('Review', backref='user')

    def __init__(self, email, full_name, password):
        self.email = email
        self.full_name = full_name
        self.password = password

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    review = Column(String)
    rating = Column(Integer)
    user_id = Column(String, ForeignKey('users.email'))
    book_id = Column (Integer, ForeignKey('books.id'), nullable= True )

    def __init__(self, review, rating, user_id, book_id):
        self.review = review
        self.rating = rating
        self.user_id = user_id
        self.book_id = book_id

Base.metadata.create_all(engine)
