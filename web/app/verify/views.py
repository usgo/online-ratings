from . import verify
from .aga_membership import get_aga_info

from flask import abort, redirect, url_for, render_template, current_app
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask.ext.wtf import Form
from flask.ext.mail import Message
from itsdangerous import BadSignature, URLSafeSerializer
import app
from app.models import User, db
import logging

from wtforms import IntegerField, SubmitField
from wtforms.validators import Required


def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']
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
    db.session.add(user)
    db.session.commit()
    #TODO: something like user.activate(), maybe generate initial token?
    msg = 'Linked account with AGA #%s' %user.aga_id
    logging.info(msg)
    return redirect(url_for('ratings.profile'))

def get_verify_link(user, aga_id):
    s = get_serializer()
    payload = s.dumps([user.id, aga_id])
    return url_for('.verify_player', payload=payload, 
                   _external=True)

def send_verify_email(user, aga_id):
    aga_info = get_aga_info(aga_id)
    if aga_info is None:
        return False
    email_address = aga_info['email']
    email_subject = "Confirm AGA ID for Online Ratings"
    email_body = render_template('verify/verification_email.html', 
        user=user, aga_id=aga_id, verify_link=get_verify_link(user, aga_id))
    email = Message(
        recipients=[email_address],
        subject=email_subject,
        html=email_body,
    )
    app.mail.send(email)
    return True

@verify.route('/verify', methods=['GET', 'POST'])
@login_required
def verify_form():
    form = LinkUserWithAGANumberForm()
    if form.validate_on_submit():
        aga_id = form.aga_id.data
        success = send_verify_email(current_user, aga_id)
        if success:
            return render_template('verify/verify_form_post_submit.html')
        else:
            return render_template('verify/verify_form_post_submit_error.html', aga_id=aga_id)
    return render_template('verify/verifyform.html', form=form)

class LinkUserWithAGANumberForm(Form):
    aga_id = IntegerField('Aga number?',
                          validators=[Required()])
    submit = SubmitField()
