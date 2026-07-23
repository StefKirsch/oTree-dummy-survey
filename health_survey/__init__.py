from otree.api import *


doc = """
Three-round healthcare-system simulation. Stakeholders make a different
trade-off in every round, wait for the whole session, and receive a shared
report. Later reports explicitly carry forward results from earlier rounds.
"""


class C(BaseConstants):
    NAME_IN_URL = 'health_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3

    LIKERT_CHOICES = [
        [1, '1 – Strongly disagree'],
        [2, '2 – Disagree'],
        [3, '3 – Neither agree nor disagree'],
        [4, '4 – Agree'],
        [5, '5 – Strongly agree'],
    ]


ROLES = [
    dict(key='we_for_you', name='We-for-You'),
    dict(key='health_alliance', name='Health Alliance'),
    dict(key='gps', name='GPs'),
    dict(key='hmc', name='HMC'),
    dict(key='nurses', name='Nurses'),
    dict(key='doctors', name='Doctors'),
    dict(key='elderly_care', name='Elderly care'),
    dict(key='medtech', name='MedTech'),
    dict(key='bigtech', name='BigTech'),
    dict(key='new_tech', name='New Tech'),
    dict(key='patients', name='Patients'),
]

ROLE_BY_KEY = {role['key']: role for role in ROLES}
TEST_ROLE_KEYS = ('doctors', 'patients', 'medtech')


