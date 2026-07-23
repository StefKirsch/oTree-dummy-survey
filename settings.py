from os import environ

SESSION_CONFIGS = [
    dict(
        name='health_survey',
        display_name='Healthcare System Stakeholder Simulation',
        app_sequence=['health_survey'],
        num_demo_participants=11,
    ),
    dict(
        name='health_survey_test',
        display_name='Healthcare System Stakeholder Simulation (3-role test mode)',
        app_sequence=['health_survey'],
        num_demo_participants=3,
        test_mode=True,
    ),
]

ROOMS = [
    dict(
        name='classroom',
        display_name='Classroom',
        participant_label_file='_rooms/classroom.txt',
        use_secure_urls=True,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    test_mode=False,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = [
    'hcs_analysis_version',
    'hcs_analysis_spec_json',
    'hcs_analysis_spec_hash',
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4394371123992'
