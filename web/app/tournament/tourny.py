
import datetime
from flask import current_app, render_template, redirect, url_for
from flask import jsonify, request, Response
from . import tournament
from app.forms import AddTournamentForm
from app.models import db, Tournament


@tournament.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('tournament_index.html',
                    tournaments=tournaments,)

@tournament.route('/new', methods=['GET', 'POST'])
def new_tournament():
    form = AddTournamentForm()
    if form.validate_on_submit():
        t = Tournament(event_name=form.event_name.data,
                       start_date=datetime.datetime.now(),
                       venue=form.venue.data,
                       director=form.director.data,
                       pairing=form.pairing.data,
                       rule_set=form.rule_set.data)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('tournament_new.html', form=form)
