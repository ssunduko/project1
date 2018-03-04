import os
import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from book import Book, Author

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

filepath = 'books.csv'

if not os.path.isfile(filepath):
    print("File does not exist ".format(filepath))
    sys.exit()

with open(filepath) as fp:
    fp.readline()
    for line in fp:

        #Strip first line of the data file
        line = line.replace("\n","")
        #Split line of the file by ','
        parts = line.split(",")

        #if there are more than 4 parts in line we must be dealing with the title that contains commas
        #or there are multiple authors
        if len(parts) != 4:

            book = Book(parts[0],'',parts[-1])
            #Deal with comma containing title
            if (parts[1].startswith('"')):
                titleparts = line.split('"')[1::2]
                book.title = titleparts[0]

            #Deal with multiple authors
            if (parts[2].startswith('"')):
                if (book.title == ''):
                    book.title = parts[1]
                authornames = line.split('"')[1::2]
                for authorname in authornames[0].split(','):
                    book.authors.append(Author(authorname.strip()))

            db.add(book)
            db.commit()

        else:

            #This is a simple case. Just create book with a single author
            book = Book(parts[0],parts[1],parts[3])
            book.authors = [Author(parts[2])]
            db.add(book)
            db.commit()