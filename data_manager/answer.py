from database_connect import db_answer as answer_manager
from log import logging_rules as log
from useful_functions import useful as util


class ReadingProblem(Exception):
    """ If there is problem reading data"""
    pass


class DeletingProblem(Exception):
    """ If there is problem deleting data"""
    pass


class WrongLength(Exception):
    """ If text has not valid length"""
    pass


class SavingDataProblem(Exception):
    """ If problems with saving data occurs"""
    pass


def count_for_each_question():
    try:
        counted_answers = answer_manager.count_answers_for_each_question()
        return counted_answers
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        return []


def get_one_with_author(answer_id):
    try:
        return answer_manager.get_answer_by_answer_id(answer_id)
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def find_question_id_in(answer_id):
    answer = get_one_with_author(answer_id)
    return answer['question_id']


def get_all_for_question(question_id):
    try:
        return answer_manager.get_answer_by_question_id(question_id)

    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def check_is_any_accepted(all_answers):
    checking_accepted = [answer['accepted'] for answer in all_answers]
    if not any(checking_accepted):
        return False
    else:
        return True


def validate_message(message):
    if util.is_text_validated(message, range(10, 100000)):
        return message
    else:
        raise WrongLength


def add(question_id, new_answer):
    try:
        return answer_manager.add_one_answer_to_question(question_id, new_answer)

    except Exception as err:
        log.logger.error(
            '{0}, Data to be added: {1}: {message}/{image}/{user_id}'.format(err, question_id, **new_answer))
        log.logging.exception(err)
        raise SavingDataProblem


def get_vote_number(answer_id):
    vote_number = answer_manager.get_vote_number_for_answer(answer_id)
    return vote_number['vote_number']


def update_vote(answer_id, data_form):
    vote_number = get_vote_number(answer_id)
    new_vote_number = util.change_vote_number(vote_number, data_form)
    try:
        answer_manager.update_vote_number_in_answer(new_vote_number, answer_id)

    except Exception as err:
        log.logger.error('%s, data to update: Q.id: %d, Vote_number: %d ', err, answer_id, new_vote_number)
        log.logging.exception(err)


def update(answer_id, new_answer):
    try:
        answer_manager.update_answer(answer_id, new_answer)

    except Exception as err:
        log.logger.error('{0}, Modified: {1}/{message}/{image}'.format(err, answer_id, **new_answer))
        log.logging.exception(err)
        raise SavingDataProblem


def delete_and_return_question_id(answer_id):
    try:
        question_id = answer_manager.delete_data_in_answer_and_answer_comment(answer_id)
        return question_id['question_id']

    except Exception as err:
        log.logger.error('%s, Answer id to delete: %d', err, answer_id)
        log.logging.exception(err)
        raise DeletingProblem


def accept(answer_id):
    try:
        return answer_manager.update_accepted_in_answer(answer_id)

    except Exception as err:
        log.logger.error('{0}, Answer to accept: {1}'.format(err, answer_id))
        log.logging.exception(err)
        raise SavingDataProblem
