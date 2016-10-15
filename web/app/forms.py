from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
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

class AddPlayerForm(Form):
    server = SelectField('Server', coerce=int, validators=[Required()])
    name = StringField('Name', validators=[Required()])
    submit = SubmitField()
