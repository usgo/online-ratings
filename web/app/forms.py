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
    event_name = StringField("Tornament Name", validators=[Required()])
    # start_date = db.Column(db.DateTime)
    venue = StringField("Venue", validators=[Required()])
    director = StringField("Director", validators=[Required()])
    pairing = StringField("Pairing", validators=[Required()])
    rule_set = StringField("Rule set", validators=[Required()])
    submitted = BooleanField("Submitted")
    submit = SubmitField()
