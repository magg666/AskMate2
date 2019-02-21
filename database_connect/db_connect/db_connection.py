import os
import psycopg2
import psycopg2.extras


def get_connection_string():
    user_name = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    host = os.environ.get('HOST')
    database_name = os.environ.get('DB_NAME')

    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name
        )
    else:
        raise KeyError('Some necessary environment variable(s) are not defined')


# noinspection PyUnresolvedReferences
def open_database():
    # noinspection PyUnresolvedReferences
    try:
        connection_string = get_connection_string()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        # noinspection PyUnresolvedReferences
        try:
            connection = open_database()
            dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            ret_value = function(dict_cur, *args, **kwargs)
            dict_cur.close()
            connection.close()
            return ret_value
        except psycopg2.DatabaseError as exception:
            raise exception

    return wrapper
