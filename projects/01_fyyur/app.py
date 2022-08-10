#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import datetime
import json
import dateutil.parser
from pprint import pprint
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)
  artist = db.relationship('Artist',back_populates='venues')
  venue = db.relationship('Venue',back_populates='artists')


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link =db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String)
    artists = db.relationship('Show',back_populates='venue')

    def __repr__(self):
      return f'<Venue : {self.name},{self.city}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String)

    venues = db.relationship('Show',back_populates='artist')


# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

"""
## To get show

venue1 = Venue.query.get(1) #parent

artist1 = Artist.query.get(2) #child


dt = datetime.now()
dateNow = dt.strftime("%d/%m/%Y %H:%M:%S")


show1 = Show(start_time=dateNow)

show1.artist = artist1
show1.venue = venue1

db.session.add(show1)
"""

"""
## To insert venue and artist
venue1 = Venue(name="Sanaa Weekend",city="San Francisco",state="CA",address="Congolo",phone="+243971774989")

artist1 = Artist(name="John Santos",city="Bukavu",state="Nord kivu",phone="+2439981333",genres= json.dumps(["Pop","RNB"]))

db.session.add_all([venue1,artist1])
"""


#show1 = Show.query.all()
#venue1 = Venue.query.get(1) 


try:
  db.session.commit()
