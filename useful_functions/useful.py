from log import logging_rules as log

EMERGENCY_NUMBER = 0
VIEW_RATE = 1
POINTS_FOR_ACCEPT = 15


# adding counted answer to questions
def combine_questions_with_counted_answer(questions, counted_answers):
    for question in questions:
        for answer in counted_answers:
            if question['id'] == answer['id']:
                question['count'] = answer['count']
    return questions


# adding grouped tags to questions
def combine_questions_with_grouped_tags(questions, grouped_tags):
    for question in questions:
        for tag in grouped_tags:
            if question['id'] == tag['question_id']:
                question['tag'] = tag['tag']
    return questions


# sorting
def define_sorting_order(order):
    sort_order = None
    if order == 'desc':
        sort_order = 'DESC'
    elif order == 'asc':
        sort_order = 'ASC'
    return sort_order


# searching
def find_wrong_searches(data_to_search, search_phrase):
    wrong_searches = []
    for row in data_to_search:
        for key, value in row.items():
            if isinstance(value, int):
                pass
            elif key == 'title':
                pass
            elif search_phrase not in str(value):
                wrong_searches.append(value)
    return wrong_searches


def prepare_correct_search(data_to_search, search_phrase):
    wrong_searches = find_wrong_searches(data_to_search, search_phrase)
    correct_searches = [{key: value for key, value in row.items() if value not in wrong_searches} for row in
                        data_to_search]
    remove_duplicate = []

    for item in correct_searches:
        if item not in remove_duplicate:
            remove_duplicate.append(item)
    return remove_duplicate


def raise_view_number(view_number):
    try:
        new_view_number = view_number + VIEW_RATE
        return new_view_number
    except Exception as err:
        log.logger.debug('%s', err)
        log.logging.exception(err)
        return EMERGENCY_NUMBER + VIEW_RATE


def prestige_system(prestige_point, data_form, rate_plus, rate_minus):
    if data_form == 'plus':
        prestige_point += rate_plus
    elif data_form == 'minus':
        prestige_point -= rate_minus
    return prestige_point


def prestige_accepted_system(prestige_point):
    new_prestige_point = prestige_point + POINTS_FOR_ACCEPT
    return new_prestige_point


def change_prestige_for_answer(prestige_sum, data_form):
    try:
        new_prestige_number = prestige_system(prestige_sum, data_form, 10, 2)
        return new_prestige_number
    except Exception as err:
        log.logger.debug('%s', err)
        log.logging.exception(err)
        return EMERGENCY_NUMBER


def change_prestige_for_question(prestige_sum, data_form):
    try:
        new_prestige_number = prestige_system(prestige_sum, data_form, 5, 2)
        return new_prestige_number
    except Exception as err:
        log.logger.debug('%s', err)
        log.logging.exception(err)
        return EMERGENCY_NUMBER


def vote_system(vote_counter, data_form):
    if data_form == 'plus':
        vote_counter += 1
    elif data_form == 'minus':
        vote_counter -= 1
    return vote_counter


def change_vote_number(vote_counter, data_form):
    try:
        new_vote_number = vote_system(vote_counter, data_form)
        return new_vote_number
    except Exception as err:
        log.logger.debug('%s', err)
        log.logging.exception(err)
        return EMERGENCY_NUMBER


def is_text_validated(text_data, area):
    if len(text_data) in area and not text_data.isspace():
        return True


