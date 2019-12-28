import db_connection as con


# CREATE
@con.connection_handler
def add_tag(cursor, tag):
    cursor.execute("""
    INSERT INTO tag (name)
    VALUES (%(tag)s);
    """,
                   {'tag': tag})


@con.connection_handler
def add_tag_to_question(cursor, tag, question_id):
    cursor.execute("""
    INSERT INTO question_tag (tag_id, question_id)
    VALUES ((SELECT id FROM tag WHERE name = %(tag)s), %(question_id)s)
    ON CONFLICT ON CONSTRAINT pk_question_tag_id
    DO NOTHING
    """,
                   {'tag': tag,
                    'question_id': question_id})


# READ
@con.connection_handler
def get_tags_for_each_question(cursor):
    cursor.execute("""
    SELECT question_id, array_agg(t.name) as tag FROM question_tag qt
    JOIN tag t on qt.tag_id = t.id
    GROUP BY question_id
    """)
    grouped_tags = cursor.fetchall()
    return grouped_tags


@con.connection_handler
def get_tags_with_counted_questions(cursor):
    sql_str = """
    SELECT name, count(question_id) FROM question_tag
    FULL OUTER JOIN tag t on question_tag.tag_id = t.id
    GROUP BY name
    """
    cursor.execute(sql_str)
    tags_and_counted_questions = cursor.fetchall()
    return tags_and_counted_questions


@con.connection_handler
def get_tags_for_question_by_question_id(cursor, question_id):
    cursor.execute("""
    SELECT tag.id, name from tag 
    INNER JOIN question_tag on
    tag.id = question_tag.tag_id 
    INNER JOIN question on
    question.id = question_tag.question_id
    WHERE question.id = %(question_id)s;

    """,
                   {'question_id': question_id})
    tag = cursor.fetchall()
    return tag


@con.connection_handler
def get_all_tags(cursor):
    sql_str = """
    SELECT * FROM tag
    """
    cursor.execute(sql_str)
    all_tags = cursor.fetchall()
    return all_tags


# DELETE
@con.connection_handler
def delete_tag(cursor, question_id, tag_id):
    cursor.execute("""
    DELETE FROM question_tag
    WHERE question_id = %(question_id)s AND tag_id = %(tag_id)s
    """,
                   {'tag_id': tag_id,
                    'question_id': question_id})


