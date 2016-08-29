
import datetime
from flask import current_app, render_template, redirect, url_for
from flask import jsonify, request, Response
from . import tournament
from app.forms import TournamentForm, TournamentPlayerForm
from app.models import db, Tournament, TournamentPlayer
from sqlalchemy import update

@tournament.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('tournament_index.html',
                    tournaments=tournaments,)

@tournament.route('/<int:tournament_id>', methods=['GET'])
def show(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    return render_template('tournament_show.html',
    tournament=tournament)

@tournament.route('/new', methods=['GET', 'POST'])
def new_tournament():
    form = TournamentForm()
    if form.validate_on_submit():
        t = Tournament(event_name=form.event_name.data,
                       venue=form.venue.data,
                       venue_address=form.venue_address.data,
                       venue_state=form.venue_state.data,
                       venue_zip=form.venue_zip.data,
                       start_date=form.start_date.data,
                       end_date=form.end_date.data,
                       director=form.director.data,
                       director_phone=form.director_phone.data,
                       director_email=form.director_email.data,
                       director_address=form.director_address.data,
                       sponsor=form.sponsor.data,
                       sponsor_phone=form.sponsor_phone.data,
                       sponsor_email=form.sponsor_email.data,
                       sponsor_website=form.sponsor_website.data,
                       sponsor_address=form.sponsor_address.data,
                       convener=form.convener.data,
                       convener_phone=form.convener_phone.data,
                       convener_email=form.convener_email.data,
                       convener_website=form.convener_website.data,
                       convener_address=form.convener_address.data,
                       pairing=form.pairing.data,
                       rule_set=form.rule_set.data,
                       time_controls=form.time_controls.data,
                       basic_time=form.basic_time.data,
                       overtime_format=form.overtime_format.data,
                       overtime_conditions=form.overtime_conditions.data,
                       komi=form.komi.data,
                       tie_break1=form.tie_break1.data,
                       tie_break2=form.tie_break2.data,
                       submitted=form.submitted.data)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('tournament_form.html', form=form)


@tournament.route('/<int:tournament_id>/edit', methods=['GET', 'POST'])
def edit_tournament(tournament_id):
    t = Tournament.query.get(tournament_id)
    form = TournamentForm(obj=t)
    if request.method == 'POST' and form.validate_on_submit():
        if t.submitted == False:
            form.populate_obj(t)
            db.session.commit()
            return redirect(url_for('.index'))
        elif t.submitted == True:
            # flash("Sorry, this tournament has already been submitted and can no \
            #       longer be edited.")
            return redirect(url_for('.index'))
    return render_template('tournament_form.html', form=form)

@tournament.route('/<int:tournament_id>/delete', methods=['POST'])
def delete(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if tournament.submitted == False:
        db.session.delete(tournament)
        db.session.commit()
        return redirect(url_for('.index'))
    # flash("Sorry, this tournament has already been submitted and can no \
    #       longer be edited.")
    return redirect(url_for('.index'))

@tournament.route('/<int:tournament_id>/player/new', methods=["GET", "POST"]) #  maybe a vanity url
def new_player(tournament_id):
    form = TournamentPlayerForm()
    if form.validate_on_submit():
        #  if before first_round  - a cutoff for adding new players
        tp = TournamentPlayer(tournament_id = tournament_id,
                             name = form.name.data,
                             player_id = form.player_id.data,
                             rating = form.rating.data,
                             affiliation = form.affiliation.data,
                             state = form.state.data,
                             address = form.address.data,
                             email = form.email.data,
                             phone = form.phone.data,
                             citizenship = form.citizenship.data,
                             dob = form.dob.data)

        db.session.add(tp)
        db.session.commit()
        tourn = Tournament.query.get(tp.tournament_id)
        player = TournamentPlayer.query.all()[-1] # player doesn't have tp id until session.commit()
        tourn.participants.append(player.id)
        db.session.add(tourn)
        db.session.commit()
        return redirect(url_for('.new_player', tournament_id=tournament_id))
    return render_template('tournament_player_form.html', form=form)

@tournament.route('/<int:tournament_id>/players', methods=["GET"])
def players_index(tournament_id):
    players = TournamentPlayer.query.all()
    return render_template("tournament_players_index.html", players=players)
