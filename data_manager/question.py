from database_connect import db_question as qst_manager
from log import logging_rules as log
from useful_functions import useful as util

EMERGENCY_NUMBER = 0
VIEW_RATE = 1


class ReadingProblem(Exception):
    """ If there is problem reading data"""
    pass


class WrongSort(Exception):
    """ If there is problem with sort functions"""
    pass


class WrongSearch(Exception):
    """ If there is problem with search functions"""
    pass


class WrongLength(Exception):
    """ If text has not valid length"""
    pass


class SavingDataProblem(Exception):
    """ If problems with saving data occurs"""
    pass


class DeletingProblem(Exception):
    """ If there is problem deleting data"""
    pass


def get_ordered_by_latest_with(counted_answers, grouped_tags,
                               column_name='q.submission_time', order='DESC', number=None):
    try:
        questions = qst_manager.get_questions(column_name, order, number)
        questions_with_counted_answers = util.combine_questions_with_counted_answer(questions, counted_answers)
        questions_with_tags = util.combine_questions_with_grouped_tags(questions_with_counted_answers, grouped_tags)
        return questions_with_tags

    except Exception as err:
        log.logger.critical('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def get_sorted_by_user(counted_answers, grouped_tags, attribute, order):
    try:
        converted_order = util.define_sorting_order(order)
        questions = get_ordered_by_latest_with(counted_answers, grouped_tags, attribute, converted_order)
        return questions

    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise WrongSort


def get_search_result(search_phrase):
    try:
        data_to_search = qst_manager.search_questions(search_phrase)
        result_of_search = util.prepare_correct_search(data_to_search, search_phrase)
        return result_of_search

    except Exception as err:
        log.logger.critical('%s', err)
        log.logging.exception(err)
        raise WrongSearch


def get_view_number(question_id):
    view_number = qst_manager.get_view_number_for_question(question_id)
    return view_number['view_number']


def update_view(question_id):
    view_number = get_view_number(question_id)
    new_view_number = util.raise_view_number(view_number)
    try:
        qst_manager.update_view_number_in_question(new_view_number, question_id)

    except Exception as err:
        log.logger.error('%s, data to update: Q.id: %d, View_number: %d ', err, question_id, new_view_number)
        log.logging.exception(err)


def get_one_with_author(question_id):
    try:
        return qst_manager.get_one_question(question_id)
    except Exception as err:
        log.logger.error('%s, Question id: %d', err, question_id)
        log.logging.exception(err)
        raise ReadingProblem


def validate_title(title):
    if util.is_text_validated(title, range(10, 81)):
        return title
    else:
        raise WrongLength


def validate_message(message):
    if util.is_text_validated(message, range(10, 100000)):
        return message
    else:
        raise WrongLength


def add(new_question):
    try:
        question_id = qst_manager.add_question(new_question)
        return question_id['id']
    except Exception as err:
        log.logger.error('{0}, Data to be added: {title}/{message}/{image}/{user_id}'.format(err, **new_question))
        log.logging.exception(err)
        raise SavingDataProblem


def update(question_id, new_question):
    try:
        qst_manager.update_question(question_id, new_question)

    except Exception as err:
        log.logger.error('{0}, Modified: {1}/ {title}/{message}/{image}'.format(err, question_id, **new_question))

        log.logging.exception(err)
        raise SavingDataProblem


def delete_with_all_related_data(question_id):
    try:
        return qst_manager.delete_all_data_question(question_id)
    except Exception as err:
        log.logger.error('%s, Question id to delete: %d', err, question_id)
        log.logging.exception(err)
        raise DeletingProblem


def get_vote_number(question_id):
    vote_number = qst_manager.get_vote_number_for_question(question_id)
    return vote_number['vote_number']


def update_vote(question_id, data_form):
    vote_number = get_vote_number(question_id)
    new_vote_number = util.change_vote_number(vote_number, data_form)
    try:
        qst_manager.update_vote_number_in_question(new_vote_number, question_id)

    except Exception as err:
        log.logger.error('%s, data to update: Q.id: %d, Vote_number: %d ', err, question_id, new_vote_number)
        log.logging.exception(err)


