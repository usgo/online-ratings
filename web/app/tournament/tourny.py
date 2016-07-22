
import datetime
from flask import current_app, render_template, redirect, url_for
from flask import jsonify, request, Response
from . import tournament
from app.forms import TournamentForm
from app.models import db, Tournament


@tournament.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('tournament_index.html',
                    tournaments=tournaments,)

@tournament.route('/new', methods=['GET', 'POST'])
def new_tournament():
    form = TournamentForm()
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
    return render_template('tournament_form.html', form=form)

@tournament.route('/<int:tournament_id>/edit', methods=['GET', 'POST'])
def edit_tournament(tournament_id):
    t = Tournament.query.get(tournament_id)
    form = TournamentForm(obj=t)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(t)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('tournament_form.html', form=form)

@tournament.route('/<int:tournament_id>', methods=['GET'])
def show(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    return render_template('tournament_show.html',
                            tournament=tournament)

@tournament.route('/<int:tournament_id>/delete', methods=['POST'])

def delete(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for('.index'))
