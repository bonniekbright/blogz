from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

def validate_username(username):
    username, username_error = username, ""
    user = User.query.filter_by(username=username).first()
    if username == "":
        username_error = "No username entered."
    elif len(username) < 3 or len(username) > 20:
        username_error = "Username must be between 3 and 20 characters."
        username = ""
    elif " " in username:
        username_error = "You can not use a space in the username."
        username = ""
    elif user != None:
        username_error = "Your chosen username is already taken. Please choose another one."
        username = ""
    return username, username_error

def validate_password(password):
    password, password_error = password, ""
    if password == "":
        password_error = "No password entered."
    elif len(password) < 3 or len(password) > 20:
        password_error = "Password must be between 3 and 20 characters."
        password = ""
    elif " " in password:
        password_error = "You can not use a space in the password."
        password = ""
    return password, password_error

def validate_verify(verify):
    verify, verify_error = verify, ""
    password = request.form['password']
    if verify == "":
        verify_error = "No verify password was entered"
    elif verify != password:
        verify_error = "Passwords do not match. Reenter password."
        verify = ""
        password = ""
    return verify, verify_error



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template("entry.html", blog_id = blog_id, blog=blog)
    
    blog_entries = Blog.query.all()

    return render_template('blog.html', title="Blog", 
    blog_entries=blog_entries)


@app.route('/new-entry', methods=["POST", "GET"])
def add_entry():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner_id = request.form['owner-id']
        if not title:
            error = "Blog entry must contain both a title and content"
            return render_template("new-entry.html", error=error, body=body)
        if not body:
            error = "Blog entry must contain both a title and content"
            return render_template("new-entry.html", error=error, title=title)
        title = request.form['title']
        body = request.form['body']
        owner_id = request.form['owner_id']        
        new_entry = Blog(title, body, owner_id)
        db.session.add(new_entry)
        db.session.commit()
        blog_id = new_entry.id
        blog = Blog.query.get(blog_id)
        return redirect("/blog?id=" + str(new_entry.id))
    return render_template('new-entry.html', page_title="Add a New Entry")

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')



@app.route("/validate", methods=['POST'])
def validate():
    username, username_error = validate_username(request.form["username"])
    password, password_error = validate_password(request.form["password"])
    verify, verify_error = validate_verify(request.form["verify"])

    if not username_error and not password_error and not verify_error:
        print("this is where the user gets created")
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('blog.html', username = username)
    else:
        return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, 
        verify_error = verify_error)


if __name__ == '__main__':
    app.run()

