import os
from flask import Flask, render_template, request, url_for, redirect, escape

from flask import Blueprint
from . import db

main = Blueprint('main', __name__)



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



@main.route('/')
def index():
    return render_template('index.html')

@main.route('/bestellungen')
def bestellungen():
    result = db_session.query(Bestellung.db_bestellung_id, Bestellung.db_schueler_id, Bestellung.db_kurs_id, Bestellung.db_bestellstatus, Bestellung.db_bestelldatum)
    return render_template('bestellungen.html', bestellung=result)

@main.route('/bestellungen', methods=('GET', 'POST'))
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




@main.route('/schueler')
def schueler():
    result = db_session.query(Schueler.db_schueler_id, Schueler.db_email, Schueler.db_username, Schueler.db_vorname, Schueler.db_nachname)
    return render_template('schueler.html', schueler=result)

@main.route('/schueler', methods=('GET', 'POST'))
def create_schueler():
    if request.method == 'POST':
        id = int(request.form['id'])
        email = request.form['email']
        username = request.form['username']
#       passwort = request.form['passwort']
        nachname = request.form['nachname']
        vorname = request.form['vorname']
        schueler = Schueler(db_schueler_id=id,
                            db_email=email,
                            db_username=username,
#                           db_passwort=passwort,
                            db_nachname=nachname,
                            db_vorname=vorname)
        db_session.add(schueler)
        db_session.commit()

        return redirect(url_for('schueler'))

    return render_template('schueler.html')


@main.route('/dozenten')
def dozenten():
    result = db_session.query(Dozent.db_vorname, Dozent.db_nachname, Dozent.db_dozent_id)
    return render_template('dozenten.html', dozenten=result)

@main.route('/kurse')
def kurse():
    result = db_session.query(Kurs.db_kurs_titel, Kurs.db_kurs_id, Kurs.db_dozent_id)
    return render_template('kurse.html', kurse=result)


if __name__ == '__main__':
    main.run(host='127.0.0.1', port='5000', debug=True)