from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import Required, URL, Optional


class AddGameServerForm(Form):
    gs_name = StringField('Server Name?',
                          validators=[Required()])
    gs_url = StringField('Server URL?',
                         validators=[Required(), URL(message="Invalid URL")])
    submit = SubmitField()

class SearchPlayerForm(Form):
    player_name = StringField('Username', validators=[])
    aga_id = StringField('AGA id', validators=[Optional()])
    submit = SubmitField()

class TournamentForm(Form):
    event_name = StringField("Tournament Name", validators=[Required()])

    venue = StringField("Venue (Optional)") # Venue info Optional
    venue_address = StringField("Venue Address (Optional)")
    venue_state = StringField("State (Optional)")
    venue_zip = StringField("Zip (Optional)")

    start_date = StringField("Start Date", validators=[Required()]) # these will change to some date format
    end_date = StringField("End Date (Optional)")

    director = StringField("Director", validators=[Required()])
    director_phone = StringField("Director's Phone", validators=[Required()])
    director_email = StringField("Director's Email", validators=[Required()])
    director_address = StringField("Director's Address (Optional)")

    sponsor = StringField("Tournament Sponser (Optional)")
    sponsor_email = StringField("Sponsor's Email (Optional)")
    sponsor_phone = StringField("Sponsor's Phone (Optional)")
    sponsor_website  = StringField("Sponsor's Website (Optional)")
    sponsor_address = StringField("Sponsor's Address (Optional)")

    convener = StringField("Tournament Convener (Optional)")
    convener_email = StringField("Convener's Email (Optional)")
    convener_phone = StringField("Convener's Phone (Optional)")
    convener_website  = StringField("Convener's Website (Optional)")
    convener_address = StringField("Convener's Address (Optional)")

    pairing = StringField("Pairing", validators=[Required()])
    rule_set = StringField("Rule set", validators=[Required()])

    time_controls = StringField("Time Controls", validators=[Required()])
    basic_time = StringField("Basic Time", validators=[Required()])
    overtime_format = StringField("Overtime Format", validators=[Required()])
    overtime_conditions = StringField("Overtime Conditions", validators=[Required()])

    komi = StringField("Komi", validators=[Required()])

    tie_break = StringField("Tie Break(s)", validators=[Required()])

    submitted = BooleanField("Submitted")
    submit = SubmitField()

class TournamentPlayerForm(Form):
    name = StringField("Player's Name", validators=[Required()])
    player_id = StringField("Player ID", validators=[Required()])
    rating = StringField("Rating", validators=[Required()])
    affiliation = StringField("Club Affiliation", validators=[Required()])
    state = StringField("State", validators=[Required()])
    address = StringField("Address", validators=[Required()])
    email = StringField("Email", validators=[Required()])
    phone = StringField("Phone", validators=[Required()])
    citizenship = StringField("Citizenship", validators=[Required()])
    dob = StringField("Date of Birth", validators=[Required()])

    submit = SubmitField()