# Metric effects are signed weights. Agreement with a role's statement raises
# a metric when its weight is positive and lowers it when negative.
ROUNDS = {
    1: dict(
        title='Cost and financial burden',
        short='Who pays, what is protected, and where savings are made',
        questions={
            'we_for_you': (
                'All organisations should accept one capped regional budget '
                'and share savings, even if some lose control of their funds.'
            ),
            'health_alliance': (
                'Treatment funding should move to prevention now, even if '
                'providers have less money for care this year.'
            ),
            'gps': (
                'GP funding should increase through cuts to hospital budgets, '
                'even if some specialist services shrink.'
            ),
            'hmc': (
                'Hospital capacity should be fully funded, even if taxes and '
                'insurance premiums must rise.'
            ),
            'nurses': (
                'Nurse staffing and pay should increase, even if total health '
                'spending rises.'
            ),
            'doctors': (
                'Specialist staffing and clinical budgets should be protected, '
                'even if the region misses its savings target.'
            ),
            'elderly_care': (
                'Long-term and home-care funding should be ring-fenced, even '
                'if other providers receive less.'
            ),
            'medtech': (
                'Proven medical technology should be reimbursed quickly, even '
                'if it raises premiums and provider costs.'
            ),
            'bigtech': (
                'Providers should use one shared commercial platform to save '
                'money, even if this creates dependence on one supplier.'
            ),
            'new_tech': (
                'Promising start-ups should receive paid pilots before savings '
                'are proven, even if providers carry the financial risk.'
            ),
            'patients': (
                'Out-of-pocket charges should be capped, even if taxpayers and '
                'providers must absorb the remaining cost.'
            ),
        },
        metrics=[
            dict(
                key='cost_control',
                name='Cost control',
                short='Ability to keep total system spending down',
                color='#176B87',
                explanation=(
                    'A high score means stronger pressure to limit total '
                    'spending. New staffing, capacity, and technology tend to '
                    'lower it; pooling and scale savings tend to raise it.'
                ),
                effects={
                    'we_for_you': 1.4, 'health_alliance': 0.7, 'gps': 0.2,
                    'hmc': -1.4, 'nurses': -1.3, 'doctors': -1.2,
                    'elderly_care': -0.8, 'medtech': -1.3, 'bigtech': 1.2,
                    'new_tech': -1.0, 'patients': 0.3,
                },
                carryovers=[],
            ),
            dict(
                key='household_affordability',
                name='Household affordability',
                short='Protection from premiums and out-of-pocket costs',
                color='#C45A3B',
                explanation=(
                    'A high score means households are better protected from '
                    'paying directly. Price caps and pooled funding help; '
                    'costly capacity and technology can shift costs to them.'
                ),
                effects={
                    'we_for_you': 0.8, 'health_alliance': 0.5, 'gps': 0.4,
                    'hmc': -0.8, 'nurses': -0.5, 'doctors': -0.5,
                    'elderly_care': 0.7, 'medtech': -1.2, 'bigtech': 0.4,
                    'new_tech': -0.7, 'patients': 1.5,
                },
                carryovers=[],
            ),
            dict(
                key='provider_capacity',
                name='Provider financial capacity',
                short='Resources available to deliver care',
                color='#6B5CA5',
                explanation=(
                    'A high score means care organisations have more financial '
                    'room to operate. Protected service and staffing budgets '
                    'help; unfunded shifts, price caps, and risky purchases '
                    'reduce that room.'
                ),
                effects={
                    'we_for_you': -0.4, 'health_alliance': -0.7, 'gps': 1.0,
                    'hmc': 1.4, 'nurses': 1.2, 'doctors': 1.1,
                    'elderly_care': 1.0, 'medtech': -0.6, 'bigtech': 0.7,
                    'new_tech': -0.7, 'patients': -0.6,
                },
                carryovers=[],
            ),
        ],
    ),
    2: dict(
        title='Wait times, access, and staff workload',
        short='Who gets access quickly and who carries the work',
        questions={
            'we_for_you': (
                'All referrals should use one regional waiting list, even if '
                'patients and providers lose some choice.'
            ),
            'health_alliance': (
                'Staff should spend more time on prevention, even if treatment '
                'waiting lists grow at first.'
            ),
            'gps': (
                'GPs should take more gatekeeping and follow-up work when '
                'funded, even if primary-care workload rises.'
            ),
            'hmc': (
                'Hospitals should extend clinic hours to shorten waits, even '
                'if staff workload increases.'
            ),
            'nurses': (
                'Nurses should independently handle more patients to shorten '
                'waits, even if their responsibility and workload increase.'
            ),
            'doctors': (
                'Doctors should cap appointments at a safe workload, even if '
                'patients wait longer.'
            ),
            'elderly_care': (
                'Home-care clients should receive priority access, even if '
                'other waiting lists move more slowly.'
            ),
            'medtech': (
                'Providers should automate triage to shorten waits, even if '
                'staff first carry extra training and implementation work.'
            ),
            'bigtech': (
                'One algorithm should allocate appointments across providers, '
                'even if local staff lose scheduling control.'
            ),
            'new_tech': (
                'Virtual-care pilots should be offered widely to add access, '
                'even if staff must support an immature service.'
            ),
            'patients': (
                'Patients should be guaranteed rapid access to requested care, '
                'even if medical staff workloads increase.'
            ),
        },
        metrics=[
            dict(
                key='timely_access',
                name='Timely access',
                short='Shorter waits and fewer access barriers',
                color='#176B87',
                explanation=(
                    'A high score means patients can reach care sooner. '
                    'Pooling, extended hours, task sharing, and digital access '
                    'help; protected workloads and diverted capacity can hurt.'
                ),
                effects={
                    'we_for_you': 1.2, 'health_alliance': -0.8, 'gps': 0.5,
                    'hmc': 1.2, 'nurses': 1.3, 'doctors': -1.2,
                    'elderly_care': -0.3, 'medtech': 0.9, 'bigtech': 1.0,
                    'new_tech': 0.9, 'patients': 1.4,
                },
                carryovers=[
                    (1, 'cost_control', -0.15),
                    (1, 'household_affordability', 0.10),
                    (1, 'provider_capacity', 0.25),
                ],
            ),
            dict(
                key='workload_sustainability',
                name='Workload sustainability',
                short='A manageable workload for medical staff',
                color='#C45A3B',
                explanation=(
                    'A high score means workload is more manageable. Shared '
                    'systems, automation, and safe caps help; extra hours, '
                    'tasks, and guaranteed rapid access create pressure.'
                ),
                effects={
                    'we_for_you': 0.7, 'health_alliance': -0.4, 'gps': -0.8,
                    'hmc': -1.2, 'nurses': -1.2, 'doctors': 1.5,
                    'elderly_care': -0.2, 'medtech': 0.5, 'bigtech': 0.8,
                    'new_tech': -0.5, 'patients': -1.4,
                },
                carryovers=[
                    (1, 'cost_control', -0.10),
                    (1, 'provider_capacity', 0.25),
                ],
            ),
            dict(
                key='care_capacity',
                name='Available care capacity',
                short='Appointments and treatment the system can supply',
                color='#6B5CA5',
                explanation=(
                    'A high score means the system can offer more care. '
                    'Extended delivery, broader roles, and virtual services '
                    'help; moving staff away from treatment or limiting work '
                    'reduces immediate capacity.'
                ),
                effects={
                    'we_for_you': 0.8, 'health_alliance': -1.0, 'gps': 0.7,
                    'hmc': 1.2, 'nurses': 1.3, 'doctors': -0.9,
                    'elderly_care': 0.3, 'medtech': 0.8, 'bigtech': 0.7,
                    'new_tech': 1.0, 'patients': 0.5,
                },
                carryovers=[
                    (1, 'cost_control', -0.15),
                    (1, 'household_affordability', 0.05),
                    (1, 'provider_capacity', 0.25),
                ],
            ),
        ],
    ),
    3: dict(
        title='Quality and coverage of care',
        short='How good care is and who receives it',
        questions={
            'we_for_you': (
                'Providers should follow one regional care standard, even if '
                'it limits local autonomy and patient choice.'
            ),
            'health_alliance': (
                'Quality targets should include prevention and population '
                'health, even if fewer resources go to individual treatments.'
            ),
            'gps': (
                'GPs should coordinate each patient’s full pathway, even if '
                'this adds work and limits direct specialist access.'
            ),
            'hmc': (
                'Complex care should be concentrated in specialist hospitals '
                'to improve quality, even if some patients travel farther.'
            ),
            'nurses': (
                'Nurses should lead standard follow-up for more patients, even '
                'if doctor contact becomes less frequent.'
            ),
            'doctors': (
                'Doctors should be free to depart from regional protocols for '
                'individual patients, even if care becomes less consistent.'
            ),
            'elderly_care': (
                'Coverage should include comprehensive long-term and home care, '
                'even if fewer resources remain for acute treatments.'
            ),
            'medtech': (
                'Only technologies with strong quality evidence should be '
                'covered, even if access to new products is slower.'
            ),
            'bigtech': (
                'A shared data platform should support care everywhere, even '
                'if patients have less control over which provider uses data.'
            ),
            'new_tech': (
                'Promising innovations should be covered early, even if their '
                'quality evidence is still uncertain.'
            ),
            'patients': (
                'Every patient should receive the same broad benefit package, '
                'even if some preferred treatments are excluded.'
            ),
        },
        metrics=[
            dict(
                key='care_quality',
                name='Care quality',
                short='Safety, evidence, and clinical effectiveness',
                color='#176B87',
                explanation=(
                    'A high score means care is safer and more evidence based. '
                    'Standards, specialization, and evidence thresholds help; '
                    'unproven adoption and inconsistent pathways can hurt.'
                ),
                effects={
                    'we_for_you': 1.0, 'health_alliance': 0.6, 'gps': 0.7,
                    'hmc': 1.2, 'nurses': 0.5, 'doctors': -0.5,
                    'elderly_care': 0.3, 'medtech': 1.3, 'bigtech': 0.7,
                    'new_tech': -1.2, 'patients': 0.6,
                },
                carryovers=[
                    (1, 'provider_capacity', 0.10),
                    (2, 'timely_access', 0.10),
                    (2, 'workload_sustainability', 0.25),
                ],
            ),
            dict(
                key='population_coverage',
                name='Population coverage',
                short='How broadly people and needs are included',
                color='#C45A3B',
                explanation=(
                    'A high score means more people and care needs are covered. '
                    'Population goals, broad roles, data sharing, and equal '
                    'benefits help; concentration and strict exclusions hurt.'
                ),
                effects={
                    'we_for_you': 0.8, 'health_alliance': 1.2, 'gps': 0.7,
                    'hmc': -0.8, 'nurses': 0.9, 'doctors': -0.3,
                    'elderly_care': 1.3, 'medtech': -0.6, 'bigtech': 1.0,
                    'new_tech': 0.7, 'patients': 1.4,
                },
                carryovers=[
                    (1, 'household_affordability', 0.15),
                    (2, 'timely_access', 0.20),
                    (2, 'care_capacity', 0.15),
                ],
            ),
            dict(
                key='continuity',
                name='Continuity of care',
                short='Coordination across providers and over time',
                color='#6B5CA5',
                explanation=(
                    'A high score means patients experience a connected '
                    'pathway. Regional standards, GP coordination, follow-up, '
                    'and shared data help; fragmented discretion can hurt.'
                ),
                effects={
                    'we_for_you': 1.3, 'health_alliance': 0.7, 'gps': 1.4,
                    'hmc': -0.3, 'nurses': 1.1, 'doctors': -0.9,
                    'elderly_care': 1.0, 'medtech': 0.2, 'bigtech': 1.2,
                    'new_tech': -0.2, 'patients': 0.8,
                },
                carryovers=[
                    (1, 'provider_capacity', 0.10),
                    (2, 'timely_access', 0.10),
                    (2, 'workload_sustainability', 0.15),
                    (2, 'care_capacity', 0.15),
                ],
            ),
        ],
    ),
}


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
        return [ROLE_BY_KEY[key] for key in TEST_ROLE_KEYS]
    return ROLES


