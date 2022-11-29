from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, scoped_session, sessionmaker

app = Flask(__name__)
engine = create_engine("mariadb+mariadbconnector://sqlkiddie3:SuperUnsicheresPasswort@127.0.0.1:3306/spielwiese_philipp")
Base = declarative_base()
Base.metadata.reflect(engine)
db_session = scoped_session(sessionmaker(bind=engine))

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



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getDozenten')
def get_dozenten():
    return render_template('base.html')

@app.route('/getBestellung')
def get_bestellungen():
    for item in db_session.query(Bestellung.db_bestellung_id, Bestellung.db_kurs_id):
        result = item

    return render_template('get_bestellungen.html', bestellungen=result)

# def main():
#     from sqlalchemy.orm import scoped_session, sessionmaker
#     db_session = scoped_session(sessionmaker(bind=engine))

#     for item in db_session.query(Dozent.db_dozent_id, Dozent.db_username):
#         print(item)


#     for item in db_session.query(Schueler.db_schueler_id, Schueler.db_email):
#         print(item)


#     first_element = []

#     for bestellung in db_session.query(Bestellung.db_bestellung_id, Bestellung.db_schueler_id):
#         first_element.append(bestellung)
#     print(first_element[5])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)