from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm, DeleteForm
from app.models import User, Post


def humanize_ts(timestamp=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """

    now = datetime.utcnow()
    diff = now - timestamp
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(int(second_diff)) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


@app.route('/')
@app.route('/index')
def index():
    posts_and_users = db.session.query(Post, User).filter(User.id == Post.user_id). \
        order_by(Post.timestamp.desc()).all()

    return render_template('index.html', title='Home', posts=posts_and_users, show_all=True)

@app.route('/')
@app.route('/user/<id>')
def user(id):
    posts_and_users = db.session.query(Post, User).filter(User.id == Post.user_id). \
        filter(User.id == id).order_by(Post.timestamp.desc()).all()

    return render_template('index.html', title='User', posts=posts_and_users, show_all=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('User logged in successfully!')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(text_jp=form.text_jp.data, text_en=form.text_en.data,
                    notes=form.notes.data, user_id=current_user.get_id())

        db.session.add(post)
        db.session.commit()
        flash('Congratulations, post added!')
        return redirect(url_for('index'))
    return render_template('add.html', title='Add', form=form)


@app.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = db.session.query(Post).filter(Post.id == id).first()

    if post is None:
        flash("Cannot delete post, not found!", "warning")
        return redirect(url_for('index'))

    if int(current_user.get_id()) != post.user_id:
        flash("Can only delete own posts!", 'danger')

        return redirect(url_for('index'))

    form = DeleteForm()
    if form.validate_on_submit():
        flash("Post deleted.", 'info')

        db.session.query(Post).filter(Post.id == id).delete()
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('delete.html', title='Delete', form=form, id=id, post=post)
