from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import Required, URL, Optional
from wtforms.fields.html5 import DateField
from .models import KOMI_VALUES as kv
from .models import TIE_BREAKS as tb
from .models import MATCH_RESULTS as mr


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

    venue = StringField("Venue (Optional)")
    venue_address = StringField("Venue Address (Optional)")
    venue_state = StringField("State (Optional)")
    venue_zip = StringField("Zip (Optional)")

    start_date = DateField('Start Date', format='%Y-%m-%d',
                            validators=[Required()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])

    director = StringField("Director", validators=[Required()])
    director_phone = StringField("Director's Phone (Optional)")
    director_address = StringField("Director's Address (Optional)")
    director_email = StringField("Director's Email", validators=[Required()])

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

    pairing = SelectField("Pairing", choices=[("McMahon","McMahon"),],
                           validators=[Required()])
    rule_set = SelectField("Rule set", choices=[("AGA", 'AGA'),
                ('INTERNATIONAL', 'INTERNATIONAL')], validators=[Required()])
    time_controls = StringField("Time Controls", validators=[Required()])
    basic_time = StringField("Basic Time", validators=[Required()])
    overtime_format = StringField("Overtime Format", validators=[Required()])
    overtime_conditions = StringField("Overtime Conditions",
                                      validators=[Required()])
    komi = SelectField("Komi", choices=[(x, x) for x in kv],
                        validators=[Required()])
    tie_break1 = SelectField("Tie Break Tier 1", choices=[(x, x) for x in tb],
                             validators=[Required()])
    tie_break2 = SelectField("Tie Break Tier 2", choices=[(x, x) for x in tb],
                             validators=[Required()])

    submitted = BooleanField("Submitted")
    submit = SubmitField()

class TournamentPlayerForm(Form):
    name = StringField("Player's Name", validators=[Required()])
    aga_num = StringField("AGA Number", validators=[Required()])
    rating = StringField("Rating", validators=[Required()])
    affiliation = StringField("Club Affiliation", validators=[Required()])
    state = StringField("State", validators=[Required()])
    address = StringField("Address", validators=[Required()])
    email = StringField("Email", validators=[Required()])
    phone = StringField("Phone", validators=[Required()])
    citizenship = StringField("Citizenship", validators=[Required()])
    dob = StringField("Date of Birth", validators=[Required()])

    submit = SubmitField()

class MatchResultsForm(Form):
    player_1_name = StringField("Black's Name")
    player_2_name= StringField("White's Name")
    result = SelectField("Match Result", choices=[(x, x) for x in mr],
                           validators=[Required()])
    submit = SubmitField()
