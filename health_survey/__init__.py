from otree.api import *


doc = """
Proof-of-concept healthcare-system simulation. Participants are assigned a
stakeholder role, answer a role-specific incentive trade-off, and see three
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
        incentive='Pool authority and resources around coalition priorities.',
        question=(
            'Regional organisations should pool part of their budgets and '
            'decision authority under our coalition’s shared priorities, even '
            'when individual organisations would spend those resources '
            'differently.'
        ),
    ),
    dict(
        key='health_alliance',
        name='Health Alliance',
        incentive='Move resources upstream to prevention and population health.',
        question=(
            'Provider budgets should be shifted from treatment to prevention '
            'and population-health programmes led by the regional alliance, '
            'even if this reduces short-term clinical capacity.'
        ),
    ),
    dict(
        key='gps',
        name='GPs',
        incentive='Increase primary-care funding and gatekeeping authority.',
        question=(
            'More funding and gatekeeping authority should move from hospitals '
            'to general practice, even if hospitals must reduce some services.'
        ),
    ),
    dict(
        key='hmc',
        name='HMC',
        incentive='Protect hospital funding and specialist capacity.',
        question=(
            'Hospital funding and specialist capacity should be protected, '
            'even if this slows the shift of resources to primary, preventive, '
            'and home care.'
        ),
    ),
    dict(
        key='nurses',
        name='Nurses',
        incentive='Expand nursing scope, autonomy, and coordination authority.',
        question=(
            'Clinical tasks and coordination authority should shift from '
            'doctors to nurses, even when this reduces doctors’ control over '
            'care decisions.'
        ),
    ),
    dict(
        key='doctors',
        name='Doctors',
        incentive='Preserve professional discretion over clinical decisions.',
        question=(
            'Doctors should retain discretion over treatment and referral '
            'decisions, even when this produces variation from regional '
            'pathways and targets.'
        ),
    ),
    dict(
        key='elderly_care',
        name='Elderly care',
        incentive='Ring-fence resources for long-term and home care.',
        question=(
            'Funding should be ring-fenced for long-term and home care, even if '
            'acute-care organisations receive a smaller share of the regional '
            'budget.'
        ),
    ),
    dict(
        key='medtech',
        name='MedTech',
        incentive='Accelerate procurement while protecting product value and IP.',
        question=(
            'Purchasers should adopt and reimburse medical technologies '
            'quickly, even when higher prices or proprietary systems limit '
            'funds and interoperability.'
        ),
    ),
    dict(
        key='bigtech',
        name='BigTech',
        incentive='Gain data access and platform scale across organisations.',
        question=(
            'Health organisations should allow large technology platforms '
            'broad access to data and infrastructure so services can scale '
            'quickly, even if this increases dependence on a commercial '
            'platform.'
        ),
    ),
    dict(
        key='new_tech',
        name='New Tech',
        incentive='Lower barriers to pilots, reimbursement, and market entry.',
        question=(
            'New health technologies should receive fast-track pilots and '
            'reimbursement before long-term evidence is complete, even if '
            'established providers bear implementation risk.'
        ),
    ),
    dict(
        key='patients',
        name='Patients',
        incentive='Protect provider choice and rapid access to requested care.',
        question=(
            'Patients should retain broad provider choice and rapid access to '
            'requested care, even if regional planners cannot concentrate '
            'services or standardise pathways.'
        ),
    ),
]

ROLE_BY_KEY = {role['key']: role for role in ROLES}

# Test sessions use only these roles. All other stakeholder roles remain part
# of the metrics, with a neutral score, so test results stay comparable with
# full-session results.
TEST_ROLE_KEYS = ('doctors', 'patients', 'medtech')


# Responses are centred around neutral: role mean - 3. A positive effect means
# agreement with that role's incentive raises the metric; a negative effect
# means agreement lowers it. Dividing by the sum of absolute effects keeps the
# result on a 0–100 scale. Responses are averaged within roles first so a role's
# influence does not depend on the number of participants assigned to it.
METRIC_DEFINITIONS = [
    dict(
        key='system_alignment',
        name='System alignment',
        short='Shared direction rather than stakeholder control',
        color='#176B87',
        explanation=(
            'Rewards incentives that pool authority around regional goals and '
            'penalises incentives that preserve a stakeholder’s own budget, '
            'autonomy, choice, platform, or market position.'
        ),
        effects={
            'we_for_you': 1.5,
            'health_alliance': 1.0,
            'gps': -0.7,
            'hmc': -1.2,
            'nurses': -0.5,
            'doctors': -1.4,
            'elderly_care': -0.7,
            'medtech': -0.8,
            'bigtech': -1.1,
            'new_tech': -0.8,
            'patients': -1.0,
        },
    ),
    dict(
        key='accessible_care',
        name='Accessible care',
        short='Care close to patients with equitable capacity',
        color='#C45A3B',
        explanation=(
            'Rewards prevention, primary care, task sharing, home care, and '
            'patient access. It penalises incentives that protect scarce acute '
            'capacity or divert access resources to professional autonomy, '
            'technology prices, or risky adoption.'
        ),
        effects={
            'we_for_you': 0.8,
            'health_alliance': 1.4,
            'gps': 1.5,
            'hmc': -1.3,
            'nurses': 1.5,
            'doctors': -0.8,
            'elderly_care': 1.4,
            'medtech': -0.6,
            'new_tech': -0.7,
            'patients': 1.3,
        },
    ),
    dict(
        key='innovation_readiness',
        name='Innovation readiness',
        short='Ability to adopt and scale new ways of working',
        color='#6B5CA5',
        explanation=(
            'Rewards incentives that enable task redesign, technology '
            'procurement, data-platform scale, and experimentation. It '
            'penalises incentives that preserve established clinical control '
            'or prioritise immediate access over implementation capacity.'
        ),
        effects={
            'we_for_you': 0.7,
            'nurses': 0.8,
            'doctors': -1.2,
            'medtech': 1.5,
            'bigtech': 1.4,
            'new_tech': 1.6,
            'patients': -0.8,
        },
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


def _effect_terms(effects):
    terms = []
    for role_key, effect in effects.items():
        if effect < 0:
            operator = '−'
        elif terms:
            operator = '+'
        else:
            operator = ''
        terms.append(
            '{} {:g} × ({} mean − 3)'.format(
                operator,
                abs(effect),
                ROLE_BY_KEY[role_key]['name'],
            ).strip()
        )
    return ' '.join(terms)


def _effect_summary(effects):
    supports = [
        '{} ×{:g}'.format(ROLE_BY_KEY[role_key]['name'], effect)
        for role_key, effect in effects.items()
        if effect > 0
    ]
    opposes = [
        '{} ×{:g}'.format(ROLE_BY_KEY[role_key]['name'], abs(effect))
        for role_key, effect in effects.items()
        if effect < 0
    ]
    parts = []
    if supports:
        parts.append('Agreement raises the score: ' + ', '.join(supports))
    if opposes:
        parts.append('Agreement lowers the score: ' + ', '.join(opposes))
    return ' · '.join(parts)


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
            role_key: effect
            for role_key, effect in definition['effects'].items()
            if role_key in scoring_averages
        }
        total_effect = sum(abs(effect) for effect in scored.values())

        if total_effect:
            weighted_deviation = sum(
                (scoring_averages[role_key] - 3) * effect
                for role_key, effect in scored.items()
            )
            unbounded_value = 50 + 25 * weighted_deviation / total_effect
            value = round(max(0, min(100, unbounded_value)), 1)
            display_value = value
            calculation = (
                '50 + 25 × ({deviation:.2f} ÷ {total:g}) = {value:.1f}'
            ).format(
                deviation=weighted_deviation,
                total=total_effect,
                value=value,
            )
        else:
            value = 0
            display_value = '—'
            calculation = 'No contributing role has a response yet.'

        metrics.append(
            dict(
                key=definition['key'],
                name=definition['name'],
                short=definition['short'],
                color=definition['color'],
                value=value,
                display_value=display_value,
                explanation=definition['explanation'],
                formula=(
                    'Score = clamp(50 + 25 × [Σ(eᵣ × (role mean − 3)) '
                    '÷ Σ|eᵣ|], 0, 100)'
                ),
                effect_terms=(
                    _effect_terms(scored)
                    or 'No role effects are included yet.'
                ),
                contributors=(
                    _effect_summary(scored)
                    or 'No role effects are included yet.'
                ),
                calculation=calculation,
                represented_count=sum(
                    role_key in role_averages
                    for role_key in definition['effects']
                ),
                assumed_neutral_count=sum(
                    role_key in non_participating_role_keys
                    for role_key in definition['effects']
                ),
                possible_count=len(definition['effects']),
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
                incentive=role['incentive'],
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
