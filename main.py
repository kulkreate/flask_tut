import os

from flask import Flask, escape, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_login.utils import fresh_login_required, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, scoped_session, sessionmaker

from user import User

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()

app = Flask(__name__)

engine = create_engine("mariadb+mariadbconnector://sqlkiddie3:SuperUnsicheresPasswort@127.0.0.1:3306/spielwiese_philipp")
Base = declarative_base()
Base.metadata.reflect(engine)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\xeaF\xa9\x88\xda\xf6\x82\xf4\xa7=\xd6\xa0\xeb[F\xd1A6G\xe0\xc6W2\xb0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

login_manager = LoginManager()
login_manager.init_app(app)

db_session = scoped_session(sessionmaker(bind=engine))
db.init_app(app)

class Bestellung(Base):
    __table__ = Base.metadata.tables['BESTELLUNG']

class Dozent(Base):
    __table__ = Base.metadata.tables['DOZENT']

class Kategorie(Base):
    __table__ = Base.metadata.tables['KATEGORIE']

class Kurs(Base):
    __table__ = Base.metadata.tables['KURS']

class Preisklasse(Base):
    __table__ = Base.metadata.tables['PREISKLASSE']

class Schueler(Base):
    __table__ = Base.metadata.tables['SCHUELER']

dozent_email = db_session.query(Dozent.db_email)
dozenten = db_session.query(Dozent.db_email, Dozent.db_passwort)

def find_in_user_dic(email):
    if dozent_email[0][email]:
        return User(email, dozenten[0][0], 'dozent', 'salt')
    return None

@login_manager.user_loader
def load_user(id):
    return find_in_user_dic(id.decode('ascii'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        l_email = request.form['email']
        l_passwort = request.form['passwort']

        if Dozent(db_email=l_email, db_passwort=l_passwort):
            dozent = User(l_email, l_passwort, 'dozent', 'salt')
            login_user(dozent, remember=False)
            return redirect('/')
        else:
            return redirect('/login')

    if request.method == 'GET':
        return render_template('login.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        passwort = request.form['passwort']
        nachname = request.form['nachname']
        vorname = request.form['vorname']

        # user = db_session.query(Dozent.db_email)

        # if user:
        #     return redirect(url_for('signup'))

        id = db_session.query(Dozent.db_dozent_id)
        new_id_str = str(id)
        new_id = int(new_id_str) + 1

        dozenten = Dozent(db_dozent_id=new_id + 1,
                            db_email=email,
                            db_username=username,
                            db_passwort=passwort,
                            db_nachname=nachname,
                            db_vorname=vorname)

        db_session.add(dozenten)
        db_session.commit()

        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/')
# @login_required
def index():
    return render_template('index.html')

@app.route('/bestellungen')
@login_required
def bestellungen():
    result = db_session.query(Bestellung.db_bestellung_id, Bestellung.db_schueler_id, Bestellung.db_kurs_id, Bestellung.db_bestellstatus, Bestellung.db_bestelldatum)
    return render_template('bestellungen.html', bestellung=result)

@app.route('/bestellungen', methods=('GET', 'POST'))
@login_required
def create_bestellungen():
    if request.method == 'POST':
        id = int(request.form['id'])
        schueler = request.form['schueler']
        kurs = request.form['kurs']
        status = request.form['status']
        datum = request.form['datum']
        bestellung = Bestellung(db_bestellung_id=id,
                            db_schueler_id=schueler,
                            db_kurs_id=kurs,
                            db_bestellstatus=status,
                            db_bestelldatum=datum)
        db_session.add(bestellung)
        db_session.commit()

        return redirect(url_for('bestellungen'))

    return render_template('bestellungen.html')

@app.route('/schueler')
@login_required
def schueler():
    result = db_session.query(Schueler.db_schueler_id, Schueler.db_email, Schueler.db_username, Schueler.db_vorname, Schueler.db_nachname)
    return render_template('schueler.html', schueler=result)

@app.route('/schueler', methods=('GET', 'POST'))
@login_required
def create_schueler():
    if request.method == 'POST':
        id = int(request.form['id'])
        email = request.form['email']
        username = request.form['username']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        schueler = Schueler(db_schueler_id=id,
                            db_email=email,
                            db_username=username,
                            db_nachname=nachname,
                            db_vorname=vorname)
        db_session.add(schueler)
        db_session.commit()

        return redirect(url_for('schueler'))

    return render_template('schueler.html')


@app.route('/dozenten')
@login_required
def dozenten():
    result = db_session.query(Dozent.db_dozent_id, Dozent.db_email, Dozent.db_username, Dozent.db_vorname, Dozent.db_nachname)
    return render_template('dozenten.html', dozenten=result)

@app.route('/dozenten', methods=('GET', 'POST'))
@login_required
def create_dozent():
    if request.method == 'POST':
        id = int(request.form['id'])
        email = request.form['email']
        username = request.form['username']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        dozent = Dozent(db_dozent_id=id,
                            db_email=email,
                            db_username=username,
                            db_nachname=nachname,
                            db_vorname=vorname)
        db_session.add(dozent)
        db_session.commit()

        return redirect(url_for('dozenten'))

    return render_template('dozenten.html')

# @app.route('/kurse')
# # @login_required
# def kurse():
#     result = db_session.query(Kurs.db_kurs_id, Kurs.db_kurs_titel, Kurs.db_dozent_id, Kurs.db_kategorie_id,)
#     return render_template('kurse.html', kurse=result)

@app.route('/kurse', methods=('GET', 'POST'))
@login_required
def kurse():
    result = db_session.query(Kurs.db_kurs_id, Kurs.db_kurs_titel, Kurs.db_dozent_id, Kurs.db_kategorie_id,)
    return render_template('kurse.html', kurse=result)

@app.route('/kurse', methods=('GET', 'POST'))
@login_required
def create_kurs():
    if request.method == 'POST':
        id = int(request.form['id'])
        titel = request.form['titel']
        dozent = request.form['dozent']
        kategorie = request.form['kategorie']
        kurs = Kurs(db_kurs_id=id,
                    db_kurs_titel=titel,
                    db_dozent_id=dozent,
                    db_kategorie_id=kategorie)
        db_session.add(kurs)
        db_session.commit()

        return redirect(url_for('kurse'))

    return render_template('kurse.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)