import os
import uuid

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.utils import secure_filename

from flask import current_app as app

from app.section.models import SectionRepository
from app.file.models import File, FileRepository

from app.file.forms import NewFileForSectionForm

section = Blueprint('section', __name__, url_prefix='/section')

@section.route('/<int:id>', methods=['GET'])
def index(id):
    section = SectionRepository.find_by_id(id)
    return render_template("section/index.html", section=section)


@section.route('/<int:id>/files', methods=['GET', 'POST'])
def files(id):
    section = SectionRepository.find_by_id(id)
    files = FileRepository.find_files_of_section(section.id)
    form = NewFileForSectionForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(f.filename)[1])
        f.save(os.path.join(app.config['UPLOAD_DIR'], 'files', filename))
        file = File()
        file.course_id = section.course_id
        file.section_id = section.id
        file.user_id = current_user.id
        file.section_only = form.section_only.data
        file.title = form.title.data
        file.filename = filename
        file.original_filename = f.filename
        file.content_type = f.content_type
        file = FileRepository.create(file)
        return redirect(url_for('section.files', id=id))
    return render_template("section/files.html", section=section, files=files, form=form, current_user=current_user)


