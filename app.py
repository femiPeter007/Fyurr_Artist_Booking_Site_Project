#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys
from model import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  venues = Venue.query.all()
  data = []
  location_data = {}
  for venue in venues:
    if venue.city not in location_data.keys():
      location_data[venue.city]={
        "city": venue.city,
        "state": venue.state,
        "venues": [venue]
      }
    else:
      location_data[venue.city]['venues'].append(venue)
  for city_venue in location_data.values():
    data.append(city_venue)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term')
  search = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  
  for venue in search:
     response = {
    'count': len(search),
    'data': [{
    'id': venue.id,
    'name': venue.name,
    'num_upcoming_shows': 0
    }]
  }
  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  data = Venue.query.get(venue_id)

  
  data = Venue.query.get(venue_id)
  data.upcoming_shows=[]
  data.past_shows=[]
  data.past_shows_count=0
  data.upcoming_shows_count=0


  upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()
  past_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()

  for show in upcoming_shows:
    item = {
      "venue_id": show.venue_data.id,
      "venue_name": show.venue_data.name,
      "venue_image_link": show.venue_data.image_link,
      "start_time": show.start_time
    }
    data.upcoming_shows.append(item)
  data.upcoming_shows_count=len(upcoming_shows)

  for show in past_shows:
    item = {
      "venue_id": show.venue_data.id,
      "venue_name": show.venue_data.name,
      "venue_image_link": show.venue_data.image_link,
      "start_time": show.start_time
    }
    data.past_shows.append(item)
  data.past_shows_count=len(past_shows)
    
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  try:
    if form.validate_on_submit():
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
    db.session.add(venue)
    db.session.commit()
    
    flash('GET IN!', " " + request.form['name'] + " ", 'has been uploaded!')

  except:
    flash('Uh-oh!', " " + request.form['name'] + " ", 'was not uploaded!')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term')
  search = Artist.query.filter(Artist.name.like('%' + search_term + '%')).all()

  for artist in search:
    response = {
      'count': len(search),
      'data': [{
        'id': artist.id,
        'name': artist.name,
        'num__upcoming_shows': 0
      }] 
    }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 

  data = Artist.query.get(artist_id)
  data.upcoming_shows=[]
  data.past_shows=[]
  data.past_shows_count=0
  data.upcoming_shows_count=0


  upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()
  past_shows = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()

  for show in upcoming_shows:
    item = {
      "venue_id": show.venue_data.id,
      "venue_name": show.venue_data.name,
      "venue_image_link": show.venue_data.image_link,
      "start_time": show.start_time
    }
    data.upcoming_shows.append(item)
  data.upcoming_shows_count=len(upcoming_shows)

  for show in past_shows:
    item = {
      "venue_id": show.venue_data.id,
      "venue_name": show.venue_data.name,
      "venue_image_link": show.venue_data.image_link,
      "start_time": show.start_time
    }
    data.past_shows.append(item)
  data.past_shows_count=len(past_shows)
    

  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

  
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('You have edited this artist')
  except:
    flash('You did not edit anything')
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  

  venue = Venue.query.get(venue_id)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('You have edited this venue')
  except:
    flash('You did not edit anything')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  form = ArtistForm(request.form)
  try:
    if form.validate_on_submit():
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  except:
    db.session.rollback()
    flash('An error occured. Artist' + request.form['name'] + 'could not be listed!')
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows=Show.query.all()
  data = []
  for show in shows:
    show_data={
      "venue_id": show.venue_data.id,
      "venue_name": show.venue_data.name,
      "artist_id":show.artist_data.id,
      "artist_name":show.artist_data.name,
      "artist_image_link":show.artist_data.image_link,
      "start_time":show.start_time
    }
    data.append(show_data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():

  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  try:
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()

    flash('Your show has been added!')

  except:
    db.rollback()
    flash('An error eccoured. Show could not be listed')
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#


if __name__ == '__main__':
    app.run()


'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