except Exception as e:
  print(e)
  print("There was an error executing your command")
  db.session.rollback()



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  dateutil
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  city_venues = db.session.query(Venue.city,Venue.state,func.count(Venue.id)).group_by('city','state').all()
  data = []
  for places in city_venues:
    new_city = {}
    new_city['city']=places[0]
    new_city['state']=places[1]
    new_city['venues']=[]
    this_city_venues = Venue.query.filter(Venue.city==new_city['city']).all()

    for venue in this_city_venues:
        new_venue = {}
        new_venue['id'] = venue.id
        new_venue['name'] = venue.name
        new_venue["num_upcoming_shows"]=len(venue.artists)
        new_city['venues'].append(new_venue)
    data.append(new_city)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get("search_term")
  result = Venue.query.filter(Venue.name.ilike(f'%{search}%') | Venue.name.ilike(f'{search}%')| Venue.name.ilike(f'%{search}')).all()

  response={
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data={}
  venue=Venue.query.get(venue_id)
  data['name']=venue.name
  data['id']=venue.id
  try:
    data["genres"]=json.loads(venue.genres)
  except: 
    data["genres"]=[venue.genres]
    print("Genre error")
  data["address"]=venue.address
  data["city"]=venue.city
  data["state"]=venue.state
  data["phone"]=venue.phone
  data["website"]=venue.website_link
  data["facebook_link"]=venue.facebook_link
  data["seeking_talent"]=venue.seeking_talent
  data["seeking_descritpion"]=venue.seeking_description
  data["image_link"]=venue.image_link
    
  shows=Show.query.filter_by(venue_id=venue_id).all()
  data["past_shows"]=[]
  data["upcoming_shows"]=[]

  dt = datetime.now()
  dateNow = dt.strftime("%d/%m/%Y %H:%M:%S")
  comp_now = datetime.strptime(dateNow, "%d/%m/%Y %H:%M:%S")

  for show in shows:
    toPush={}
    artistForThisShow = Artist.query.get(show.artist_id)
    comp_show_time = datetime.strptime(str(show.start_time), "%Y-%m-%d %H:%M:%S")

    toPush["artist_id"] = artistForThisShow.id
    toPush["artist_name"] = artistForThisShow.name
    toPush["artist_image_link"] = artistForThisShow.image_link
    toPush["start_time"] = str(show.start_time)

    if(comp_now>comp_show_time): #old show
      data["past_shows"].append(toPush)
    else:
      data["upcoming_shows"].append(toPush)
  
  data["past_shows_count"]=len(data["past_shows"])
  data["upcoming_shows_count"]=len(data["upcoming_shows"])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  datas = request.form
  venue = Venue(
    name=datas['name'],
    city=datas['city'],
    state=datas['state'],
    address=datas['address'],
    phone=datas['phone'],
    genres=json.dumps(datas['genres']),
    facebook_link=datas['facebook_link'],
    image_link = datas['image_link'],
    website_link= datas['website_link'],
    seeking_talent=True if (datas['seeking_talent']=='y') else False,
    seeking_description=datas['seeking_description']
  )

  db.session.add(venue)

  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + datas['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/delete/<venue_id>', methods=['GET'])
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  show = Show.query.filter_by(venue_id=venue_id).first()
  db.session.delete(show)
  db.session.delete(venue)

  try:
    db.session.commit()
    flash('The Venue '+ venue_id+' was successfully deleted!')
  except Exception as e:
    print(e)
    flash('An error occurred, Venue '+venue_id+' could not be deleted!')
  finally:
    db.session.close()
  
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get("search_term")
  result = Artist.query.filter(Artist.name.ilike(f'%{search}%') | Artist.name.ilike(f'{search}%')| Artist.name.ilike(f'%{search}')).all()

  response={
    "count": len(result),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data={}
  artist=Artist.query.get(artist_id)
  data['name']=artist.name
  data['id']=artist.id
  try:
    data["genres"]=json.loads(artist.genres)
  except: 
    data["genres"]=[artist.genres]
    print("Genre error")
  data["city"]=artist.city
  data["state"]=artist.state
  data["phone"]=artist.phone
  data["website"]=artist.website_link
  data["facebook_link"]=artist.facebook_link
  data["image_link"]=artist.image_link
  data['seeking_venue']=artist.seeking_venue
  data['seeking_description']=artist.seeking_description
    
  shows=Show.query.filter_by(artist_id=artist_id).all()
  data["past_shows"]=[]
  data["upcoming_shows"]=[]

  dt = datetime.now()
  dateNow = dt.strftime("%d/%m/%Y %H:%M:%S")
  comp_now = datetime.strptime(dateNow, "%d/%m/%Y %H:%M:%S")

  for show in shows:
    toPush={}
    venueForThisShow = Venue.query.get(show.venue_id)
    comp_show_time = datetime.strptime(str(show.start_time), "%Y-%m-%d %H:%M:%S")

    toPush["venue_id"] = venueForThisShow.id
    toPush["venue_name"] = venueForThisShow.name
    toPush["venue_image_link"] = venueForThisShow.image_link
    toPush["start_time"] = str(show.start_time)

    if(comp_now>comp_show_time): #old show
      data["past_shows"].append(toPush)
    else:
      data["upcoming_shows"].append(toPush)
  
  data["past_shows_count"]=len(data["past_shows"])
  data["upcoming_shows_count"]=len(data["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  try:
    g=json.loads(artist.genres)
  except: 
    g=[artist.genres]
    print("Genre error")

  forms = ArtistForm(
    id=artist.id,
    name = artist.name,
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    genres=g,
    website=artist.website_link,
    facebook_link=artist.facebook_link,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description,
    image_link=artist.image_link
  )
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=forms, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  data = request.form
  print(data)
  artist.name = data["name"]
  artist.genres = json.dumps([data["genres"]])
  artist.city=data["city"]
  artist.state=data["state"]
  artist.phone=data["phone"]
  artist.website=data["website_link"]
  artist.facebook_link=data["facebook_link"]
  try:
    artist.seeking_venue=True if data["seeking_venue"]=='y' else False
  except:
    print(data)
    print("No value supplied for seeking_venue")

  artist.seeking_description=data["seeking_description"]
  artist.image_link=data["image_link"]
  db.session.add(artist)
  try:
    db.session.commit()
    flash("The Artist " + artist.name + "'s informations has been successfully edited")
  except Exception as e:
    print(e)
    db.session.rollback()
    flash("Something went wrong while trying to edit the artist "+ artist.name +"'s informations")
  finally:
    db.session.close()
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    g=json.loads(venue.genres)
  except: 
    g=[venue.genres]
    print("Genre error")
    
  form = VenueForm(
    id=venue.id,
    name=venue.name,
    genres=g,
    address=venue.address,
    city=venue.city,
    state=venue.state,
    phone=venue.phone,
    website=venue.website_link,
    facebook_link=venue.facebook_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description,
    image_link = venue.image_link
  )
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  datas=request.form
  venue.name=datas["name"]
  venue.genres=json.dumps([datas["genres"]])
  venue.address=datas["address"]
  venue.city=datas["city"]
  venue.state=datas["state"]
  venue.phone=datas["phone"]
  venue.website_link=datas["website_link"]
  venue.facebook_link=datas["facebook_link"]
  venue.seeking_talent=True if datas["seeking_talent"]=='y' else False
  venue.seeking_description=datas["seeking_description"]
  venue.image_link=datas["image_link"]

  db.session.add(venue)
  try:
    db.session.commit()
    flash("The venue "+ str(venue_id) + " has been successfully updated")
  except Exception as e:
    print(e)
    db.session.rollback()
    flash("An error occured, the venue "+ venue_id + " was not updated")
  finally:
    db.session.close()
  
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  datas = request.form
  artist = Artist(
    name=datas['name'],
    city=datas['city'],
    state=datas['state'],
    phone=datas['phone'],
    genres=json.dumps([datas['genres']]),
    facebook_link=datas['facebook_link'],
    image_link = datas['image_link'],
    website_link= datas['website_link'],
    seeking_venue=True if (datas['seeking_venue']=='y') else False,
    seeking_description=datas['seeking_description']
  )
  db.session.add(artist)

  try:
    db.session.commit()
    flash('The artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + datas['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    i = {}
    artist = Artist.query.get(show.artist_id)
    print(show.start_time)
    venue = Venue.query.get(show.venue_id)
    i["venue_id"] = show.venue_id
    i["venue_name"] = venue.name
    i['artist_id'] = show.artist_id
    i['artist_name'] = artist.name
    i['artist_image_link'] = artist.image_link
    i['start_time'] = str(show.start_time)
    data.append(i)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  datas =  request.form
  print(datas)
  venue1 = Venue.query.get(datas["venue_id"]) #parent
  if not venue1:
    flash("The venue ID could not be found")
    return redirect(url_for('index'))

  artist1 = Artist.query.get(datas["artist_id"]) #child
  if not artist1:
    flash("The artist ID could not be found")
    return redirect(url_for('index'))

  show1 = Show(start_time=datas['start_time'])
  show1.artist = artist1
  show1.venue = venue1

  db.session.add(show1)

  try:
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash("Un error occured while listing the show")
  finally:
    db.session.close()

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
