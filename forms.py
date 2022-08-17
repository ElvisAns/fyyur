from datetime import datetime
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField,HiddenField
from wtforms.validators import *
from flask_wtf import FlaskForm #Any form that instanciate flask form will have form.csrf_token prop and will create the input for us whenever we place it in the form template
import re
import enum
state_choices=[
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

genres_choices=[
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip_Hop', 'Hip-Hop'),
    ('Heavy_Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical_Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R_B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock_n_Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

class Genres(enum.Enum):
    Alternative='Alternative'
    Blues='Blues'
    Classical='Classical'
    Country='Country'
    Electronic='Electronic'
    Folk='Folk'
    Funk='Funk'
    Hip_Hop='Hip-Hop'
    Heavy_Metal='Heavy Metal'
    Instrumental='Instrumental'
    Jazz='Jazz'
    Musical_Theatre='Musical Theatre'
    Pop='Pop'
    Punk='Punk'
    R_B='R&B'
    Reggae='Reggae'
    Rock_n_Roll='Rock n Roll'
    Soul='Soul'
    Other='Other'

class States(enum.Enum):
    AL='AL'
    AK='AK'
    AZ='AZ'
    AR='AR'
    CA='CA'
    CO='CO'
    CT='CT'
    DE='DE'
    DC='DC'
    FL='FL'
    GA='GA'
    HI='HI'
    ID='ID'
    IL='IL'
    IN='IN'
    IA='IA'
    KS='KS'
    KY='KY'
    LA='LA'
    ME='ME'
    MT='MT'
    NE='NE'
    NV='NV'
    NH='NH'
    NJ='NJ'
    NM='NM'
    NY='NY'
    NC='NC'
    ND='ND'
    OH='OH'
    OK='OK'
    OR='OR'
    MD='MD'
    MA='MA'
    MI='MI'
    MN='MN'
    MS='MS'
    MO='MO'
    PA='PA'
    RI='RI'
    SC='SC'
    SD='SD'
    TN='TN'
    TX='TX'
    UT='UT'
    VT='VT'
    VA='VA'
    WA='WA'
    WV='WV'
    WI='WI'
    WY='WY'

def validate_genres(form, prop):
    for genre in prop.data:
        try:
            value = Genres[genre] #Access the Genres enum as iterable by name, to access by value we may use Genres()
        except:
            raise ValidationError(
                f'{genre} is not an allowed genre'
            )

def validate_states(form, prop):
    state = prop.data #state single select, no need to loop
    print(state)
    try:
        value = States[state] #Access the States enum as iterable by name, to access by value we may use States()
    except:
        raise ValidationError(
            f'{state} is not an allowed genre'
        )

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()],
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )
    def validate_venue_id(form, field):
        if not re.search(r"^[0-9]+$", field.data): #starts with (^) any number between 0 and 9 [0-9] , repeated many time (+) and Ends like that ($) 
            raise ValidationError("Invalid venue id")
    def validate_artist_id(form, field):
        if not re.search(r"^[0-9]+$", field.data):
            raise ValidationError("Invalid artist id")

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),validate_states],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',validators=[DataRequired(),Length(9,13)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(),validate_genres],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),URL()]
    )
    website_link = StringField(
        'website_link', validators=[Optional(),URL()]
    )
    seeking_talent = BooleanField( 
        'seeking_talent', validators=[Optional()]
    )
    seeking_description = StringField(
        'seeking_description',validators=[Optional(),Length(5)]
    )
    
    def validate_phone(form,field):
        if not re.search(r"^\+[0-9]+$", field.data): #start with "+" and any number
            raise ValidationError("Telephone number incorrect")



class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),validate_states],
        choices=state_choices
    )
    phone = StringField(
        # TODO implement validation logic for phone 
        'phone',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link',
        validators=[DataRequired(),URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),validate_genres],
        choices=genres_choices
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[Optional(),URL()]
     )
    website_link = StringField(
        'website_link',
        validators=[Optional(),URL()]
     )
    seeking_venue = BooleanField( 'seeking_venue',validators=[Optional()])
    seeking_description = StringField(
            'seeking_description',
            validators=[Optional(),Length(5)]
     )
    def validate_phone(form,field):
        if not re.search(r"^\+[0-9]+$", field.data): #start with "+" and any number
            raise ValidationError("Telephone number incorrect")

class ShowForm_Quick(FlaskForm):
    venue_id = HiddenField(
        'venue_id',
        validators=[DataRequired()]
    )
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        choices=[]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )