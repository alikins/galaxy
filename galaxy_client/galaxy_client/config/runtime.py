# equiv to ansible.constants

# config data that is set at runtime (as opposed to defaults
# and constants)

# FIXME: replace with something backed with config files etc

# as used (for now) by utils/colors.py and display.py
ANSIBLE_FORCE_COLOR = False
ANSIBLE_NOCOLOR = False

# FIXME: replace with something namespace
# FIXME: replace with enums

COLOR_CHANGED = "yellow"
COLOR_DEBUG = "dark gray"
COLOR_DEPRECATE = "purple"
COLOR_ERROR = "red"
COLOR_VERBOSE = "blue"
COLOR_WARN = "bright purple"

# used by display.py
DEPRECATION_WARNINGS = True
SYSTEM_WARNINGS = True
