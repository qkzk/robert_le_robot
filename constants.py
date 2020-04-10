VERBOSE = True

# Files
PATH_TOKEN_BOT = "./config/token.robert"
PATH_OPTIONS_SERVER = "./config/server_options.yml"
PATH_STANDARD_ANSWERS = './responses/standard_answers.yml'
PATH_TEAM_CLASSROOM = './config/team_classroom.yml'
# globals
PATH_LOGFILE = './log/robert.log'

# key words
START_COMMAND = "!robert "
START_LATEX = "```latex"
END_LATEX = "\n```"

# Formatting options
DATETIME_FORMAT = "La date est %Y-%m-%d et il est %H:%M"
LOG_FORMAT = '%(asctime)s %(levelname)s %(pathname)s %(funcName)s(%(lineno)d) %(message)s'

DEFAULT_MUTE_DURATION = 60

EMOJI_NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five',
                 'six', 'seven', 'eight', 'nine', 'ten']
EMOJIS_YES_NO = {"oui": "green_heart",
                 "non": "red_circle"}
