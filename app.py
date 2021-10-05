from flask import Flask, render_template, abort, session, redirect, url_for
from forms import LoginForm, SignupForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paws.db'
db = SQLAlchemy(app)

"""Information regarding pets in the system."""
pets = [
    {"id": 1, "name": "Nelly", "age": "5 weeks", "bio": "I am a tiny kitten rescued by the good people at Paws "
                                                        "Rescue Center. I love squeaky toys and cuddles."},
    {"id": 2, "name": "Yuki", "age": "8 months", "bio": "I am a handsome gentle-cat. I like to dress "
                                                        "up in bow ties."},
    {"id": 3, "name": "Basker", "age": "1 year", "bio": "I love barking. But, I love my friends more."},
    {"id": 4, "name": "Mr. Furrkins", "age": "5 years", "bio": "Probably napping."},
]

"""Information regarding the Users in the System"""
users = [
    {"id": 1, "full_name": "Pet Rescue Team", "email": "team@pawsrescue.co", "password": "adminpass"},
]


class User(db.Model):
    """Model for Users."""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    pets = db.relationship('Pet', backref='user')


class Pet(db.Model):
    """Model for Pets."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    age = db.Column(db.String)
    bio = db.Column(db.String)
    posted_by = db.Column(db.String, db.ForeignKey('user.id'))


db.create_all()

# Create 'team' user and add it to session
team = User(full_name="Pet Rescue Team", email="team@petrescue.co", password="adminpass")
db.session.add(team)

# Create pet objects and add to the session
nelly = Pet(name = "Nelly", age = "5 weeks", bio = "I am a tiny kitten rescued by the good people at Paws Rescue "
                                                   "Center. I love squeaky toys and cuddles.")
yuki = Pet(name = "Yuki", age = "8 months", bio = "I am a handsome gentle-cat. I like to dress up in bow ties.")
basker = Pet(name = "Basker", age = "1 year", bio = "I love barking. But, I love my friends more.")
mrfurrkins = Pet(name = "Mr. Furrkins", age = "5 years", bio = "Probably napping.")

db.session.add(nelly)
db.session.add(yuki)
db.session.add(basker)
db.session.add(mrfurrkins)


# Commit changes in the session
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
finally:
    db.session.close()


@app.route("/")
def homepage():
    pets = Pet.query.all()
    return render_template("home.html", pets=pets)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/details/<int:pet_id>")
def pet_details(pet_id):
    """View function for Showing Details of Each Pet."""
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="No Pet was Found with the given ID")
    return render_template("details.html", pet=pet)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first
        if user is None:
            return render_template("login.html", form=form, message="Wrong Credentials. Please Try Again.")
        else:
            session['user'] = user.id
            return render_template("login.html", message="Successfully Logged In!")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('homepage', _scheme='https', _external=True))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(full_name=form.full_name, email=form.email)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template("signup.html", form=form,
                                   message="This Email already exists in the system! Please Log in instead.")
        finally:
            db.session.close()
        return render_template("signup.html", message="Successfully signed up")
    return render_template("signup.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
