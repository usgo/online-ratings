from datetime import datetime
from pyparsing import alphanums, Combine, Literal, nums, oneOf, Optional, ParseException, Regex, Suppress, Word

'''
Definition of parsers to pull data out of AGAGD SQL dumps.
'''

_header = Literal('INSERT INTO `games` (`Game_ID`, `Tournament_Code`, '
                  '`Game_Date`, `Round`, `Pin_Player_1`, `Color_1`, `Rank_1`, '
                  '`Pin_Player_2`, `Color_2`, `Rank_2`, `Handicap`, `Komi`, '
                  '`Result`, `Sgf_Code`, `Online`, `Exclude`, `Rated`, '
                  '`Elab_Date`) VALUES(')

_bool = oneOf('1 0').setParseAction(lambda s, l, t: t[0] == '1')
_int = Regex('-?\d+').setParseAction(lambda s, l, t: int(t[0]))


def _quoted(expr):
    return Combine(Suppress(Literal("'")) + expr + Suppress(Literal("'")))

_color = _quoted(oneOf('B W'))
_rank = _quoted(Optional(Word(alphanums)))


def _parse_date(s, l, t):
    try:
        return datetime.strptime(t[0], "%Y-%m-%d")
    except ValueError:
        # If the date is invalid, return the epoch
        return datetime.utcfromtimestamp(0)

_date = _quoted(Word(nums + '-')).setParseAction(_parse_date)

# Define format expected for each field
_fields = [_int.setResultsName('Game_ID'),
           _quoted(Word(alphanums)).setResultsName('Tournament_Code'),
           _date.setResultsName('Game_Date'),
           _int.setResultsName('Round'),
           _int.setResultsName('Pin_Player_1'),
           _color.setResultsName('Color_1'),
           _rank.setResultsName('Rank_1'),
           _int.setResultsName('Pin_Player_2'),
           _color.setResultsName('Color_2'),
           _rank.setResultsName('Rank_2'),
           _int.setResultsName('Handicap'),
           _int.setResultsName('Komi'),
           _color.setResultsName('Result'),
           # If Sgf_Code is NULL then the key will not be inserted into the results dict
           _quoted(Optional(Word(alphanums + '-').setResultsName('Sgf_Code'))) | Literal('NULL'),
           _bool.setResultsName('Online'),
           _bool.setResultsName('Exclude'),
           _bool.setResultsName('Rated'),
           _date.setResultsName('Elab_Date')
           ]

# Join fields list with commas
loader_expr = Combine(_header + _fields[0])
for field in _fields[1:]:
    loader_expr += Combine(', ' + field)

loader_expr = Combine(loader_expr + Literal(');'))


def agagd_parser(file_):
    '''
    Generator which yields a mapping of field names to values from an AGAGD dump
    '''
    for line in file_:
        if line.startswith('INSERT INTO'):
            try:
                yield loader_expr.parseString(line)
            except ParseException as e:
                print("Malformed or unexpected line: " + line)
                raise e

# Expression for parsing out pin changes
# Match expressions of the form ([0-9]+, [0-9]+)[,;]
pin_change_expr = (Combine(Literal('(') + _int.setResultsName('old') + Literal(',')) +
                   Combine(_int.setResultsName('new') + Literal(')') + oneOf('; ,')))


def pin_change_parser(file_):
    '''
    Generator which yields a map of pin changes: {'old': <int>, 'new': <int>}
    '''
    for line in file_:
        if pin_change_expr.matches(line):
            yield pin_change_expr.parseString(line)
