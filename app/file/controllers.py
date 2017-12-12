import os

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_required, logout_user

from flask import current_app as app

from app.file.models import File, FileRepository

file = Blueprint('file', __name__, url_prefix='/files')

@file.route('/<int:id>/trigger_section_only', methods=['GET'])
@login_required
def trigger_section_only(id):
    current_file = FileRepository.find_by_id(id)
    if current_file.user_id == current_user.id:
        FileRepository.update_section_only(current_file.id, not current_file.section_only)

    if request.args.get('from') == 'section':
        return redirect(url_for('section.files', id=current_file.section_id))
    else:
        return redirect(url_for('course.files', id=current_file.course_id))


@file.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    current_file = FileRepository.find_by_id(id)
    if current_file.user_id == current_user.id:
        if FileRepository.delete(current_file.id):
            os.remove(os.path.join(app.config['UPLOAD_DIR'], 'files', current_file.filename))

    if request.args.get('from') == 'section':
        return redirect(url_for('section.files', id=current_file.section_id))
    else:
        return redirect(url_for('course.files', id=current_file.course_id))

