# AskMate2
Web application which allows to ask questions and give answers. 
Created to practice MVC pattern, errors handling, logging.
I used custom created errors classes, data validation, logging library. 
Implemented Jinja template language, css styling, hashing passwords.


## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Features](#features)
* [Status](#status)
* [Contact](#contact)

## General info
AskMate:
* Shows on main page list of all questions
* Displays form to add questions, answers, comments
* Displays form to register or login
* Gives possibility to tag questions by topis
* Logs errors
* Handles errors on differents levels of MVC pattern

## Technologies
* Python 3.7
* Flask
* Postgresql
* bcrypt
* html, css, bootstrap

## Setup
Use requirements.txt to download all nedeed dependencies.
Use askmatepart2-sample-data.sql script to create database.


## Code Examples
Logging:
```python
logger = logging.getLogger(__name__)
f_handler = logging.FileHandler('log/app.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - LEVEL: %(levelname)s - '
                             'IN MODULE: %(module)s - IN FUNCTION: %(funcName)s '
                             'IN LINE: %(lineno)d - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
```
Custom errors:
```python
class ReadingProblem(Exception):
    """ If there is problem reading data"""
    pass
```
SQL queries with handling sql injections:
```python
@con.connection_handler
def get_answer_by_question_id(cursor, question_id):
    cursor.execute("""
    SELECT answer.id, submission_time, vote_number, question_id, message, image, 
    accepted, user_id, ud.login  FROM answer 
    JOIN user_data ud ON user_id = ud.id
    WHERE question_id = %(question_id)s
    ORDER BY submission_time DESC;
    """,
                   {'question_id': question_id})
    answers = cursor.fetchall()
    return answers
```

## Features
AskMate uses:
* MVC pattern desing
* Jinja template language
* Custom SQL queries 
* Custom exceptions classes
* Logging
* Data validation

## Status
Project is finished.

## Contact
Created by [Magda Wąsowicz](mailto:mw23127@gmail.com) - feel free to contact me!
