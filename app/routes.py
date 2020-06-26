from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm
from app.models import User, Post


@app.route('/')
@app.route('/index')
def index():
    posts_and_users = db.session.query(Post, User).filter(User.id == Post.user_id). \
        order_by(Post.timestamp.desc()).all()

    return render_template('index.html', title='Home', posts=posts_and_users)


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
        flash('Congratulations, you are now a registered user!')
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
