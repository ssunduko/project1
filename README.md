# Project 1

Web Programming with Python and JavaScript

# Created by Sergey L. Sundukovskiy

<h3>File Content</h3>

<h4>book.py<h4>

Contains definition of all Model Objects (User, Book, Author, Review)
and responsible for creating tables

Book and Author have a many to many relationship<br>
Book and Review have a one to many relationship

<h4>import.py<h4>

Contains logic for reading books.csv file and populating tables

<h4>application.py<h4>

Contains main application logic

<h4>index.html</h4>

Contains hmtl code for displaying home page of the app

<h4>login.html</h4>

Contains html and python code for allowing user to login<br>
If login information is not correct or user does not exist warning message<br>
will be displayed, otherwise user will be redirected to the search page

<h4>register.html</h4>

Contains html and python code for allowing user to register<br>
If user tries to register with already registered email address<br>
warning message will be displayed, otherwise user will be redirected to<br>
the login page

<h4>search.html</h4>

Contains html and python code for displaying book search results<br>
If user enters search query that yields no results, warning message<br>
will be displayed

<h4>book.html<h4>

Contains html and python code for displaying detailed book information.<br>
It allows user to review the book. If user already reviewed the book, he/she<br>
will not be allowed to submit another book review

<h4>requirements.txt<h4>

Contains 3rd party libraries.<br>
In addition to provided libraries added 'requests' lib


<h3>Short Description</h3>

Initial project implementation used sqlalchemy orm. After that it was<br>
refactored to use raw sql<br>

For proper execution DATABASE_URL environment variable must be set to <br>
postgres://sojelnptnsncxh:6d44b0816915c80507f801b9b514d0ca1928e959438b9d128f862c4d022b0bb9@ec2-107-22-175-33.compute-1.amazonaws.com:5432/d38636j4dsvs33<br>

In order to prep the DB 'python import.py' must be executed first







