from database_connect.db_connect import db_connection as con

# CREATE
@con.connection_handler
def add_question_comment(cursor, new_comment):
    cursor.execute("""
    INSERT INTO comment(question_id, message, submission_time, user_id)
    VALUES (%(question_id)s, %(message)s, DATE_TRUNC('minute', now()), %(user_id)s);
    """,
                   {'question_id': new_comment['question_id'],
                    'message': new_comment['message'],
                    'user_id': new_comment['user_id']})


@con.connection_handler
def add_answer_comment(cursor, new_comment):
    cursor.execute("""
    INSERT INTO comment(answer_id, message, submission_time, user_id)
    VALUES (%(answer_id)s, %(message)s, DATE_TRUNC('minute', now()), %(user_id)s);
    """,
                   {'answer_id': new_comment['answer_id'],
                    'message': new_comment['message'],
                    'user_id': new_comment['user_id']})


# READ
@con.connection_handler
def get_comment_by_answer_or_question_id(cursor, column, matching_id):
    cursor.execute("""
        SELECT * FROM comment
        JOIN user_data ud on comment.user_id = ud.id
        WHERE {0} = %(matching_id)s;
        """.format(column),
                   {'matching_id': matching_id})
    all_comments = cursor.fetchall()
    return all_comments


@con.connection_handler
def get_comment_by_id(cursor, comment_id):
    sql_str = """
    SELECT * FROM comment
    WHERE id = %(comment_id)s
    """
    cursor.execute(sql_str, {'comment_id': comment_id})
    comment = cursor.fetchone()
    return comment


# UPDATE
@con.connection_handler
def update_comment(cursor, comment_id, edited_comment):
    sql_str = """
    UPDATE comment
    SET (message, edited_count) = (%(message)s, %(edited_count)s)
    WHERE id = %(comment_id)s
    """
    cursor.execute(sql_str, {'comment_id': comment_id,
                             'message': edited_comment['message'],
                             'edited_count': edited_comment['edited_count']})


# DELETE
@con.connection_handler
def delete_comment(cursor, comment_id):
    sql_str = """
    DELETE FROM comment
    WHERE id = %(comment_id)s
    """
    cursor.execute(sql_str, {'comment_id': comment_id})
