from copy import deepcopy
import json
from django.db import models


class samwordle(models.Model):
    class Meta:
        app_label = "samwordle"

    def __init__(
        self,
        word,
        g_count=0,
        w_hash_table={},
        rows=6,
        letters=5,
        board=[],
        colours=[],
        alph=[],
    ):
        self.g_count = 0
        self.word = word
        self.w_hash_table = w_hash_table
        if word is not None:
            for x, l in enumerate(word):
                if l in self.w_hash_table:
                    self.w_hash_table[l]["count"] += 1
                    self.w_hash_table[l]["pos"].append(x)
                else:
                    self.w_hash_table[l] = {"count": 1, "pos": [x]}
        self.rows = rows
        self.letters = letters
        self.board = [["" for _ in range(letters)] for _ in range(rows)]
        self.colours = [["" for _ in range(letters)] for _ in range(rows)]
        self.alph = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    def __iter__(self):
        yield from {
            "word": self.word,
            "g_count": self.g_count,
            "w_hash_table": self.w_hash_table,
            "rows": self.rows,
            "letters": self.letters,
            "board": self.board,
            "colours": self.colours,
            "alph": self.alph,
        }.items()

    @staticmethod
    def from_json(json_dct):
        print(json_dct)
        return samwordle(
            json_dct["word"],
            json_dct["g_count"],
            json_dct["w_hash_table"],
            json_dct["rows"],
            json_dct["letters"],
            json_dct["board"],
            json_dct["colours"],
            json_dct["alph"],
        )

    def is_end(self):
        if self.board[-1] != ["" for _ in range(self.letters)]:
            return True
        else:
            r = self.game_result()
            if r[0] == True:
                return True
            else:
                return False

    def game_result(self):
        win = (False, 99)
        for i, r in enumerate(self.board):
            if self.word == "".join(r):
                win = (True, i)
                break
        return win

    def update_board(self, u_inp):
        w_hash_table = deepcopy(self.w_hash_table)
        i_hash_table = {}
        for x, l in enumerate(str(u_inp).upper()):
            self.board[self.g_count][x] = l
            if l in i_hash_table:
                i_hash_table[l].append(x)
            else:
                i_hash_table[l] = [x]
        colours = {"G": [], "B": [], "Y": []}
        for l in i_hash_table:
            if l in w_hash_table:
                g_hold = []
                for p in i_hash_table[l]:
                    if p in w_hash_table[l]["pos"]:
                        g_hold.append(p)
                for p in g_hold:
                    i_hash_table[l].remove(p)
                colours["G"] += g_hold
                if len(g_hold) < w_hash_table[l]["count"]:
                    y_hold = []
                    for p in i_hash_table[l]:
                        y_hold.append(p)
                        if len(y_hold) == w_hash_table[l]["count"]:
                            break
                    for p in y_hold:
                        i_hash_table[l].remove(p)
                    colours["Y"] += y_hold
                for p in i_hash_table[l]:
                    colours["B"].append(p)
            else:
                colours["B"] += i_hash_table[l]
                i_hash_table[l] = []
        for c in colours:
            for p in colours[c]:
                self.colours[self.g_count][p] = c
        self.g_count += 1

    def valid_guess(self, u_inp):
        if len(u_inp) == 5 and False not in [
            False for s in str(u_inp).upper() if s not in self.alph
        ]:
            return True
        else:
            return False
