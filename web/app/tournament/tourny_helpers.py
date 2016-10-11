from flask import current_app, render_template, redirect, url_for
from flask import jsonify, request, Response, flash
from app.models import db, Tournament, TournamentPlayer, Match, Round

def empty_field(form_data, fetched_db_data):
    """Treating an empty string returned by form as equal to None in DB"""
    if (form_data == None and fetched_db_data == '') or (form_data == '' and fetched_db_data == None):
        return True
    else:
        return False


def match_edit(form, match, tournament_id):
    """Edit logic for match function on match edit route"""
    if form.validate_on_submit():
        if (form.player_1_name.data == match.player_1_name or empty_field(
            form.player_1_name.data, match.player_1_name)) and (
            form.player_2_name.data == match.player_2_name or empty_field(
            form.player_2_name.data, match.player_2_name)):

            form.populate_obj(match)
            db.session.commit()
            return redirect(url_for('.matches_by_round_index',
                tournament_id=tournament_id,
                round_id=match.t_round))
        else:
            if form.player_1_name.data != match.player_1_name:
                if form.player_1_name.data == "":
                    match.player_1_name = None
                    match.player_1_id = None
                    match.result = form.result.data
                    match.result_notation = form.result_notation.data
                    db.session.commit()
                    # flash("Player removed from match")
                else:
                    tp1 = TournamentPlayer.query.filter_by(
                        tournament_id=match.tournament_id,
                        name=form.player_1_name.data).first()
                    if tp1:
                        match.player_1_name = tp1.name
                        match.player_1_id = tp1.id
                        match.result = form.result.data
                        match.result_notation = form.result_notation.data
                        db.session.commit()
                        #  flash('Match Modified')
                    else:
                        #flash("Player not entered in tournament")
                        return redirect(url_for('.matches_by_round_index',
                            tournament_id=tournament_id,
                            round_id=match.t_round))

            if form.player_2_name.data != match.player_2_name:
                if form.player_2_name.data != match.player_2_name:
                    if form.player_2_name.data == "":
                        match.player_2_name = None
                        match.player_2_id = None
                        match.result = form.result.data
                        match.result_notation = form.result_notation.data
                        db.session.commit()
                        # flash("Player removed from match")
                    else:
                        tp2 = TournamentPlayer.query.filter_by(
                            tournament_id=match.tournament_id,
                            name=form.player_2_name.data).first()
                        if tp2:
                            match.player_2_name = tp2.name
                            match.player_2_id = tp2.id
                            match.result = form.result.data
                            match.result_notation = form.result_notation.data
                            db.session.commit()
                        else:
                            # flash("Player not entered in tournament")
                            return redirect(url_for('.matches_by_round_index',
                                tournament_id=tournament_id,
                                round_id=match.t_round))

        return redirect(url_for('.matches_by_round_index',
            tournament_id=tournament_id,
            round_id=match.t_round))
