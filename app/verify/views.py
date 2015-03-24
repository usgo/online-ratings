from . import verify

from flask import abort, redirect, url_for, render_template, flash
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask.ext.wtf import Form
from itsdangerous import BadSignature, URLSafeSerializer
from app.models import User
import app, logging

from wtforms import IntegerField, SubmitField
from wtforms.validators import Required


def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.app.secret_key #why app.app?
    return URLSafeSerializer(secret_key)

@verify.route('/verify/<payload>')
@login_required
def verify_player(payload):
    s = get_serializer()
    try:
        user_id, aga_id = s.loads(payload)
    except BadSignature:
        logging.info('Verify called with invalid paylod')
        abort(404)

    if user_id != current_user.id:
        logging.warn("Verify called for id %s, but wrong user answered, %s" % (user_id, current_user))
        abort(404)

    user = User.query.get_or_404(user_id)
    user.aga_id = aga_id
    app.db.session.add(user)
    app.db.session.commit()
    #TODO: something like user.activate(), maybe generate initial token?
    msg = 'Linked account with AGA #%s' %user.aga_id
    logging.info(msg)
    return redirect(url_for('ratings.viewprofile'))

def get_verify_link(user, aga_id):
    s = get_serializer()
    payload = s.dumps([user.id, aga_id])
    return url_for('.verify_player', payload=payload, 
                   _external=True)

@verify.route('/verify', methods=['GET', 'POST'])
@login_required
def verify_form():
    form = LinkUserWithAGANumberForm()
    if form.validate_on_submit():
        aga_id = form.aga_id.data
        link = get_verify_link(current_user, aga_id)
        return render_template('verify/testmsg.html', link=link)
    return render_template('verify/verifyform.html', form=form)

class LinkUserWithAGANumberForm(Form):
    aga_id = IntegerField('Aga number?',
                          validators=[Required()])
    submit = SubmitField()