def creating_session(subsession):
    roles = _participating_roles(
        subsession.session.config.get('test_mode', False)
    )
    for player in subsession.get_players():
        if subsession.round_number == 1:
            role_key = roles[
                (player.id_in_subsession - 1) % len(roles)
            ]['key']
            player.participant.vars['hcs_role'] = role_key
        else:
            role_key = player.participant.vars['hcs_role']
        player.stakeholder_role = role_key


def _ensure_labeled_room_role(player):
    """Make role-named room links deterministic, regardless of join order."""
    label = player.participant.label
    eligible_keys = (
        set(TEST_ROLE_KEYS)
        if player.session.config.get('test_mode', False)
        else set(ROLE_BY_KEY)
    )
    if label in eligible_keys and label != player.stakeholder_role:
        player.participant.vars['hcs_role'] = label
        for round_player in player.in_all_rounds():
            round_player.stakeholder_role = label


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


def _scoring_averages(players):
    players = list(players)
    role_averages = _role_averages(players)
    assumed_neutral = (
        set(ROLE_BY_KEY) - set(TEST_ROLE_KEYS)
        if _is_test_mode(players)
        else set()
    )
    averages = {role_key: 3 for role_key in assumed_neutral}
    averages.update(role_averages)
    return role_averages, averages, assumed_neutral


