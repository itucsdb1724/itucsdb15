import os

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_required, logout_user

from flask import current_app as app

from app.message.models import MessageRepository

message = Blueprint('message', __name__, url_prefix='/messages')

@message.route('/<int:id>/trigger_section_only', methods=['GET'])
@login_required
def trigger_section_only(id):
    current_message = MessageRepository.find_by_id(id)
    if current_message.user_id == current_user.id:
        MessageRepository.update_section_only(current_message.id, not current_message.section_only)
    if request.args.get('from') == 'section':
        return redirect(url_for('section.threads', id=current_message.section_id))
    else:
        return redirect(url_for('home_page'))


@message.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    current_message = MessageRepository.find_by_id(id)
    if current_message.user_id == current_user.id:
        MessageRepository.delete(current_message.id)
    if request.args.get('from') == 'section':
        return redirect(url_for('section.threads', id=current_message.section_id))
    elif request.args.get('from') == 'thread':
        return redirect(url_for('section.messages', section_id=current_message.section_id, id=current_message.thread_id))
    else:
        return redirect(url_for('home_page'))

