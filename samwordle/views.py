from click import option
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import random
import numpy as np
import pandas as pd
from tqdm import tqdm

from samwordle.bot import Agent
from samwordle.samwordle import samwordle

import json
import pickle
from django.forms.models import model_to_dict

ROWS = 6
LETTERS = 5
GAMES = 10

w_bank = pd.read_csv("./wordle/samwordle/data/words.csv")
w_bank = w_bank[w_bank["words"].str.len() == LETTERS]
w_bank["words"] = w_bank["words"].str.upper()  # Convert all words to uppercase


def process(u_inp, game, bot, guess, i):
    game.colours[i] = [s for s in str(u_inp).upper()]
    game.board[i] = [s for s in str(guess).upper()]
    game.g_count += 1
    for x, s in enumerate(game.colours[i]):
        if s == "Y":
            if guess[x] in bot.y_letters:
                bot.y_letters[guess[x]].append(x)
            else:
                bot.y_letters[guess[x]] = [x]
        elif s == "B":
            if guess[x] in bot.g_letters:
                bot.g_letters.append(guess[x])
        elif s == "G":
            bot.prediction[x] = guess[x]


# Create your views here.
def index(request):
    print("--------------------------------------------------------------------")
    print("--------------------------------------------------------------------")
    print("--------------------------------------------------------------------")
    print(f' Your option is --> {request.session.get("your_options", False)}')
    if not request.session.get("your_options", False):
        your_options = []
    else:
        your_options = request.session.get("your_options", False)

    print(f" Your processed option is --> {your_options}")

    u_inp = request.POST.get("your_options", "")
    if u_inp == "":
        your_options = []
    else:
        your_options.append(u_inp)

    game = samwordle(None, rows=ROWS, letters=LETTERS)
    bot = Agent(game)

    guess = bot.choose_action()
    word_list = [guess]
    print(
        f"Calling process with {u_inp} and Guess {guess} and wordlist as {your_options}"
    )

    if u_inp != "":
        for i in range(len(your_options)):
            print("Entering the loop!!!")
            process(your_options[i], game, bot, guess, i)
            guess = bot.choose_action()
            word_list.append(guess)

    # return HttpResponse("Hello, world. You're at the samwordle index.")
    template = loader.get_template("index.html")
    context = {"data": guess, "list": word_list}

    while "" in your_options:
        your_options.remove("")
    print(f" Your returning option is --> {your_options}")
    request.session["your_options"] = your_options
    print("--------------------------------------------------------------------")
    print("--------------------------------------------------------------------")
    print("--------------------------------------------------------------------")

    return HttpResponse(template.render(context, request))