def _clamp(value):
    return max(0, min(100, value))


def _metric_lookup(metrics):
    return {metric['key']: metric for metric in metrics}


def calculate_metrics(subsession, cache=None):
    """Return the three report metrics for one round, including carry-over."""
    cache = {} if cache is None else cache
    round_number = subsession.round_number
    if round_number in cache:
        return cache[round_number]

    players = list(subsession.get_players())
    role_averages, scoring_averages, assumed_neutral = _scoring_averages(
        players
    )
    previous = {}
    for prior_round in range(1, round_number):
        prior_subsession = subsession.in_round(prior_round)
        previous[prior_round] = _metric_lookup(
            calculate_metrics(prior_subsession, cache)
        )

    metrics = []
    for definition in ROUNDS[round_number]['metrics']:
        effects = {
            role_key: effect
            for role_key, effect in definition['effects'].items()
            if role_key in scoring_averages
        }
        weight_total = sum(abs(effect) for effect in effects.values())
        vote_numerator = sum(
            effect * ((scoring_averages[role_key] - 3) / 2)
            for role_key, effect in effects.items()
        )
        vote_effect = (
            25 * vote_numerator / weight_total if weight_total else 0
        )

        carryover_effect = 0
        carryover_rows = []
        for source_round, source_key, coefficient in definition['carryovers']:
            source = previous[source_round][source_key]
            effect = coefficient * (source['value'] - 50)
            carryover_effect += effect
            carryover_rows.append(
                dict(
                    round_number=source_round,
                    name=source['name'],
                    value=source['display_value'],
                    coefficient=coefficient,
                    effect=round(effect, 1),
                    calculation=(
                        '{coefficient:g} × ({value:.1f} − 50) = '
                        '{effect:+.1f}'
                    ).format(
                        coefficient=coefficient,
                        value=source['value'],
                        effect=effect,
                    ),
                )
            )

        raw_value = 50 + vote_effect + carryover_effect
        value = round(_clamp(raw_value), 1)
        display_value = value if effects or carryover_rows else '—'

        contributing_roles = []
        for role_key, effect in effects.items():
            role_mean = scoring_averages[role_key]
            contribution = (
                25
                * effect
                * ((role_mean - 3) / 2)
                / weight_total
            )
            contributing_roles.append(
                dict(
                    name=ROLE_BY_KEY[role_key]['name'],
                    mean=round(role_mean, 2),
                    weight=effect,
                    contribution=round(contribution, 1),
                    assumed_neutral=role_key in assumed_neutral,
                )
            )

        if carryover_rows:
            previous_explanation = (
                'Earlier scores shift the 50-point baseline using the '
                'carry-over terms below. A prior score of 50 has no effect.'
            )
        else:
            previous_explanation = (
                'This is the opening round, so no previous result influences '
                'this metric.'
            )

        metrics.append(
            dict(
                key=definition['key'],
                name=definition['name'],
                short=definition['short'],
                color=definition['color'],
                explanation=definition['explanation'],
                value=value,
                display_value=display_value,
                vote_effect=round(vote_effect, 1),
                carryover_effect=round(carryover_effect, 1),
                calculation=(
                    '50 {vote:+.1f} from this round '
                    '{carry:+.1f} carried forward = {value:.1f}'
                ).format(
                    vote=vote_effect,
                    carry=carryover_effect,
                    value=value,
                ),
                formula=(
                    'Score = clamp(50 + 25 × '
                    '[Σ(weight × (role mean − 3) ÷ 2) ÷ Σ|weight|] '
                    '+ Σ[coefficient × (prior score − 50)], 0, 100)'
                ),
                previous_explanation=previous_explanation,
                carryovers=carryover_rows,
                contributors=contributing_roles,
                represented_count=sum(
                    role_key in role_averages for role_key in effects
                ),
                assumed_neutral_count=sum(
                    role_key in assumed_neutral for role_key in effects
                ),
            )
        )

    cache[round_number] = metrics
    return metrics


