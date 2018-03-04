import os
import requests

from flask import Flask, render_template, json, session, jsonify, abort, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from book import Book, Author, User, Review

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL Does Not Exist")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def main():
    # Display home page of the app
    return render_template('index.html')


@app.route('/login')
def login():
    # Display login page of the app
    return render_template('login.html')


@app.route('/register')
def register():
    # Display registration page of the app
    return render_template('register.html')


@app.route('/validateRegistration', methods=['POST', 'GET'])
def signup():
    try:

        # Extract all the form parameters
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # Create password hash
        _hashed_password = generate_password_hash(_password)

        #user = db.query(User).filter(User.email == _email).first()
        user = User('', '', '')

        # See if user with this email already exists
        result = db.execute('select email, password from users where email = :val', {'val': _email})

        for row in result:
            user.email = row['email']

        # If user with this email does not exist create one and redirect to login
        if user.email == '':

            db.execute ('insert into users (email, password, full_name) values (:val1, :val2, :val3)',
                                 {'val1': _email, 'val2': _hashed_password, 'val3': _name})
            #db.add(user)
            db.commit()
            return render_template('login.html')
        # If user already exists stay on registration page
        else:
            return render_template('register.html', match=None)

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        db.close()


@app.route('/validateLogin', methods=['POST'])
def validatelogin():
    try:

        # Extract all the form parameters
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # Create empty user
        user = User('','','')

        #user = db.query(User).filter(User.email == _username).first()

        # Extract user from the DB
        result = db.execute('select email, password from users where email = :val', {'val': _username})
        for row in result:
            user.email = row['email']
            user.password = row['password']

        # If user exists and password matches create user in the session and redirect to the search page
        if user.email != '' and check_password_hash(user.password, _password):
            session['user'] = user
            return render_template('search.html')
        # If user does not exist or password did not match stay on the login page
        else:
            return render_template('login.html', match = None)

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        db.close()


@app.route('/search', methods=['POST'])
def search():
    try:

        _search = request.form['search']

        #books = db.query(Book).join(Book.authors).filter(
        #    Author.name.contains(_search) | Book.title.contains(_search) | Book.isbn.contains(_search)).all()


        # Look for a book in the DB has matches partial isbn, author or title
        result = db.execute ('select books.isbn, books.title, books.year, authors.name from books join book_author '
                             'on books.id = book_author.fk_book join authors on authors.id = book_author.fk_author '
                             'where books.isbn like :val or books.title like :val or authors.name like :val', {'val': '%'+_search + '%' })


        books = []

        # Iterate through results and set Books and Authors collection
        for row in result:
            book = next((x for x in books if x.isbn == row['isbn']), None)
            if(book == None):
                book = Book(row['isbn'], row['title'], row['year'])
                books.append(book)
            author = Author (row['name'])
            book.authors.append(author)

        return render_template('search.html', books=books)

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        db.close()


@app.route('/logout')
def logout():

    # Remove user from session and redirect to login page
    session.pop('user', None)
    return render_template('login.html')


@app.route('/book/<isbn>', methods=['POST', 'GET'])
def bookdetails(isbn):
    try:
        user = session['user']

        if request.method == 'POST':
            _review = request.form['review']
            _option = request.form['rating']
            #book = db.query(Book).filter(Book.isbn == isbn).first()
            #review = Review(_review, _option, user.email, book.id)

            # Look for a book in the DB with a particular isbn
            result = db.execute('select books.id from books '
                                'where books.isbn = :val',{'val': isbn})

            for row in result:
                book_id = row['id']


            # Create a review for a book
            db.execute('insert into reviews (review, rating, user_id, book_id) values (:val1, :val2, :val3, :val4)',
                       {'val1':_review, 'val2': _option, 'val3': user.email, 'val4': book_id})

            #book.reviews.append(review)
            #db.add(book)
            db.commit()

        # Look for a book in the DB with a particular isbn
        result = db.execute('select books.id, books.isbn, books.title, books.year, authors.name from books join book_author '
                            'on books.id = book_author.fk_book join authors on authors.id = book_author.fk_author '
                            'where books.isbn = :val', {'val': isbn})

        #book = db.query(Book).filter(Book.isbn == isbn).first()

        book = None
        for row in result:

            book_id = row['id']

            # Make sure book is not created twice
            if(book == None):
                book = Book(row['isbn'], row['title'], row['year'])

            author = Author (row['name'])
            book.authors.append(author)


        # Extract reviews and rating for a particular book
        result = db.execute('select reviews.review, reviews.rating, reviews.book_id, reviews.user_id from reviews '
                            'where reviews.book_id = :val', {'val': book_id})

        for row in result:
            review = Review (row['review'], row['rating'], row['user_id'], row['book_id'])
            book.reviews.append(review)

        found = 0

        # Set a flag if this user already submitted a review
        for review in book.reviews:
            if review.user_id == user.email:
                found = 1

        # Extract rating from Good Reads
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "9DwgS5nVqvkD4i9tgAPfxA", "isbns": isbn}).json()

        for element in res['books']:
            print(element['average_rating'])
            print(element['reviews_count'])

        return render_template('book.html', book=book, found=found, element=element)

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        db.close()


@app.route('/api/<isbn>', methods=['GET'])
def get_api(isbn):

    #result = db.query(Book).filter(Book.isbn == isbn).first()

    # Look for a book with specific isbn
    result = db.execute(
        'select books.id, books.isbn, books.title, books.year, authors.name from books join book_author '
        'on books.id = book_author.fk_book join authors on authors.id = book_author.fk_author '
        'where books.isbn = :val', {'val': isbn})


    # If there is no book found return 404 page
    if result.rowcount == 0:
        abort(404)

    book = None
    for row in result:
        book_id = row ['id']
        author = Author(row['name'])
        if (book == None):
            book = Book(row['isbn'], row['title'], row['year'])
        book.authors.append(author)

    # Extract information for a particular book
    result = db.execute('select reviews.review, reviews.rating, reviews.book_id, reviews.user_id from reviews '
                        'where reviews.book_id = :val', {'val': book_id})

    for row in result:
        review = Review(row['review'], row['rating'], row['user_id'], row['book_id'])
        book.reviews.append(review)

    total = 0


    # Calculate average book rating
    for review in book.reviews:
        total = total + int(review.rating)

    if total != 0:
        total = total / len(book.reviews)

    authorlist = ""

    for author in book.authors:
        if len(book.authors) == 1:
            authorlist = author.name
        else:
            authorlist = author.name + ", " + authorlist

    authorlist = authorlist.strip()[:-1]

    # Create json response representing book information
    book = [{
        "title": book.title,
        "author": authorlist,
        "year": book.year,
        "isbn": isbn,
        "review_count": len(book.reviews),
        "average_score": round(total, 2)
    }]

    return jsonify({'book': book})