from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'cohort_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    invest_in_healthcare = models.IntegerField(
        choices=[
            [1, '1 - Much less'],
            [2, '2 - Less'],
            [3, '3 - About the same'],
            [4, '4 - More'],
            [5, '5 - Much more'],
        ],
        widget=widgets.RadioSelect,
        label='Would you invest less or more in healthcare?',
    )


def vars_for_admin_report(subsession):
    session = subsession.session
    participants = session.get_participants()
    n_created = len(participants)
    n_completed = sum(1 for p in participants if p.status == 'finished')
    completion_pct = round((n_completed / n_created * 100) if n_created else 0, 1)

    players = subsession.get_players()
    responses = [
        p.field_maybe_none('invest_in_healthcare')
        for p in players
        if p.field_maybe_none('invest_in_healthcare') is not None
    ]
    total_responses = len(responses)
    counts = {score: responses.count(score) for score in range(1, 6)}
    mean = round(sum(responses) / total_responses, 2) if total_responses else 0
    question = dict(
        label='Would you invest less or more in healthcare?',
        mean=mean,
        n=total_responses,
        distribution=[
            dict(
                score=score,
                count=counts[score],
                pct=round((counts[score] / total_responses * 100), 1)
                if total_responses
                else 0,
                width=round((counts[score] / total_responses * 100), 1)
                if total_responses
                else 0,
            )
            for score in range(1, 6)
        ],
    )

    return dict(
        session_name=session.code,
        n_created=n_created,
        n_completed=n_completed,
        completion_pct=completion_pct,
        questions=[question],
        comments=[],
    )


# PAGES
class Survey(Page):
    form_model = 'player'
    form_fields = ['invest_in_healthcare']


class ResultsWaitPage(WaitPage):
    pass


class ThankYou(Page):
    pass


page_sequence = [Survey, ResultsWaitPage, ThankYou]
