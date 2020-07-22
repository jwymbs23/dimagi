from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from whereis_app.auth import login_required
from whereis_app.db import get_db

from whereis_app.geolocator import Geo




bp = Blueprint('locations', __name__)


def get_location(id, check_user=True):
    location = get_db().execute(
        'SELECT l.location_id, location, lat, lon, person_id, created, person_name'
        ' FROM location l JOIN user u ON l.person_id = u.id'
        ' WHERE l.location_id = ?',
        (id,)
    ).fetchone()

    if location is None:
        abort(404, "Location id {0} doesn't exist.".format(id))

    if check_user and location['person_id'] != g.user['id']:
        abort(403)

    return location

    

def push_location(city, country, user_id, off_the_grid, user_id_type='id'):

    G = Geo(city, country, user_id)

    location = G.geolocate()

    try:
        db = get_db()
        db.execute(
            'INSERT INTO location (location, lat, lon, person_id, off_the_grid)'
            ' VALUES (?, ?, ?, ?, ?)',
            (f'{location["city"]}, {location["country"]}',
             location['lat'],
             location['lng'],
             g.user['id'],
             off_the_grid)
            )
        db.commit()
        return 1
    except:
        return 0
    

def update_location(city, country, user_id, location_id, off_the_grid=0, user_id_type='id'):
    G = Geo(city, country, user_id, edit=True)

    location = G.geolocate()

    db = get_db()
    db.execute(
        'UPDATE location SET location = ?, lat = ?, lon = ? '
        ' WHERE location_id = ?',
        (f'{location["city"]}, {location["country"]}', location['lat'], location['lng'], location_id)
        )
    db.commit()



@bp.route('/')
def index():
    db = get_db()

    if g.user and g.user['person_name'] == 'admin':
        locations = db.execute(
        'SELECT l.location_id, location, lat, lon, person_id, created, person_name'
        ' FROM location l JOIN user u ON l.person_id = u.id '
        ).fetchall()
    else:
        locations = db.execute(
            ' SELECT l.location_id, location, lat, lon, person_id, created, person_name'
            ' FROM location l JOIN user u ON l.person_id = u.id '
            ' WHERE '
            'l.off_the_grid == 0 '
            ' AND '
            '(person_id, created) in (SELECT person_id, max(created)'
            'FROM location GROUP BY person_id)'
            ).fetchall()
    return render_template('locations/index.html', locations=locations)


@bp.route('/add_location', methods=('GET', 'POST'))
@login_required
def add_location():
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']
        if country == 'Country':
            country = ''

        off_the_grid = request.form['otg']
        error = None

        if not name:
            error = 'Name is required.'
            
        if not city:
            error = 'City is required.'
            
        if error is not None:
            flash(error)
        else:
            push_location(city, country, g.user['id'], off_the_grid)
            return redirect(url_for('locations.index'))

    return render_template('locations/create.html')


@bp.route('/<int:location_id>/update', methods=('GET', 'POST'))
@login_required
def update(location_id):
    location = get_location(location_id)

    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']
        if country == 'Country':
            country = ''
        error = None

        if not name:
            error = 'Name is required.'

        if not city:
            error = 'City is required.'

        if error is not None:
            flash(error)

        if error is not None:
            flash(error)
        else:
            update_location(city, country, g.user['id'], location_id)

            return redirect(url_for('locations.index'))

    return render_template('locations/update.html', location=location)



