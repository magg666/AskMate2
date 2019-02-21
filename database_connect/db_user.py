import db_connection as con


# CREATE
@con.connection_handler
def add_user(cursor, login, password):
    str_sql = """
    INSERT INTO user_data(login, password, registration_date)
    VALUES (%(login)s, %(password)s, DATE_TRUNC('minute', now()))
    RETURNING id, login, registration_date, prestige_points
    """
    cursor.execute(str_sql, {'login': login,
                             'password': password})
    user_data = cursor.fetchone()
    return user_data


# READ
@con.connection_handler
def get_data_for_user(cursor, user_id):
    sql_str = """
    SELECT id, login, registration_date, prestige_points FROM user_data
    WHERE id = %(user_id)s
    """
    cursor.execute(sql_str, {'user_id': user_id})
    user_data = cursor.fetchone()
    return user_data


@con.connection_handler
def get_password_for_user(cursor, username):
    str_sql = """
    SELECT password FROM user_data
    WHERE login = %(username)s
    """
    cursor.execute(str_sql, {'username': username})
    password = cursor.fetchone()
    return password['password']


@con.connection_handler
def get_id_for_user(cursor, username):
    str_sql = """
    SELECT id FROM user_data
    WHERE login = %(username)s
    """
    cursor.execute(str_sql, {'username': username})
    user_id = cursor.fetchone()
    return user_id


@con.connection_handler
def check_if_username_in_logins(cursor, username):
    str_sql = """
    SELECT CASE WHEN EXISTS (SELECT 1
                         FROM user_data
                         WHERE login = %(username)s)
            THEN CAST (1 AS bit)
            ELSE CAST (0 AS bit)

            END
    AS bit


    """
    cursor.execute(str_sql, {'username': username})
    exist = cursor.fetchone()
    return exist['bit']


@con.connection_handler
def get_all_users(cursor):
    str_sql = """
    SELECT id, login, registration_date, prestige_points FROM user_data
    """
    cursor.execute(str_sql)
    all_users = cursor.fetchall()
    return all_users


@con.connection_handler
def get_all_questions_for_user(cursor, user_id):
    sql_str = """
    SELECT id, title FROM question
    WHERE user_id = %(user_id)s
    """
    cursor.execute(sql_str, {'user_id': user_id})
    user_questions = cursor.fetchall()
    return user_questions


@con.connection_handler
def get_all_answers_for_user(cursor, user_id):
    sql_str = """
        SELECT id, question_id, message FROM answer
        WHERE user_id = %(user_id)s
        """
    cursor.execute(sql_str, {'user_id': user_id})
    user_answers = cursor.fetchall()
    return user_answers


@con.connection_handler
def get_all_comments_for_user(cursor, user_id):
    sql_str = """
        SELECT id, question_id, answer_id, message FROM comment
        WHERE user_id = %(user_id)s
        """
    cursor.execute(sql_str, {'user_id': user_id})
    user_comments = cursor.fetchall()
    return user_comments


@con.connection_handler
def get_prestige_for_user_for_answer(cursor, answer_id):
    cursor.execute("""
    SELECT ud.id, prestige_points FROM user_data ud
    JOIN answer a on ud.id = a.user_id
    WHERE a.id = %(answer_id)s
    """, {'answer_id': answer_id})
    prestige_for_answer = cursor.fetchone()
    return prestige_for_answer


@con.connection_handler
def get_prestige_for_user_for_question(cursor, question_id):
    cursor.execute("""
    SELECT ud.id, prestige_points FROM user_data ud
    JOIN question q on ud.id = q.user_id
    WHERE q.id = %(question_id)s
    """, {'question_id': question_id})
    prestige_for_answer = cursor.fetchone()
    return prestige_for_answer


# UPDATE
@con.connection_handler
def update_prestige_for_user(cursor, user_id, prestige_sum):
    cursor.execute("""
    UPDATE user_data
    SET prestige_points = %(prestige_sum)s
    WHERE user_data.id = %(user_id)s
    """, {'user_id': user_id,
          'prestige_sum': prestige_sum})
