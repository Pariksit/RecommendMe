from flask import render_template, url_for, flash, redirect,request
from flaskblog import app,db,bcrypt
from flaskblog.forms import RegistrationForm, LoginForm,UpdateAccountForm
from flaskblog.models import User,Post
import json
import requests 
import secrets
import os
from PIL import Image 
from flask_login import login_user,current_user,logout_user,login_required


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

tmdb_api_key="6aea1175d1a4e027fc1721b35947dd9f"

@app.route("/")
@app.route("/home")
def home():
    response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' +  tmdb_api_key)
    display = response.json()
    display_movies=display['results']
    r = json.dumps(display_movies)
    loaded_r = json.loads(r)
    movie_info={}
    for i in loaded_r:
        movie_title=i['original_title']
        movie_poster=i['poster_path']
        movie_info[movie_title]=movie_poster
    #return render_template('test.html',movie_info=movie_info)
    return render_template('home.html',movie_info=movie_info)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password,
            fav_actor=form.fav_actor.data,fav_director=form.fav_director.data,fav_genre=form.fav_genre.data,
            fav_movie=form.fav_movie.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    actor_info='Christane Bale'
    #response=requests.get('http://api.tmdb.org/3/search/person?api_key='+tmdb_api_key '&query='+current_user.fav_actor)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fav_actor = form.fav_actor.data
        current_user.fav_director = form.fav_director.data
        current_user.fav_genre = form.fav_genre.data
        current_user.fav_movie = form.fav_movie.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method== 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fav_actor.data = current_user.fav_actor
        form.fav_director.data = current_user.fav_director
        form.fav_genre.data = current_user.fav_genre
        form.fav_movie.data = current_user.fav_movie

    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    #response=requests.get('http://api.tmdb.org/3/search/person?api_key='+tmdb_api_key '&query='+current_user.fav_actor)
    actor_info=current_user.fav_actor
    return render_template('account.html',title="Account",image_file=image_file,form=form,actor_info=actor_info)