from database_connect import db_comments as comm_manager
from log import logging_rules as log
from useful_functions import useful as util
from data_manager import answer as answer

EDIT_RATE = 1
EMERGENCY_NUMBER = 0


class ReadingProblem(Exception):
    """ If there is problem reading data"""
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


def get_for_question(question_id):
    try:
        return comm_manager.get_comment_by_answer_or_question_id('question_id', question_id)

    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def get_for_every_answer(all_answers):
    try:
        all_comments = []
        for answer in all_answers:
            all_comments.append(comm_manager.get_comment_by_answer_or_question_id('answer_id', answer['id']))
        return all_comments

    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def get_by_id(comment_id):
    try:
        return comm_manager.get_comment_by_id(comment_id)
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def validate_message(message):
    if util.is_text_validated(message, range(5, 100000)):
        return message
    else:
        raise WrongLength


def add_to_question(new_comment):
    try:
        comm_manager.add_question_comment(new_comment)
    except Exception as err:
        log.logger.error('{0}, Data to be added: {question_id}/{message}/{user_id}'.format(err, **new_comment))
        log.logging.exception(err)
        raise SavingDataProblem


def add_to_answer(new_comment):
    try:
        comm_manager.add_answer_comment(new_comment)
    except Exception as err:
        log.logger.error('{0}, Data to be added: {answer_id}/{message}/{user_id}'.format(err, **new_comment))
        log.logging.exception(err)
        raise SavingDataProblem


def raise_edited_count(comment_to_edit):
    try:
        edited_count = comment_to_edit['edited_count']
        new_edited_count = edited_count + EDIT_RATE
        return new_edited_count
    except Exception as err:
        log.logger.error('{0}, Comment edited: {comment_id}/{edited_count}'.format(err, **comment_to_edit))
        log.logging.exception(err)
        return EMERGENCY_NUMBER + EDIT_RATE


def find_question_id_for(comment_id):
    comment = get_by_id(comment_id)
    question_id = comment['question_id']
    if question_id is None:
        answer_id = comment['answer_id']
        full_answer = answer.get_one_with_author(answer_id)
        question_id = full_answer['question_id']
        return question_id
    else:
        return question_id


def update(comment_id, edited_comment):
    try:
        comm_manager.update_comment(comment_id, edited_comment)
    except Exception as err:
        log.logger.error(
            '{0}, Modified comment: {1}/{message}/{edited_count}'.format(err, comment_id, **edited_comment))
        log.logging.exception(err)
        raise SavingDataProblem


def delete(comment_id):
    try:
        comm_manager.delete_comment(comment_id)
    except Exception as err:
        log.logger.error('%s, Comment id to delete: %d', err, comment_id)
        log.logging.exception(err)
        raise DeletingProblem


def assign_question_id_to_answer_comment(all_comments):
    for comments in all_comments:
        if comments['question_id'] is None:
            answer_id = comments['answer_id']
            question_id = answer.find_question_id_in(answer_id)
            comments['question_id'] = question_id
    return all_comments
