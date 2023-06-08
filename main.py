from flask import Flask, redirect, url_for, render_template, session, request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your own secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Google OAuth configuration
google_blueprint = make_google_blueprint(client_id='151500634911-ul5daj51rh6ebc57btq18gpjogh277tr.apps.googleusercontent.com',
                                         client_secret='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',
                                         scope=['profile', 'email'],
                                         redirect_url='http://localhost:5000/login/google/callback'
                                         )

app.register_blueprint(google_blueprint, url_prefix='/login')


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)


# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    votes = db.Column(db.Integer, default=0)


# Home page
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts, google=google)


# Create post
@app.route('/create', methods=['GET', 'POST'])
def create():
    if not google.authorized:
        return redirect(url_for('google.login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('create.html')


# Upvote post
@app.route('/upvote/<int:post_id>')
def upvote(post_id):
    post = Post.query.get(post_id)
    post.votes += 1
    db.session.commit()
    return redirect(url_for('home'))


# Downvote post
@app.route('/downvote/<int:post_id>')
def downvote(post_id):
    post = Post.query.get(post_id)
    post.votes -= 1
    db.session.commit()
    return redirect(url_for('home'))


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
