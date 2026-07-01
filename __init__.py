from otree.api import *


doc = """
Dummy classroom questionnaire with a teacher-only analytics page.
"""


class C(BaseConstants):
    NAME_IN_URL = 'cohort_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    LIKERT_CHOICES = [
        [1, '1 - Strongly disagree'],
        [2, '2'],
        [3, '3 - Neutral'],
        [4, '4'],
        [5, '5 - Strongly agree'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prepared = models.IntegerField(
        label="I felt prepared for today's topic.",
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelectHorizontal,
    )

    confidence = models.IntegerField(
        label="I feel confident applying the method.",
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelectHorizontal,
    )

    discussion_helped = models.IntegerField(
        label="The classroom discussion helped my understanding.",
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelectHorizontal,
    )

    comment = models.LongStringField(
        label="Optional: what should we discuss next?",
        blank=True,
    )


class Survey(Page):
    form_model = 'player'
    form_fields = [
        'prepared',
        'confidence',
        'discussion_helped',
        'comment',
    ]


class ThankYou(Page):
    pass


page_sequence = [Survey, ThankYou]


def _mean(values):
    values = [v for v in values if v is not None]
    if not values:
        return 'n/a'
    return round(sum(values) / len(values), 2)


def _distribution(players, field_name):
    values = [
        getattr(p, field_name)
        for p in players
        if getattr(p, field_name) is not None
    ]

    n = len(values)
    rows = []

    for score in range(1, 6):
        count = values.count(score)
        pct = round(100 * count / n, 1) if n else 0
        rows.append(
            dict(
                score=score,
                count=count,
                pct=pct,
                width=pct,
            )
        )

    return rows


def vars_for_admin_report(subsession):
    players = subsession.get_players()

    completed_players = [
        p for p in players
        if p.prepared is not None
    ]

    questions = [
        dict(
            field='prepared',
            label="Prepared for today's topic",
        ),
        dict(
            field='confidence',
            label='Confidence applying the method',
        ),
        dict(
            field='discussion_helped',
            label='Discussion helped understanding',
        ),
    ]

    for q in questions:
        field_name = q['field']
        values = [
            getattr(p, field_name)
            for p in completed_players
            if getattr(p, field_name) is not None
        ]
        q['n'] = len(values)
        q['mean'] = _mean(values)
        q['distribution'] = _distribution(completed_players, field_name)

    comments = [
        dict(
            participant_id=p.participant.id_in_session,
            participant_label=p.participant.label or '',
            comment=p.comment,
        )
        for p in completed_players
        if p.comment
    ]

    session = subsession.session

    return dict(
        session_name=session.config.get('display_name', session.config['name']),
        n_created=len(players),
        n_completed=len(completed_players),
        completion_pct=round(
            100 * len(completed_players) / len(players),
            1,
        ) if players else 0,
        questions=questions,
        comments=comments,
    )


def custom_export(players):
    yield [
        'session_code',
        'participant_code',
        'participant_label',
        'prepared',
        'confidence',
        'discussion_helped',
        'comment',
    ]

    for p in players:
        yield [
            p.session.code,
            p.participant.code,
            p.participant.label,
            p.prepared,
            p.confidence,
            p.discussion_helped,
            p.comment,
        ]