def previous_reports(subsession, role_key=None):
    cache = {}
    return [
        dict(
            round_number=round_number,
            title=ROUNDS[round_number]['title'],
            short=ROUNDS[round_number]['short'],
            question=(
                ROUNDS[round_number]['questions'][role_key]
                if role_key
                else None
            ),
            metrics=calculate_metrics(
                subsession.in_round(round_number), cache
            ),
        )
        for round_number in range(1, subsession.round_number)
    ]


def reports_through_current_round(subsession, role_key):
    reports = previous_reports(subsession, role_key)
    round_number = subsession.round_number
    reports.append(
        dict(
            round_number=round_number,
            title=ROUNDS[round_number]['title'],
            short=ROUNDS[round_number]['short'],
            question=ROUNDS[round_number]['questions'][role_key],
            metrics=calculate_metrics(subsession),
        )
    )
    return reports


def role_rows(subsession):
    players = list(subsession.get_players())
    role_averages, _, assumed_neutral = _scoring_averages(players)
    round_data = ROUNDS[subsession.round_number]
    rows = []
    for role in ROLES:
        average = role_averages.get(role['key'])
        is_assumed_neutral = role['key'] in assumed_neutral
        rows.append(
            dict(
                name=role['name'],
                question=round_data['questions'][role['key']],
                n=sum(
                    player.stakeholder_role == role['key']
                    and player.field_maybe_none('impact_choice') is not None
                    for player in players
                ),
                mean=(
                    3
                    if is_assumed_neutral
                    else round(average, 2)
                    if average is not None
                    else '—'
                ),
                basis=(
                    'Non-participating; assumed neutral'
                    if is_assumed_neutral
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
        _ensure_labeled_room_role(player)
        round_data = ROUNDS[player.round_number]
        role = ROLE_BY_KEY[player.stakeholder_role]
        return dict(
            role=role,
            round_data=round_data,
            question=round_data['questions'][player.stakeholder_role],
            previous_reports=previous_reports(
                player.subsession, player.stakeholder_role
            ),
        )


class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = 'Waiting for all stakeholders'
    body_text = (
        'The round report will open when every stakeholder has submitted. '
        'You can safely close this page and reopen the same participant link.'
    )


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        _ensure_labeled_room_role(player)
        return dict(
            role=ROLE_BY_KEY[player.stakeholder_role],
            round_data=ROUNDS[player.round_number],
            reports=reports_through_current_round(
                player.subsession, player.stakeholder_role
            ),
            test_mode=player.session.config.get('test_mode', False),
            is_last_round=player.round_number == C.NUM_ROUNDS,
        )


page_sequence = [Survey, ResultsWaitPage, Results]


def vars_for_admin_report(subsession):
    players = list(subsession.get_players())
    completed = [
        player
        for player in players
        if player.field_maybe_none('impact_choice') is not None
    ]
    return dict(
        session_name=subsession.session.config.get(
            'display_name', subsession.session.config['name']
        ),
        round_data=ROUNDS[subsession.round_number],
        round_number=subsession.round_number,
        n_created=len(players),
        n_completed=len(completed),
        completion_pct=(
            round(100 * len(completed) / len(players), 1) if players else 0
        ),
        test_mode=subsession.session.config.get('test_mode', False),
        metrics=calculate_metrics(subsession),
        previous_reports=previous_reports(subsession),
        roles=role_rows(subsession),
    )


def custom_export(players):
    yield [
        'session_code',
        'participant_code',
        'participant_label',
        'round',
        'round_topic',
        'role_key',
        'role_name',
        'question',
        'impact_choice',
        'metric_1_name',
        'metric_1_value',
        'metric_2_name',
        'metric_2_value',
        'metric_3_name',
        'metric_3_value',
    ]

    for player in players:
        role = ROLE_BY_KEY[player.stakeholder_role]
        round_data = ROUNDS[player.round_number]
        metrics = calculate_metrics(player.subsession)
        yield [
            player.session.code,
            player.participant.code,
            player.participant.label,
            player.round_number,
            round_data['title'],
            player.stakeholder_role,
            role['name'],
            round_data['questions'][player.stakeholder_role],
            player.field_maybe_none('impact_choice'),
            metrics[0]['name'],
            metrics[0]['display_value'],
            metrics[1]['name'],
            metrics[1]['display_value'],
            metrics[2]['name'],
            metrics[2]['display_value'],
        ]
