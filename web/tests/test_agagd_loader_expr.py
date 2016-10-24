from collections import ChainMap
from datetime import datetime
from pyparsing import ParseException
from tests import BaseTestCase
from scripts.parsing import loader_expr

test_line_format = ("INSERT INTO `games` (`Game_ID`, `Tournament_Code`, "
                    "`Game_Date`, `Round`, `Pin_Player_1`, `Color_1`, "
                    "`Rank_1`, `Pin_Player_2`, `Color_2`, `Rank_2`, "
                    "`Handicap`, `Komi`, `Result`, `Sgf_Code`, `Online`, "
                    "`Exclude`, `Rated`, `Elab_Date`) "
                    "VALUES({Game_ID}, {Tournament_Code}, "
                    "{Game_Date}, {Round}, {Pin_Player_1}, "
                    "{Color_1}, {Rank_1}, {Pin_Player_2}, "
                    "{Color_2}, {Rank_2}, {Handicap}, {Komi}, "
                    "{Result}, {Sgf_Code}, {Online}, {Exclude}, "
                    "{Rated}, {Elab_Date});\n")

base_map = {'Game_ID': 17,
            'Tournament_Code': "'edo1234'",
            'Game_Date': "'1835-06-27'",
            'Round': 1,
            'Pin_Player_1': 1234,
            'Color_1': "'W'",
            'Rank_1': "'9p'",
            'Pin_Player_2':  4321,
            'Color_2': "'B'",
            'Rank_2': "'7p'",
            'Handicap': 0,
            'Komi': 0,
            'Result': "'W'",
            'Sgf_Code': 'NULL',
            'Online': 0,
            'Exclude': 0,
            'Rated': 1,
            'Elab_Date': "'0000-00-00'"}


def _parse_with_values(**kwargs):
    line = test_line_format.format(**ChainMap(kwargs, base_map))
    return loader_expr.parseString(line)


class TestAgagdLoaderExpr(BaseTestCase):
    def test_dates(self):
        data = _parse_with_values()
        self.assertEqual(data['Game_Date'], datetime(year=1835, month=6, day=27))
        self.assertEqual(data['Elab_Date'], datetime.utcfromtimestamp(0))

    def test_colors(self):
        data = _parse_with_values(Color_1="'B'", Color_2="'W'", Result="'W'")
        self.assertEqual(data['Color_1'], 'B')
        self.assertEqual(data['Color_2'], 'W')
        self.assertEqual(data['Result'], 'W')

        with self.assertRaises(ParseException):
            _parse_with_values(Color_1="'Banana'")

        with self.assertRaises(ParseException):
            _parse_with_values(Color_2='')

        with self.assertRaises(ParseException):
            _parse_with_values(Color_1="''")

    def test_ints(self):
        data = _parse_with_values(Handicap=382, Komi=-17)
        self.assertEqual(data['Handicap'], 382)
        self.assertEqual(data['Komi'], -17)

        data = _parse_with_values(Pin_Player_1=1234, Pin_Player_2=4321)
        self.assertEqual(data['Pin_Player_1'], 1234)
        self.assertEqual(data['Pin_Player_2'], 4321)

    def test_ranks(self):
        for r1, r2 in (('7k', '4d'), ('8p', '4D'), ('', '')):
            data = _parse_with_values(Rank_1=repr(r1), Rank_2=repr(r2))
            self.assertEqual(data['Rank_1'], r1)
            self.assertEqual(data['Rank_2'], r2)

    def test_bool(self):
        data = _parse_with_values(Rated=0)
        self.assertEqual(data['Rated'], False)
        data = _parse_with_values(Rated=1)
        self.assertEqual(data['Rated'], True)

    def test_sgf_code(self):
        data = _parse_with_values(Sgf_Code="'abc123'")
        self.assertEqual(data['Sgf_Code'], 'abc123')

        for val in ("''", 'NULL'):
            data = _parse_with_values(Sgf_Code=val)
            self.assertNotIn('Sgf_Code', data)
