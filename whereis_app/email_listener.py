from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from whereis_app.auth import login_required
from whereis_app.db import get_db


from whereis_app.geolocator import Geo

bp = Blueprint('email_listener', __name__)


sample_data = [{'email': 'josephemail',
                'subject': 'London, England',
                }]

def get_user_id_from_email(email):

    ids = get_db().execute(
        'SELECT id FROM user '
        ' WHERE email = ? ',
        (email, )
        ).fetchone()
    if ids:
        return ids['id']
    else:
        return None


def email_push_location(city, country, user_id, off_the_grid=0, user_id_type='email'):

    if user_id_type == 'email':
        user_id = get_user_id_from_email(user_id)
    if not user_id:
        return 0, 'no user with that email'

    G = Geo(city, country, user_id)

    location = G.geolocate()
    
    #try:
    db = get_db()
    db.execute(
        'INSERT INTO location (location, lat, lon, person_id, off_the_grid)'
        ' VALUES (?, ?, ?, ?, ?)',
        (f'{location["city"]}, {location["country"]}',
         location['lat'],
         location['lng'],
         user_id,
         off_the_grid)
        )
    db.commit()
    return 1
    #except:
    #    return 0


def parse_subject(subj):

    if ',' in subj:
        return subj.split(',')
    else:
        return [subj, '']


def parse_email(data):

    city, country = parse_subject(data['subject'])

    return {'city': city,
            'country': country,
            'email': data['email']}


def main():
    
    # on new email:
    parsed_data = parse_email(sample_data[0])
    
    status = email_push_location(parsed_data['city'],
                                 parsed_data['country'],
                                 parsed_data['email'],
                                 user_id_type='email')
    print(status)

    
#if __name__ == "__main__":

