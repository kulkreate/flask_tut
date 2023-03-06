import os
import bcrypt
from flask import Flask, escape, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_login.utils import fresh_login_required, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, asc, desc, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, scoped_session, sessionmaker
from sqlalchemy.sql.expression import exists
from user import User

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app = Flask(__name__)

engine = create_engine("mariadb+mariadbconnector://sqlkiddie3:SuperUnsicheresPasswort@127.0.0.1:3306/spielwiese_philipp")
Base = declarative_base()
Base.metadata.reflect(engine)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
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

dozent_data  = db_session.query(Dozent.db_email, Dozent.db_passwort)

def find_in_user_dic(email):
    if dozent_data[0]:
        return User(email, dozent_data[0][0], 'dozent', 'salt')
    return None

@login_manager.user_loader
def load_user(id):
    return find_in_user_dic(id.decode('ascii'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

@app.route('/registrieren', methods=('GET', 'POST'))
def registrieren():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        passwort = request.form['passwort']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        b_passwort = passwort.encode('utf-8')
        salt = bcrypt.gensalt()
        hashedpw = bcrypt.hashpw(b_passwort, salt)
        id = db_session.query(Dozent.db_dozent_id).order_by(desc(Dozent.db_dozent_id))
        dozenten = Dozent(db_dozent_id=id[0][0]+1,
                            db_email=email,
                            db_username=username,
                            db_passwort=hashedpw,
                            db_nachname=nachname,
                            db_vorname=vorname)
        db_session.add(dozenten)
        db_session.commit()
        dozent = User(email, passwort, 'dozent', 'salt')
        login_user(dozent, remember=False)
        return redirect(url_for('index'))
    return render_template('registrieren.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        l_email = request.form['email']
        l_passwort = request.form['passwort']
        byte_l_passwort = l_passwort.encode('utf-8')
        checkin = login_check(l_email, l_passwort, byte_l_passwort)
        if checkin == True:
            return redirect('/')
        else:
            return redirect('/login')
    if request.method == 'GET':
        return render_template('login.html')

def login_check(l_email, l_passwort, byte_l_passwort):
    dbpw = None
    dbpw_query = select(Dozent.db_passwort).where(Dozent.db_email==l_email)
    with engine.connect() as conn:
        for pwdic in conn.execute(dbpw_query):    
            dbpw = bytes(pwdic[0], 'utf-8')
    if dbpw != None and bcrypt.checkpw(byte_l_passwort, dbpw):
        dozent = User(l_email, l_passwort, 'dozent', 'salt')
        login_user(dozent, remember=False)
        return True

    # verify_login = db_session.query(Dozent).filter(Dozent.db_email=='timokeller@gmail.com', Dozent.db_passwort=='Hallo123?')
    # print(db_session.query(verify_login.exists()).scalar())

    # Mithilfe von Login-Email dazugehöriges verschl. PW abfragen
    # dbpw_query = select(Dozent.db_passwort).where(Dozent.db_email=='ogreco@gmail.com')
    # with engine.connect() as conn:
    #     for pwdic in conn.execute(dbpw_query):    
    #         dbpw = bytes(pwdic[0], 'utf-8')

    # testpw = 'Hallo'
    # testpw_b = testpw.encode('utf-8')
    # if bcrypt.checkpw(testpw_b, dbpw):
    #     print('Es hat geklappt')

    # def check_login(l_email, l_passwort, byte_l_passwort):
    #     a_data = db_session.query(Dozent.db_email, Dozent.db_passwort)
    #     for email, passwort in a_data:
    #         byte_passwort = bytes(passwort, 'utf-8')
    #         if l_email == email and bcrypt.checkpw(byte_l_passwort, byte_passwort):
    #             dozent = User(l_email, l_passwort, 'dozent', 'salt')
    #             login_user(dozent, remember=False)
    #             return True

@app.route("/logout", methods=["GET"])
def logout():
    if not current_user.is_authenticated:
        return redirect("/login")
    logout_user()
    return redirect("/login")

@app.route('/')
@login_required
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
        #id = int(request.form['id'])
        email = request.form['email']
        username = request.form['username']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        schueler = Schueler(#db_schueler_id=id,
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

@app.route('/kurse', methods=('GET', 'POST'))
@login_required
def kurse():
    result = db_session.query(Kurs.db_kurs_id, Kurs.db_kurs_titel, Kurs.db_dozent_id, Kurs.db_kategorie_id,)
    return render_template('kurse.html', kurse=result)

@app.route('/kurse', methods=('GET', 'POST'))
@login_required
def create_kurs():
    if request.method == 'POST':
        #id = int(request.form['id'])
        titel = request.form['titel']
        dozent = request.form['dozent']
        kategorie = request.form['kategorie']
        kurs = Kurs(#db_kurs_id=id,
                    db_kurs_titel=titel,
                    db_dozent_id=dozent,
                    db_kategorie_id=kategorie)
        db_session.add(kurs)
        db_session.commit()
        return redirect(url_for('kurse'))
    return render_template('kurse.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)