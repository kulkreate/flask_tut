import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Table

#import sqlalchemy as sa
#from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Query, scoped_session, sessionmaker
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
engine = create_engine("mariadb+mariadbconnector://sqlkiddie3:SuperUnsicheresPasswort@127.0.0.1:3306/spielwiese_philipp")
Base = declarative_base()
Base.metadata.reflect(engine)
db_session = scoped_session(sessionmaker(bind=engine))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

#class Schueler(Base):
#    __table__ = Base.metadata.tables['SCHUELER']

class Schueler(Base):
    __table__ = Table('SCHUELER', Base.metadata, autoload=True, autoload_with=engine)

#class Schueler(Base):
#    __tablename__ = 'SCHUELER'
#    db_schueler_id = sa.Column(sa.VARCHAR, primary_key=True)
#    db_email = sa.Column(sa.VARCHAR)
#    db_username = sa.Column(sa.VARCHAR)
#    db_passwort = sa.Column(sa.VARCHAR)
#    db_vorname = sa.Column(sa.VARCHAR)
#    db_nachname = sa.Column(sa.VARCHAR)


#class Student(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    firstname = db.Column(db.String(100), nullable=False)
#    lastname = db.Column(db.String(100), nullable=False)
#    email = db.Column(db.String(80), unique=True, nullable=False)
#    age = db.Column(db.Integer)
#    created_at = db.Column(db.DateTime(timezone=True),
#                           server_default=func.now())
#    bio = db.Column(db.Text)
#
#   def __repr__(self):
#        return f'<Student {self.firstname}>'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bestellungen')
def bestellungen():
    result = db_session.query(Bestellung.db_bestellung_id, Bestellung.db_kurs_id, Bestellung.db_schueler_id)
    return render_template('bestellungen.html', bestellung=result)

@app.route('/schueler')
def schueler():
    result = db_session.query(Schueler.db_vorname, Schueler.db_nachname, Schueler.db_schueler_id)
    return render_template('schueler.html', schueler=result)

@app.route('/dozenten')
def dozenten():
    result = db_session.query(Dozent.db_vorname, Dozent.db_nachname, Dozent.db_dozent_id)
    return render_template('dozenten.html', dozenten=result)

@app.route('/kurse')
def kurse():
    result = db_session.query(Kurs.db_kurs_titel, Kurs.db_kurs_id, Kurs.db_dozent_id)
    return render_template('kurse.html', kurse=result)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        id = int(request.form['id'])
        email = request.form['email']
        username = request.form['username']
        passwort = request.form['passwort']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        schueler = Schueler(db_schueler_id=id,
                            db_email=email,
                            db_username=username,
                            db_passwort=passwort,
                            db_nachname=nachname,
                            db_vorname=vorname,)
        db.session.add(schueler)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)