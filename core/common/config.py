VERSION = (1, 1, 0)

BANNER = '''
 ####################################################
 #                                                  #
 #            _________   CreatorSniper   _______   #
 #  _-----____/   ========================|______|  #
 #  |           ______________/                     #
 #  |    ___--_/(_)       ^                         #
 #  |___ ---                                        #
 #                                                  #
 ####################################################
 '''

PATTERN = '48 8D ? ? ? ? ? 4D 69 F6 ? ? ? ? 4C 03 ? 41 39 ? ? ? ? ? 0F 86 ? ? ? ? 48 8B'

EXPR_SESS_KEY = '''
memory.reset()
memory.add(3)
memory.rip()
memory.add(1544)
'''

EXPR_SESS_TICKET = '''
memory.reset()
memory.add(3)
memory.rip()
memory.add(512)
'''

EXPR_ACCT_TICKET = '''
memory.reset()
memory.add(3)
memory.rip()
'''

ROS_KEY = 'C4pWJwWIKGUxcHd69eGl2AOwH2zrmzZAoQeHfQFcMelybd32QFw9s10px6k0o75XZeB5YsI9Q9TdeuRgdbvKsxc='

ROS_VERSION = 11

FLASK_HOST = 'localhost'

FLASK_PORT = 5000

FLASK_DEBUG = False

FLASK_FOLDER = 'static'
