from otree.api import *


doc = """
Proof-of-concept healthcare-system simulation. Participants are assigned a
stakeholder role, answer a role-specific Likert question, and see three
aggregate system-impact metrics.
"""


class C(BaseConstants):
    NAME_IN_URL = 'health_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    LIKERT_CHOICES = [
        [1, '1 – Strongly disagree'],
        [2, '2 – Disagree'],
        [3, '3 – Neither agree nor disagree'],
        [4, '4 – Agree'],
        [5, '5 – Strongly agree'],
    ]


# This is the single source of truth for role names and questions. The order
# also determines how roles are allocated to participant numbers.
ROLES = [
    dict(
        key='we_for_you',
        name='We-for-You',
        question=(
            'Our coalition should prioritise initiatives that connect '
            'organisations around shared healthcare-system goals.'
        ),
    ),
    dict(
        key='health_alliance',
        name='Health Alliance',
        question=(
            'Regional health alliances should redirect more resources towards '
            'prevention and population health.'
        ),
    ),
    dict(
        key='gps',
        name='GPs',
        question=(
            'Primary care should receive more capacity to coordinate patients '
            'across the healthcare system.'
        ),
    ),
    dict(
        key='hmc',
        name='HMC',
        question=(
            'Hospitals should shift more resources from isolated specialist '
            'production towards integrated care pathways.'
        ),
    ),
    dict(
        key='nurses',
        name='Nurses',
        question=(
            'Nurses should have greater autonomy in care coordination and '
            'service improvement.'
        ),
    ),
    dict(
        key='doctors',
        name='Doctors',
        question=(
            'Doctors should standardise care pathways across organisations, '
            'even when this limits some local discretion.'
        ),
    ),
    dict(
        key='elderly_care',
        name='Elderly care',
        question=(
            'Elderly-care organisations should invest more in care at home '
            'and cross-sector coordination.'
        ),
    ),
    dict(
        key='medtech',
        name='MedTech',
        question=(
            'MedTech companies should prioritise interoperable solutions with '
            'demonstrable patient value.'
        ),
    ),
    dict(
        key='bigtech',
        name='BigTech',
        question=(
            'BigTech companies should share data infrastructure with health '
            'partners under public governance.'
        ),
    ),
    dict(
        key='new_tech',
        name='New Tech',
        question=(
            'Emerging health technologies should be adopted faster through '
            'supervised real-world experiments.'
        ),
    ),
    dict(
        key='patients',
        name='Patients',
        question=(
            'Patients should have greater influence over healthcare priorities '
            'and resource allocation.'
        ),
    ),
]

ROLE_BY_KEY = {role['key']: role for role in ROLES}

# Test sessions use only these roles. All other stakeholder roles remain part
# of the metrics, with a neutral score, so test results stay comparable with
# full-session results.
TEST_ROLE_KEYS = ('doctors', 'patients', 'medtech')


# A score of 1 maps to 0 impact points, 3 to 50, and 5 to 100. We first
# average multiple participants with the same role, so every represented role
# has the intended influence regardless of participant count.
METRIC_DEFINITIONS = [
    dict(
        key='system_alignment',
        name='System alignment',
        short='Shared direction across the HCS',
        color='#176B87',
        weights={role['key']: 1.0 for role in ROLES},
        formula='Equal-weight mean of all represented stakeholder roles.',
    ),
    dict(
        key='accessible_care',
        name='Accessible care',
        short='Capacity, coordination and equitable access',
        color='#C45A3B',
        weights={
            'we_for_you': 1.0,
            'health_alliance': 1.2,
            'gps': 1.4,
            'hmc': 1.1,
            'nurses': 1.4,
            'doctors': 1.1,
            'elderly_care': 1.3,
            'patients': 1.3,
        },
        formula=(
            'Weighted mean of care-delivery roles; GPs and nurses carry the '
            'largest weights.'
        ),
    ),
    dict(
        key='innovation_readiness',
        name='Innovation readiness',
        short='Responsible adoption and interoperability',
        color='#6B5CA5',
        weights={
            'health_alliance': 0.7,
            'hmc': 1.0,
            'nurses': 0.6,
            'doctors': 0.8,
            'medtech': 1.4,
            'bigtech': 1.2,
            'new_tech': 1.5,
            'patients': 0.8,
        },
        formula=(
            'Weighted mean of innovation roles; New Tech and MedTech carry '
            'the largest weights.'
        ),
    ),
]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    stakeholder_role = models.StringField()
    impact_choice = models.IntegerField(
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
        label='',
    )


def _is_test_mode(players):
    players = list(players)
    return bool(players and players[0].session.config.get('test_mode', False))


def _participating_roles(test_mode):
    if test_mode:
        return [ROLE_BY_KEY[role_key] for role_key in TEST_ROLE_KEYS]
    return ROLES


def creating_session(subsession):
    participating_roles = _participating_roles(
        subsession.session.config.get('test_mode', False)
    )
    for player in subsession.get_players():
        role = participating_roles[
            (player.id_in_subsession - 1) % len(participating_roles)
        ]
        player.stakeholder_role = role['key']
        player.participant.vars['hcs_role'] = role['key']


