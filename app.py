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
from models.model import db,Show,Artist,Venue
from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(date, format='medium'):
  dateutil
  value = str(date) #explitly convert the upcoming data to string
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
  artists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
  venues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
  return render_template('pages/home.html',artists=artists,venues=venues)

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
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
        new_venue['image_link'] = venue.image_link
        new_venue["num_upcoming_shows"]=len(venue.artists)
        new_city['venues'].append(new_venue)
    data.append(new_city)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get("search_term")
  option_for_search = request.form.get("option_for_search")
  if search is not None:
    if option_for_search == "name":
      result = Venue.query.filter(Venue.name.ilike(f'%{search}%') | Venue.name.ilike(f'{search}%')| Venue.name.ilike(f'%{search}')).all()
    elif option_for_search == "city":
      result = Venue.query.filter(Venue.city.ilike(f'%{search}%') | Venue.city.ilike(f'{search}%')| Venue.city.ilike(f'%{search}')).all()
    else:
      result = Venue.query.filter(Venue.state.ilike(f'%{search}%') | Venue.state.ilike(f'{search}%')| Venue.state.ilike(f'%{search}')).all()
  else:
    result = Venue.query.all()

  response={
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
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
  data["seeking_description"]=venue.seeking_description
  data["image_link"]=venue.image_link
  
  data["past_shows"] = db.session.query(
    Show,
    Artist.name.label("artist_name"),
    Artist.id.label("artist_id"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time
  ).join(Venue).join(Artist).filter(
    Venue.id==venue_id,
    Show.artist_id==Artist.id,
    Show.start_time<datetime.now()
  ).all()

  data["upcoming_shows"] = db.session.query(
    Show,
    Artist.name.label("artist_name"),
    Artist.id.label("artist_id"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time
  ).join(Venue).join(Artist).filter(
    Venue.id==venue_id,
    Show.artist_id==Artist.id,
    Show.start_time>=datetime.now()
  ).all()

  data["past_shows_count"]=len(data["past_shows"])
  data["upcoming_shows_count"]=len(data["upcoming_shows"])

  artists = Artist.query.all()
  form = ShowForm_Quick(venue_id=venue_id)
  form.artist_id.choices = [(artist.id, artist.name) for artist in artists]
  return render_template('pages/show_venue.html',form = form,artists=artists,venue_id=venue_id,venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  datas = request.form
  form = VenueForm(datas)
  if form.validate(): #form validated
    try:
      y=True if (datas['seeking_talent']=='y') else False
    except:
      y=False
    venue = Venue(
      name=datas['name'],
      city=datas['city'],
      state=datas['state'],
      address=datas['address'],
      phone=datas['phone'],
      genres=json.dumps(form.genres.data),
      facebook_link=datas['facebook_link'],
      image_link = datas['image_link'],
      website_link= datas['website_link'],
      seeking_talent=y,
      seeking_description=datas['seeking_description']
    )

    db.session.add(venue)

    try:
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + datas['name'] + ' could not be listed.','alert-danger')
    finally:
      db.session.close()
  else:
    flash("Your form contains error and the venue was not listed",'alert-danger') #flash message as danger alert
    return render_template('forms/new_venue.html', form=form)

  return redirect(url_for('index'))

@app.route('/venues/delete/<venue_id>', methods=['GET'])
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  show = Show.query.filter_by(venue_id=venue_id).first()
  if(show): venue.artists.remove(show)
  db.session.delete(venue)

  try:
    db.session.commit()
    flash('The Venue '+ venue_id+' was successfully deleted!')
  except Exception as e:
    print(e)
    flash('An error occurred, Venue '+venue_id+' could not be deleted!','alert-danger')
  finally:
    db.session.close()
  
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get("search_term")
  option_for_search = request.form.get("option_for_search")
  if search is not None:
    if option_for_search == "name":
      result = Artist.query.filter(Artist.name.ilike(f'%{search}%') | Artist.name.ilike(f'{search}%')| Artist.name.ilike(f'%{search}')).all()
    elif option_for_search == "city" :
      result = Artist.query.filter(Artist.city.ilike(f'%{search}%') | Artist.city.ilike(f'{search}%')| Artist.city.ilike(f'%{search}')).all()
    else:
      result = Artist.query.filter(Artist.state.ilike(f'%{search}%') | Artist.state.ilike(f'{search}%')| Artist.state.ilike(f'%{search}')).all()
  else:
    result = Artist.query.all()

  response={
    "count": len(result),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
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

  data["past_shows"] = db.session.query(
    Show,
    Venue.name.label("venue_name"),
    Venue.id.label("venue_id"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time
  ).join(Venue).join(Artist).filter(
    Venue.id==Show.venue_id,
    Show.artist_id==artist_id,
    Show.start_time<datetime.now()
  ).all()

  data["upcoming_shows"] = db.session.query(
    Show,
    Venue.name.label("venue_name"),
    Venue.id.label("venue_id"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time
  ).join(Venue).join(Artist).filter(
    Venue.id==Show.venue_id,
    Show.artist_id==artist_id,
    Show.start_time>=datetime.now()
  ).all()
  
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
  return render_template('forms/edit_artist.html', form=forms, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  data = request.form
  forms = ArtistForm(data)
  if(forms.validate()):
    try:
      sv = True if data["seeking_venue"]=='y' else False
    except:
      sv = False
    artist.name = data["name"]
    artist.genres = json.dumps(forms.genres.data) # as the genres is werkzeug MultiDict, better pick datas from the processed form data
    artist.city=data["city"]
    artist.state=data["state"]
    artist.phone=data["phone"]
    artist.website=data["website_link"]
    artist.facebook_link=data["facebook_link"]
    artist.seeking_venue=sv
    artist.seeking_description=data["seeking_description"]
    artist.image_link=data["image_link"]
    db.session.add(artist)
    try:
      db.session.commit()
      flash("The Artist " + artist.name + "'s informations has been successfully edited")
    except Exception as e:
      print(e)
      db.session.rollback()
      flash("Something went wrong while trying to edit the artist "+ artist.name +"'s informations",'alert-danger')
    finally:
      db.session.close()
  else:
    flash("Your form contains errors and the artist could not be updated","alert-danger")
    return render_template('forms/edit_artist.html', form=forms, artist=artist)
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

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  datas = request.form
  forms = VenueForm(datas)
  if(forms.validate()):
    try:
      st = True if datas["seeking_talent"]=='y' else False
    except:
      st = False
    venue.name=datas["name"]
    venue.genres=json.dumps(forms.genres.data)
    venue.address=datas["address"]
    venue.city=datas["city"]
    venue.state=datas["state"]
    venue.phone=datas["phone"]
    venue.website_link=datas["website_link"]
    venue.facebook_link=datas["facebook_link"]
    venue.seeking_talent=st
    venue.seeking_description=datas["seeking_description"]
    venue.image_link=datas["image_link"]

    db.session.add(venue)
    try:
      db.session.commit()
      flash("The venue "+ str(venue_id) + " has been successfully updated")
    except Exception as e:
      print(e)
      db.session.rollback()
      flash("An error occured, the venue "+ venue_id + " was not updated",'alert-danger')
    finally:
      db.session.close()
  else:
    flash("Your form contains errors and the venue could not be updated","alert-danger")
    return render_template('forms/edit_venue.html', form=forms, venue=venue)

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
  forms = ArtistForm(datas)
  if(forms.validate()):
    try:
      sv = True if (datas['seeking_venue']=='y') else False
    except:
      sv = False
    artist = Artist(
      name=datas['name'],
      city=datas['city'],
      state=datas['state'],
      phone=datas['phone'],
      genres=json.dumps(forms.genres.data),
      facebook_link=datas['facebook_link'],
      image_link = datas['image_link'],
      website_link= datas['website_link'],
      seeking_venue= sv,
      seeking_description=datas['seeking_description']
    )
    db.session.add(artist)

    try:
      db.session.commit()
      flash('The artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist ' + datas['name'] + ' could not be listed.','alert-danger')
    finally:
      db.session.close()
  else:
    flash("Your form contains errors and the artist could not be listed","alert-danger")
    return render_template('forms/new_artist.html', form=forms)

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
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
  forms  = ShowForm(datas)
  if(forms.validate()):
    venue1 = Venue.query.get(datas["venue_id"]) #parent
    if not venue1:
      flash("The venue ID could not be found",'alert-danger')
      return redirect(url_for('index'))

    artist1 = Artist.query.get(datas["artist_id"]) #child
    if not artist1:
      flash("The artist ID could not be found",'alert-danger')
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
      flash("Un error occured while listing the show",'alert-danger')
    finally:
      db.session.close()
  else:
    flash("Your form contains errors and the show could not be listed","alert-danger")
    return render_template('forms/new_show.html', form=forms)

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
