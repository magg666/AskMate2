from database_connect import db_tags as tag_manager
from log import logging_rules as log


class ReadingProblem(Exception):
    """ If there is problem reading data"""
    pass


class SavingDataProblem(Exception):
    """ If problems with saving data occurs"""
    pass


class DeletingProblem(Exception):
    """ If there is problem deleting data"""
    pass


def group_for_questions():
    try:
        grouped_tags = tag_manager.get_tags_for_each_question()
        return grouped_tags
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        return []


def get_for_one_question(question_id):
    try:
        return tag_manager.get_tags_for_question_by_question_id(question_id)

    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        return []


def get_all():
    try:
        all_tags = tag_manager.get_all_tags()
        return all_tags
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def get_with_counted_questions():
    try:
        tags_with_counted_questions = tag_manager.get_tags_with_counted_questions()
        return tags_with_counted_questions
    except Exception as err:
        log.logger.error('%s', err)
        log.logging.exception(err)
        raise ReadingProblem


def make_list_of_existing():
    all_tags = get_all()
    existing_tags = [tag['name'] for tag in all_tags]
    return existing_tags


def add_chosen(question_id, chosen_tags):
    existing_tags = make_list_of_existing()
    try:
        for tag in chosen_tags:
            if tag in existing_tags:
                tag_manager.add_tag_to_question(tag, question_id)
            else:
                tag_manager.add_tag(tag)
                tag_manager.add_tag_to_question(tag, question_id)
    except Exception as err:
        log.logger.error('{0} Question id: {1}, tags: {2} ', err, question_id, '/'.join(chosen_tags))
        log.logging.exception(err)
        raise SavingDataProblem


def add_new(question_id, new_tag):
    existing_tags = make_list_of_existing()
    try:
        if new_tag == '' or new_tag.isspace():
            pass
        elif new_tag in existing_tags:
            tag_manager.add_tag_to_question(new_tag, question_id)
        else:
            tag_manager.add_tag(new_tag)
            tag_manager.add_tag_to_question(new_tag, question_id)
    except Exception as err:
        log.logger.error('{0} Question id: {1}, tag: {2} ', err, question_id, new_tag)
        log.logging.exception(err)
        raise SavingDataProblem


def delete_from_question(question_id, tag_id):
    try:
        tag_manager.delete_tag(question_id, tag_id)
    except Exception as err:
        log.logger.error('{0} Question id: {1}, tag: {2} ', err, question_id, tag_id)
        log.logging.exception(err)
        raise DeletingProblem
