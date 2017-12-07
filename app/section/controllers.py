# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user


section = Blueprint('section', __name__, url_prefix='/section')

@section.route('/<int:id>', methods=['GET'])
def index(id):
    return render_template("section/index.html")