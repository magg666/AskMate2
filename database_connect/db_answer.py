import db_connection as con


# CREATE
@con.connection_handler
def add_one_answer_to_question(cursor, question_id, new_answer):
    cursor.execute("""
    INSERT INTO answer(submission_time, question_id, message, image, user_id)
    VALUES (DATE_TRUNC('minute', now()), %(question_id)s, %(message)s, %(image)s, %(user_id)s)
    """,
                   {'question_id': question_id,
                    'message': new_answer['message'],
                    'image': new_answer['image'],
                    'user_id': new_answer['user_id']})


# READ
@con.connection_handler
def count_answers_for_each_question(cursor, number=None):
    cursor.execute("""
    SELECT question.id, COUNT(answer.id) FROM question
    FULL OUTER JOIN answer ON question.id = answer.question_id
    GROUP BY question.id
    ORDER BY question.submission_time DESC
    LIMIT %(number)s
    """,
                   {'number': number})
    counted_answers = cursor.fetchall()
    return counted_answers


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


@con.connection_handler
def get_answer_by_answer_id(cursor, answer_id):
    cursor.execute("""
    SELECT answer.id, submission_time, vote_number, question_id, message, image, 
    accepted, user_id, ud.login  FROM answer 
    JOIN user_data ud ON user_id = ud.id
    WHERE answer.id = %(answer_id)s
    ORDER BY submission_time DESC;
    """,
                   {'answer_id': answer_id})
    answers = cursor.fetchone()
    return answers


@con.connection_handler
def get_vote_number_for_answer(cursor, answer_id):
    cursor.execute("""
    SELECT vote_number FROM answer
    WHERE id = %(answer_id)s
        """,
                   {'answer_id': answer_id})
    vote_number = cursor.fetchone()
    return vote_number


# UPDATE
@con.connection_handler
def update_vote_number_in_answer(cursor, new_vote_number, answer_id):
    cursor.execute("""
    UPDATE answer
    SET vote_number = %(new_vote_number)s 
    WHERE id = %(answer_id)s; 
    """,
                   {'new_vote_number': new_vote_number,
                    'answer_id': answer_id})


@con.connection_handler
def update_answer(cursor, answer_id, new_answer):
    cursor.execute("""
        UPDATE answer
        SET (message, image) = (%(message)s , %(image)s)
        WHERE id = %(answer_id)s;
        """,
                   {'message': new_answer['message'],
                    'image': new_answer['image'],
                    'answer_id': answer_id})


@con.connection_handler
def update_accepted_in_answer(cursor, answer_id):
    sql_str = """
    UPDATE answer
    SET accepted = TRUE
    WHERE id = %(answer_id)s
    """
    cursor.execute(sql_str, {'answer_id': answer_id})


# DELETE
@con.connection_handler
def delete_data_in_answer_and_answer_comment(cursor, answer_id):
    cursor.execute("""
    DELETE FROM comment
    WHERE answer_id = %(answer_id)s;
    DELETE FROM answer 
    WHERE id = %(answer_id)s
    RETURNING question_id

    """,
                   {'answer_id': answer_id})
    question_id = cursor.fetchone()
    return question_id
