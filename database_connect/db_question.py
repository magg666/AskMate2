from database_connect.db_connect import db_connection as con

# CREATE
@con.connection_handler
def add_question(cursor, new_question):
    cursor.execute("""
    INSERT INTO question(submission_time, title, message, image, user_id)
    VALUES (DATE_TRUNC('minute', now()), %(title)s, %(message)s, %(image)s, %(user_id)s)
    RETURNING id;
    """,
                   {'title': new_question['title'],
                    'message': new_question['message'],
                    'image': new_question['image'],
                    'user_id': new_question['user_id']})
    question_id = cursor.fetchone()
    return question_id


# READ
@con.connection_handler
def get_questions(cursor, column_name, order, number):
    cursor.execute("""
    SELECT q.id, submission_time, vote_number, view_number, title, 
    user_id, ud.login, prestige_points FROM question q
    JOIN user_data ud on q.user_id = ud.id
    ORDER BY {0} {1}
    LIMIT %(number)s
    """.format(column_name, order),
                   {'number': number})
    questions = cursor.fetchall()
    return questions


@con.connection_handler
def get_one_question(cursor, question_id):
    cursor.execute("""
    SELECT q.id, submission_time, vote_number, view_number, title, 
    q.message, user_id, ud.login, prestige_points FROM question q
    JOIN user_data ud on q.user_id = ud.id
    WHERE q.id = %(question_id)s
    """,
                   {'question_id': question_id})
    question = cursor.fetchone()
    return question


@con.connection_handler
def get_view_number_for_question(cursor, question_id):
    cursor.execute("""
    SELECT view_number FROM question
    WHERE id = %(question_id)s
        """,
                   {'question_id': question_id})
    view_number = cursor.fetchone()
    return view_number


@con.connection_handler
def get_vote_number_for_question(cursor, question_id):
    cursor.execute("""
    SELECT vote_number FROM question
    WHERE id = %(question_id)s
        """,
                   {'question_id': question_id})
    vote_number = cursor.fetchone()
    return vote_number


# READ - SEARCH
@con.connection_handler
def search_questions(cursor, search_phrase):
    cursor.execute("""
        SELECT q.id, q.title, q.message, a.message as answer_message FROM question q
        LEFT JOIN answer a ON a.question_id = q.id
        WHERE q.title LIKE '%%' || %(search_phrase)s || '%%'
        OR q.message LIKE '%%' || %(search_phrase)s || '%%'
        OR a.message LIKE '%%' || %(search_phrase)s || '%%'
        ORDER BY q.id ASC;

        """,
                   {'search_phrase': search_phrase})
    data = cursor.fetchall()
    iterable_data = []
    for row in data:
        iterable_data.append(dict(row))
    return iterable_data


# UPDATE
@con.connection_handler
def update_view_number_in_question(cursor, new_view_number, question_id):
    cursor.execute("""
    UPDATE question
    SET view_number = %(new_view_number)s 
    WHERE id = %(question_id)s; 
    """,
                   {'new_view_number': new_view_number,
                    'question_id': question_id})


@con.connection_handler
def update_vote_number_in_question(cursor, new_vote_number, question_id):
    cursor.execute("""
    UPDATE question
    SET vote_number = %(new_vote_number)s 
    WHERE id = %(question_id)s; 
    """,
                   {'new_vote_number': new_vote_number,
                    'question_id': question_id})


@con.connection_handler
def update_question(cursor, question_id, new_question):
    cursor.execute("""
        UPDATE question
        SET (title, message, image) = (%(title)s, %(message)s , %(image)s)
        WHERE id = %(question_id)s;
        """,
                   {'title': new_question['title'],
                    'message': new_question['message'],
                    'image': new_question['image'],
                    'question_id': question_id})


# DELETE
@con.connection_handler
def delete_all_data_question(cursor, question_id):
    sql_string = """
    DELETE FROM comment c
    USING answer a
    JOIN question q on a.question_id = %(question_id)s
    WHERE answer_id = a.id;
    DELETE FROM answer
    WHERE question_id = %(question_id)s;
    DELETE FROM question_tag
    WHERE question_id = %(question_id)s;
    DELETE FROM comment
    WHERE question_id = %(question_id)s;
    DELETE FROM question
    WHERE id = %(question_id)s;
    
    """
    cursor.execute(sql_string, {'question_id': question_id})
