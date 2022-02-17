import random
import re
import numpy as np
import pandas as pd

from sys import platform

if platform == "win32":
    file_name = "./data/words.csv"
else:
    file_name = "./wordle/samwordle/data/words.csv"

logging = False


class Wordle:
    def __init__(self, letters=5):
        self.letters = 5
        self.wordleBank = WordBank(self.letters)
        self.word_list = list()

    def process_word(self, word):
        self.word_list.append(word)
        # print(self.word_list)
        # self.wordleBank.calc_letter_probs(self.letters)
        # self.wordleBank.set_score(self.letters)
        self.wordleBank.reduce_word_bank(self.word_list[-1])
        # self.wordleBank.set_score(self.letters)


class WordBank:
    def __init__(self, letters, f_name=file_name):
        self.vowels = ["A", "E", "I", "O", "U", "Y"]
        w_bank = pd.read_csv(f_name)
        w_bank = w_bank[w_bank["words"].str.len() == letters]
        w_bank["words"] = w_bank["words"].str.upper()  # Convert all words to uppercase
        w_bank["v-count"] = (
            w_bank["words"]
            .apply(lambda x: "".join(set(x)))
            .str.count("|".join(self.vowels))
        )  # Count amount of vowels in words
        self.w_bank = w_bank
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

    def calc_letter_probs(self, letters):
        for x in range(letters):
            counts = self.w_bank["words"].str[x].value_counts(normalize=True).to_dict()
            # print("------------------------------")
            self.w_bank[f"p-{x}"] = self.w_bank["words"].str[x].map(counts)
            self.w_bank[f"pos-{x}"] = self.w_bank["words"].str[x]

    def get_word(self, letters):
        self.w_bank["w-score"] = [0] * len(self.w_bank)
        for x in range(letters):
            self.w_bank["w-score"] += self.w_bank[f"p-{x}"]
        mv_bank = self.w_bank[self.w_bank["w-score"] == self.w_bank["w-score"].max()]
        # print(self.w_bank.head(n=1000))
        if logging:
            print(mv_bank.head(n=1000))
        # return mv_bank["words"].to_list()[0]
        return (
            self.w_bank.sort_values("w-score", ascending=False)
            .head(10)["words"]
            .to_list()
        )

    def reduce_word_bank(self, word):
        # Regular Expression:
        # ^(?=.*A)(?=.*B)(?=.*C) - check if all 3 exists (any order)
        # ^(?=.*A)|(?=.*B)|(?=.*C)| - check if one of 3 exists (any order)
        # Creating string for Black

        for x in range(len(word)):
            if word[x][1] == "G":
                # print(
                #    f"Green Processing for x: {x} ===> char {word[x][0]} with mask as {word[x][1]}"
                # )
                self.w_bank = self.w_bank[
                    self.w_bank[f"pos-{x}"].str.contains(word[x][0])
                ]
                # print(self.w_bank.head(n=1000))

        word_list = self.w_bank["words"].tolist()
        if logging:
            print("Wordlist after filtering for Greens")
            print(word_list)

        colored_list = []
        for char in word:
            if char[1] == "G" or char[1] == "Y":
                colored_list.append(char[0])

        for x in range(len(word)):
            for char in word:
                if char[1] == "B" and word.index(char) == x:
                    self.w_bank = self.w_bank[
                        ~self.w_bank[f"pos-{x}"].str.contains(char[0])
                    ]
                    # print(self.w_bank.head(n=1000))
        word_list = self.w_bank["words"].tolist()
        if logging:
            print("Wordlist after filtering for Black at specific position")
            print(word_list)

        reg_str_black = "^"
        reg_str_yellow = "^"

        if logging:
            print(f"Value of word is {word}")
            print(f"Value of colored list {colored_list}")

        for char in word:
            if char[1] == "B" and char[0] not in colored_list:
                if reg_str_black.find(char[0]) < 0:
                    reg_str_black = reg_str_black + f"(?=.*{char[0]})|"
            if char[1] == "Y":
                # if reg_str_yellow.find(char[0]) < 0:
                replication_count = colored_list.count(char[0])
                reg_str_yellow = (
                    reg_str_yellow + "(?=" + f".*{char[0]}" * replication_count + ")"
                )

        reg_str_black = reg_str_black[:-1]
        reg_str_yellow = reg_str_yellow

        if logging:
            print(f"Black Processing for x: regstr - {reg_str_black}")
        if reg_str_black != "":
            self.w_bank = self.w_bank[
                ~self.w_bank[f"words"].str.contains(reg_str_black, regex=True)
            ]

        word_list = self.w_bank["words"].tolist()
        if logging:
            print("Wordlist after filtering for Blacks overall")
            print(word_list)

        for char in word:
            if char[1] == "Y":
                for x in range(len(word)):
                    # print(
                    #    f"Yellow Processing for x: {x} ===> char {char[0]} with mask as {char[1]}"
                    # )
                    # print(self.w_bank.head(n=10))
                    if word.index(char) == x:
                        # print("Removed")
                        self.w_bank = self.w_bank[
                            ~self.w_bank[f"pos-{x}"].str.contains(char[0])
                        ]
                    # print(self.w_bank.head(n=1000))

        word_list = self.w_bank["words"].tolist()
        if logging:
            print("Wordlist after filtering for Yellow - Incorrect Position")
            print(word_list)

        if logging:
            print(f"Yellow Processing for x: regstr - {reg_str_yellow}")
        # print(self.w_bank.head(n=1000))
        if reg_str_yellow != "":
            self.w_bank = self.w_bank[
                self.w_bank[f"words"].str.contains(reg_str_yellow, regex=True)
            ]
        word_list = self.w_bank["words"].tolist()
        if logging:
            print("Wordlist after filtering for Yellow on other positions")
            print(word_list)
            # print(len(word_list))
            print(word)


def handle_input(guess):
    input_mask = input(
        "\nNow enter the output in ##### format where # can be in B, G or Y. B represents a black tile, G a green tile and Y represents Yellow Tile\n"
    )
    if input_mask == "GGGGG":
        return "GGGGG"
    word = []
    for x in range(len(guess)):
        word.append((guess[x], input_mask[x]))
    print(f"Word mask is ==> {word}")
    return word


def main():
    wordle = Wordle()
    wordle.wordleBank.calc_letter_probs(wordle.letters)
    word_list = wordle.wordleBank.get_word(wordle.letters)
    # print(word_list)

    guess = "CRANE"
    print(f"Starting the game, the word that you should start with is ==> {guess}")

    input_mask = handle_input(guess)
    # print(word)

    while input_mask != "GGGGG":
        wordle.process_word(input_mask)
        wordle.wordleBank.calc_letter_probs(wordle.letters)
        word_list = wordle.wordleBank.get_word(wordle.letters)
        print("---------------------")
        print("You can select one of the following words")
        print(word_list)
        guess = input("Enter on of the words from the above list ==> ")
        print(f"The next word that you selected ==> {guess}")
        input_mask = handle_input(guess)

    print(wordle.word_list)
    # print(wordle.wordleBank.w_bank.to_string())
    # print(wordle.wordleBank.w_bank.head())
    # data_with_name = wordle.wordleBank.w_bank.set_index("words")
    # data_with_name = data_with_name.drop("CIGAR")
    # print(data_with_name.head())


if __name__ == "__main__":
    main()
