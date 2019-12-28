from flask import Flask, render_template, request, redirect, url_for, flash, Markup, session, escape
from functools import wraps

import question as question
import answer as answer
import comment as comment
import tags as tag
import user as user

app = Flask(__name__)
app.secret_key = 'uuu'


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('errors.html',
                           error=405,
                           error_message='Method not allowed')


# wrapper to verify if user is logged
def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('route_login'))

    return wrap


# wrapper to verified if user is not logged
def login_forbidden(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'username' not in session:
            return func(*args, **kwargs)
        else:
            flash("You are already logged {0}".format(session['username']))
            return redirect(url_for('route_main'))

    return wrap


# main page, list of all, sorted, searched
@app.route('/')
def route_main():
    try:
        counted_answers = answer.count_for_each_question()
        grouped_tags = tag.group_for_questions()
        # number of displayed questions on main page should be five (5)
        questions = question.get_ordered_by_latest_with(counted_answers, grouped_tags, number=5)

        return render_template('main_list.html',
                               questions=questions)
    except question.ReadingProblem:
        return render_template('errors.html')


@app.route('/list')
def route_questions_list():
    try:
        counted_answers = answer.count_for_each_question()
        grouped_tags = tag.group_for_questions()
        questions = question.get_ordered_by_latest_with(counted_answers, grouped_tags)
        return render_template('main_list.html',
                               questions=questions)
    except question.ReadingProblem:
        return render_template('errors.html')


@app.route('/list/sorted')
def route_list_sorted():
    try:
        counted_answers = answer.count_for_each_question()
        grouped_tags = tag.group_for_questions()

        sorted_questions = question.get_sorted_by_user(counted_answers,
                                                       grouped_tags,
                                                       request.args.get('attribute'),
                                                       request.args.get('order'))
        return render_template('main_list.html',
                               questions=sorted_questions)
    except question.WrongSort:
        flash(message='The sorting function is currently not available. Sorry for inconvenience')
        return redirect(url_for('route_main'))


@app.route('/search')
def route_search():
    search_phrase = request.args.get('q')
    try:
        all_data = question.get_search_result(search_phrase)
        styled_search_phrase = Markup('<span class="phrase">') + search_phrase + Markup('</span>')

        searched_result = {
            'all_data': all_data,
            'search_phrase': search_phrase,
            'styled_search_phrase': styled_search_phrase,
            'session': session
        }

        return render_template('search_option.html',
                               **searched_result)

    except question.WrongSearch:
        flash(message='The search function is currently not available. Sorry for inconvenience')
        return redirect(url_for('route_main'))


# /question, /add question, /edit question, /delete question part, /vote question
@app.route('/question/<int:question_id>')
def route_question_view(question_id):
    question.update_view(question_id)

    try:
        all_answers = answer.get_all_for_question(question_id)
        all_data = {'question': question.get_one_with_author(question_id),
                    'tags': tag.get_for_one_question(question_id),
                    'question_comments': comment.get_for_question(question_id),
                    'all_answers': all_answers,
                    'is_any_answer_accepted': answer.check_is_any_accepted(all_answers),
                    'answer_comments': comment.get_for_every_answer(all_answers),
                    'session': session}
        return render_template('question_page.html',
                               **all_data)

    except (question.ReadingProblem, answer.ReadingProblem, comment.ReadingProblem):
        flash(message="This question is either deleted or modifying. Please try again in few minutes")
        return redirect(url_for('route_main'))


@app.route('/add-question')
@login_required
def route_add_question_form():
    return render_template('add_or_update_question.html',
                           form_url=url_for('route_add_question_form'))


@app.route('/add-question', methods=['POST'])
@login_required
def route_add_question():
    try:
        new_question = {'title': escape(question.validate_title(request.form.get('title'))),
                        'message': escape(question.validate_message(request.form.get('message'))),
                        'image': escape(request.form.get('image')),
                        'user_id': session.get('id')}

    except question.WrongLength:
        flash(message='Length of text must be correct')
        return redirect(url_for('route_add_question_form'))

    try:
        question_id = question.add(new_question)
        return redirect(url_for('route_question_view',
                                question_id=question_id))

    except question.SavingDataProblem:
        flash('Your question will be verified and added within 24 hours.')
        return redirect('/')


@app.route('/question/<int:question_id>/edit')
@login_required
def route_show_edit_form(question_id):
    try:
        question_to_edit = question.get_one_with_author(question_id)
        if session['id'] == question_to_edit['user_id']:
            return render_template('add_or_update_question.html',
                                   question=question_to_edit,
                                   form_url=url_for('route_show_edit_form',
                                                    question_id=question_id))
        else:
            flash("Only author can edit this question")
            return redirect(url_for('route_question_view',
                                    question_id=question_id))

    except question.ReadingProblem:
        flash('We are sorry but editing this question is not possible now. Please try again in few minutes')
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/question/<int:question_id>/edit', methods=['POST'])
@login_required
def route_save_edited_question(question_id):
    try:
        new_question = {'title': escape(question.validate_title(request.form.get('title'))),
                        'message': escape(question.validate_message(request.form.get('message'))),
                        'image': escape(request.form.get('image'))}

    except question.WrongLength:
        flash('Length of text must be correct')
        return redirect(url_for('route_show_edit_form',
                                question_id=question_id))

    try:
        question.update(question_id, new_question)
    except question.SavingDataProblem:
        flash('Your question will be verified and updated within 24 hours.')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def route_delete_question(question_id):
    try:
        question.delete_with_all_related_data(question_id)
    except question.DeletingProblem:
        flash('Your question will be deleted in 24 hours.')
    finally:
        return redirect(url_for('route_main'))


# @app.route('/question/<question_id>/vote')
# def route_question_vote(question_id):
#     pass


@app.route('/question/<int:question_id>/vote', methods=['POST'])
@login_required
def route_question_vote(question_id):
    question.update_vote(question_id, request.form['vote_button'])
    user.update_prestige_for_question(question_id, request.form['vote_button'])
    return redirect(url_for('route_question_view',
                            question_id=question_id))


# /add answer, /vote answer, /edit answer, /delete answer part, /accept answer
@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
@login_required
def route_post_answer(question_id):
    if request.method == 'GET':
        return render_template('add_or_update_answer.html',
                               form_url=url_for('route_post_answer',
                                                question_id=question_id),
                               question_id=question_id)

    elif request.method == 'POST':
        try:
            new_answer = {'message': escape(answer.validate_message(request.form.get('message'))),
                          'image': request.form.get('image'),
                          'user_id': session.get('id')}
        except answer.WrongLength:
            flash(message='Length of text must be correct')
            return redirect(url_for('route_post_answer',
                                    question_id=question_id))

        try:
            answer.add(question_id, new_answer)
        except answer.SavingDataProblem:
            flash('Your answer will be verified and added within 24 hours.')
        finally:
            return redirect(url_for('route_question_view',
                                    question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>', methods=['POST'])
@login_required
def route_answer_vote(question_id, answer_id):
    answer.update_vote(answer_id, request.form.get('vote_button'))
    user.update_prestige_for_answer(answer_id, request.form.get('vote_button'))
    return redirect(url_for('route_question_view',
                            question_id=question_id))


@app.route('/answer/<int:answer_id>/edit')
@login_required
def route_show_edit_answer_form(answer_id):
    try:
        answer_to_edit = answer.get_one_with_author(answer_id)

        if session['id'] == answer_to_edit['user_id']:
            return render_template('add_or_update_answer.html',
                                   answer=answer_to_edit,
                                   form_url=url_for('route_show_edit_answer_form',
                                                    answer_id=answer_id))
        else:
            flash("Only author can edit this answer")
            return redirect(url_for('route_question_view',
                                    question_id=answer_to_edit['question_id']))

    except answer.ReadingProblem:
        flash('We are sorry but editing this answer is not possible now. Please try again in few minutes')
        return redirect(url_for('route_main'))


@app.route('/answer/<int:answer_id>/edit', methods=['POST'])
@login_required
def route_save_edit_answer(answer_id):
    question_id = answer.find_question_id_in(answer_id)
    try:
        edited_answer = {'message': escape(answer.validate_message(request.form.get('message'))),
                         'image': escape(request.form.get('image'))}

    except answer.WrongLength:
        flash('Length of text must be correct')
        return redirect(url_for('route_show_edit_answer_form',
                                answer_id=answer_id))

    try:
        answer.update(answer_id, edited_answer)
    except answer.SavingDataProblem:
        flash('Your answer will be verified and updated within 24 hours.')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/answer/<int:answer_id>/delete', methods=['POST'])
@login_required
def route_delete_answer(answer_id):
    try:
        question_id = answer.delete_and_return_question_id(answer_id)
        return redirect(url_for('route_question_view',
                                question_id=question_id))
    except answer.DeletingProblem:
        flash('Your answer will be deleted in 24 hours.')
        return redirect(url_for('route_main'))


@app.route('/answer/<int:answer_id>/accept', methods=['POST'])
@login_required
def route_accept_answer(answer_id):
    question_id = answer.find_question_id_in(answer_id)
    try:
        answer.accept(answer_id)
        user.update_prestige_for_accepted(answer_id)
        flash(message='You accepted answer! Thank you for contribution :)')
    except answer.SavingDataProblem:
        flash(message='Some problem occurred. We will add your acceptance in next 24 hours.')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


# /add comment - question, /add comment - answer, /edit comment, /delete comment
@app.route('/question/<int:question_id>/new-comment', methods=['GET', 'POST'])
@login_required
def route_add_question_comment(question_id):
    if request.method == 'GET':
        return render_template('add_or_update_comment.html',
                               form_url=url_for('route_add_question_comment',
                                                question_id=question_id))
    elif request.method == 'POST':
        try:
            new_comment = {'question_id': question_id,
                           'message': escape(comment.validate_message(request.form['message'])),
                           'user_id': session.get('id')}
        except comment.WrongLength:
            flash('Length of text must be correct')
            return redirect(url_for('route_add_question_comment',
                                    question_id=question_id))

        try:
            comment.add_to_question(new_comment)
        except comment.SavingDataProblem:
            flash('Your comment will be verified and added within 24 hours.')
        finally:
            return redirect(url_for('route_question_view',
                                    question_id=question_id))


@app.route('/answer/<int:answer_id>/new-comment', methods=['GET', 'POST'])
@login_required
def route_add_answer_comment(answer_id):
    question_id = answer.find_question_id_in(answer_id)
    if request.method == 'GET':
        return render_template('add_or_update_comment.html',
                               form_url=url_for('route_add_answer_comment',
                                                answer_id=answer_id))
    elif request.method == 'POST':
        try:
            new_comment = {'answer_id': answer_id,
                           'message': escape(comment.validate_message(request.form['message'])),
                           'user_id': session.get('id')}
        except comment.WrongLength:
            flash('Length of text must be correct')
            return redirect(url_for('route_add_answer_comment',
                                    answer_id=answer_id))

        try:
            comment.add_to_answer(new_comment)
        except comment.SavingDataProblem:
            flash('Your comment will be verified and added within 24 hours.')
        finally:
            return redirect(url_for('route_question_view',
                                    question_id=question_id))


@app.route('/comment/<int:comment_id>/edit')
@login_required
def route_show_edit_comment_form(comment_id):
    try:
        comment_to_edit = comment.get_by_id(comment_id)

        if session['id'] == comment_to_edit['user_id']:
            return render_template('add_or_update_comment.html',
                                   comment=comment_to_edit,
                                   form_url=url_for('route_show_edit_comment_form',
                                                    comment_id=comment_id))
        else:
            flash("Only author can edit this comment")
            return redirect(url_for('route_main'))

    except comment.ReadingProblem:
        flash('We are sorry but editing this comment is not possible now. Please try again in few minutes')
        return redirect(url_for('route_main'))


@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def route_edit_comment(comment_id):
    comment_to_edit = comment.get_by_id(comment_id)
    question_id = comment.find_question_id_for(comment_id)
    try:
        new_comment = {'message': escape(comment.validate_message(request.form.get('message'))),
                       'edited_count': comment.raise_edited_count(comment_to_edit)}
    except comment.WrongLength:
        flash(message='Length of text must be correct')
        return redirect(url_for('route_show_edit_comment_form',
                                comment_id=comment_id))

    try:
        comment.update(comment_id, new_comment)
    except comment.SavingDataProblem:
        flash('Your comment will be verified and added within 24 hours.')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def route_delete_comment(comment_id):
    question_id = comment.find_question_id_for(comment_id)
    try:
        comment.delete(comment_id)
    except comment.DeletingProblem:
        flash('Your comment will be deleted in 24 hours.')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


# /add new tag, /delete tag, /show all tags with counted questions
@app.route('/question/<int:question_id>/new-tag')
@login_required
def route_show_add_tag_page(question_id):
    try:
        tags = tag.get_all()
        return render_template('add_tag.html',
                               tags=tags,
                               question_id=question_id)
    except tag.ReadingProblem:
        flash('Adding tags in not possible right now. Please try again in few minutes')
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/question/<int:question_id>/new-tag', methods=['POST'])
@login_required
def route_add_tag(question_id):
    try:
        tag.add_chosen(question_id, request.form.getlist('existing_tag'))
        tag.add_new(question_id, request.form.get('tag'))
    except tag.SavingDataProblem:
        flash('Your tag(s) will be verified and added in 24 hours')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def route_delete_tags(question_id, tag_id):
    try:
        tag.delete_from_question(question_id, tag_id)
    except tag.DeletingProblem:
        flash('Your tag will be deleted in 24 hours')
    finally:
        return redirect(url_for('route_question_view',
                                question_id=question_id))


@app.route('/tags')
def route_show_tags_with_counted_questions():
    try:
        tags_with_counted_questions = tag.get_with_counted_questions()
        return render_template("all_tags.html",
                               tags=tags_with_counted_questions)
    except tag.ReadingProblem:
        flash('Sorry, tags page is not available. Please try again in few minutes')
        return redirect(url_for('route_main'))


# registration, login, logout, all users, one user activity
@app.route('/registration')
@login_forbidden
def route_show_register_form():
    return render_template('registration.html',
                           form_url='/registration')


@app.route('/registration', methods=['POST'])
@login_forbidden
def route_user_register():
    username = escape(request.form.get('username'))
    first_password = escape(request.form.get('password_one'))
    validation_password = escape(request.form.get('password_two'))

    if not user.is_all_data_validate(username, first_password, validation_password):
        flash('Please provide all data')
        return redirect(url_for('route_show_register_form'))

    if user.is_exist_already(username):
        flash('This username exist already')
        return redirect(url_for('route_show_register_form'))

    if not user.is_passwords_equal(first_password, validation_password):
        flash('Passwords must be equal')
        return redirect(url_for('route_show_register_form'))

    user_data = user.registration(username, first_password)
    return redirect(url_for('route_main'))


@app.route('/login')
@login_forbidden
def route_show_login_form():
    return render_template('registration.html',
                           form_url='/login')


@app.route('/login', methods=['POST'])
@login_forbidden
def route_login():
    username = request.form.get('username')
    password = request.form.get('password_one')
    try:
        user_id = user.get_id_by_username(username)
        if user.verify_password(username, password):
            session['username'] = username
            session['id'] = user_id
            flash('Welcome {0}'.format(username))
            return redirect(url_for('route_main'))
        else:
            flash('Wrong password')
            return redirect(url_for('route_show_login_form'))

    except user.WrongUsername:
        flash('Such user do not exist')
        return redirect(url_for('route_show_login_form'))


@app.route('/logout')
@login_required
def route_logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect(url_for('route_main'))


@app.route('/all-users')
def route_all_users():
    try:
        all_users = user.get_all()
        return render_template('all_users.html',
                               all_users=all_users)
    except user.ReadingProblem:
        flash('This page is being updated. Please try again in few minutes.')
        return redirect(url_for('route_main'))


@app.route('/user/<int:user_id>')
def route_user(user_id):
    try:
        user_data = user.get_by_id(user_id)
        user_questions, user_answers, user_comments = user.get_all_activity(user_id)
        return render_template('user_page.html',
                               user_data=user_data,
                               user_questions=user_questions,
                               user_answers=user_answers,
                               user_comments=user_comments)
    except user.ReadingProblem:
        flash('We cannot show you your activity right now.')
        return redirect(url_for('route_main'))


if __name__ == "__main__":
    app.run(debug=True,
            host='127.0.0.1',
            port=5000)