def _role_averages(players):
    values_by_role = {role['key']: [] for role in ROLES}
    for player in players:
        choice = player.field_maybe_none('impact_choice')
        if choice is not None and player.stakeholder_role in values_by_role:
            values_by_role[player.stakeholder_role].append(choice)

    return {
        role_key: sum(values) / len(values)
        for role_key, values in values_by_role.items()
        if values
    }


def calculate_metrics(players):
    players = list(players)
    test_mode = _is_test_mode(players)
    role_averages = _role_averages(players)
    non_participating_role_keys = (
        set(ROLE_BY_KEY) - set(TEST_ROLE_KEYS) if test_mode else set()
    )
    scoring_averages = {
        role_key: 3 for role_key in non_participating_role_keys
    }
    scoring_averages.update(role_averages)
    metrics = []

    for definition in METRIC_DEFINITIONS:
        scored = {
            role_key: weight
            for role_key, weight in definition['weights'].items()
            if role_key in scoring_averages
        }
        total_weight = sum(scored.values())

        if total_weight:
            weighted_likert = sum(
                scoring_averages[role_key] * weight
                for role_key, weight in scored.items()
            ) / total_weight
            value = round((weighted_likert - 1) * 25, 1)
            display_value = value
        else:
            value = 0
            display_value = '—'

        metrics.append(
            dict(
                key=definition['key'],
                name=definition['name'],
                short=definition['short'],
                color=definition['color'],
                value=value,
                display_value=display_value,
                formula=definition['formula'],
                contributors=', '.join(
                    '{} ×{:g}'.format(ROLE_BY_KEY[role_key]['name'], weight)
                    for role_key, weight in definition['weights'].items()
                ),
                represented_count=sum(
                    role_key in role_averages
                    for role_key in definition['weights']
                ),
                assumed_neutral_count=sum(
                    role_key in non_participating_role_keys
                    for role_key in definition['weights']
                ),
                possible_count=len(definition['weights']),
            )
        )

    return metrics


def role_rows(players):
    players = list(players)
    test_mode = _is_test_mode(players)
    non_participating_role_keys = (
        set(ROLE_BY_KEY) - set(TEST_ROLE_KEYS) if test_mode else set()
    )
    averages = _role_averages(players)
    rows = []
    for role in ROLES:
        role_players = [
            player
            for player in players
            if player.stakeholder_role == role['key']
            and player.field_maybe_none('impact_choice') is not None
        ]
        average = averages.get(role['key'])
        assumed_neutral = role['key'] in non_participating_role_keys
        rows.append(
            dict(
                name=role['name'],
                question=role['question'],
                n=len(role_players),
                mean=(
                    3
                    if assumed_neutral
                    else round(average, 2)
                    if average is not None
                    else '—'
                ),
                basis=(
                    'Non-participating; assumed neutral'
                    if assumed_neutral
                    else 'Participant response'
                    if average is not None
                    else 'No response'
                ),
            )
        )
    return rows


class Survey(Page):
    form_model = 'player'
    form_fields = ['impact_choice']

    @staticmethod
    def vars_for_template(player):
        return dict(role=ROLE_BY_KEY[player.stakeholder_role])


class ResultsWaitPage(WaitPage):
    title_text = 'Waiting for the healthcare system'
    body_text = 'The combined system impact will appear when everyone has responded.'


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            role=ROLE_BY_KEY[player.stakeholder_role],
            metrics=calculate_metrics(player.subsession.get_players()),
            test_mode=player.session.config.get('test_mode', False),
        )


page_sequence = [Survey, ResultsWaitPage, Results]


def vars_for_admin_report(subsession):
    players = subsession.get_players()
    completed_players = [
        player
        for player in players
        if player.field_maybe_none('impact_choice') is not None
    ]

    return dict(
        session_name=subsession.session.config.get(
            'display_name', subsession.session.config['name']
        ),
        n_created=len(players),
        n_completed=len(completed_players),
        completion_pct=(
            round(100 * len(completed_players) / len(players), 1)
            if players
            else 0
        ),
        test_mode=subsession.session.config.get('test_mode', False),
        metrics=calculate_metrics(players),
        roles=role_rows(players),
    )


def custom_export(players):
    yield [
        'session_code',
        'participant_code',
        'participant_label',
        'role_key',
        'role_name',
        'custom_question',
        'impact_choice',
        'system_alignment',
        'accessible_care',
        'innovation_readiness',
    ]

    players = list(players)
    metrics = {
        metric['key']: metric['display_value']
        for metric in calculate_metrics(players)
    }
    for player in players:
        role = ROLE_BY_KEY.get(
            player.stakeholder_role, dict(name='', question='')
        )
        yield [
            player.session.code,
            player.participant.code,
            player.participant.label,
            player.stakeholder_role,
            role['name'],
            role['question'],
            player.field_maybe_none('impact_choice'),
            metrics['system_alignment'],
            metrics['accessible_care'],
            metrics['innovation_readiness'],
        ]
