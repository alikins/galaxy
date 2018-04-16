
class GalaxyClientError(Exception):
    pass


# replacement for AnsibleOptionError
# FIXME: CliOptionError (singular Option) ?
class CliOptionsError(GalaxyClientError):
    pass


class ParserError(GalaxyClientError):
    pass
