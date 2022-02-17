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

from sys import platform

if platform == "win32":
    file_name = "./samwordle/data/words.csv"
else:
    file_name = "./wordle/samwordle/data/words.csv"


ROWS = 6
LETTERS = 5
GAMES = 10


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
    print("------- S T A R T ----T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    # print(f' Your option is --> {request.session.get("your_options", False)}')
    your_options, word_list = retrieve_session_vars(request)
    print(f" Your processed option is --> {your_options}")
    print(f" Your wordlist is -->         {word_list}")

    u_inp = request.POST.get("your_options", "").upper()

    if len(u_inp) != 5 and word_list != []:
        save_session_vars(request, your_options, word_list)
        return return_HttpResponse(
            request,
            word_list[-1],
            word_list,
            "===> Please provide a valid color mask <==",
        )

    if u_inp.upper() == "RESET":
        save_session_vars(request, [], [word_list[0]])
        return return_HttpResponse(
            request, word_list[0], [word_list[0]], "Game has been reset!"
        )

    if u_inp.upper() == "PRUNE" and len(word_list) > 1:
        save_session_vars(request, your_options[:-1], word_list[:-1])
        return return_HttpResponse(
            request, word_list[-1], word_list[:-1], "Deleted the last word"
        )

    your_options.append(u_inp)

    w_bank = pd.read_csv(file_name)
    w_bank = w_bank[w_bank["words"].str.len() == LETTERS]
    w_bank["words"] = w_bank["words"].str.upper()  # Convert all words to uppercase

    for word in w_bank:
        print(word["words"])

    print(w_bank)
    print("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print(file_name)

    game = samwordle(None, rows=ROWS, letters=LETTERS)
    bot = Agent(game)

    guess = bot.choose_action()
    word_list = [guess]
    print(
        f"Calling process with {u_inp} and Guess {guess} and option_list as {your_options}"
    )

    if u_inp != "":
        for i in range(len(your_options)):
            print("Entering the loop!!!")
            bot = Agent(game)
            process(your_options[i], game, bot, guess, i)
            guess = bot.choose_action()
            word_list.append(guess)

    while "" in your_options:
        your_options.remove("")
    print("--------------------------------------------------------------------")
    print("------- E N D --------T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    save_session_vars(request, your_options, word_list)
    return return_HttpResponse(request, guess, word_list)


def retrieve_session_vars(request):
    if not request.session.get("your_options", False):
        your_options = []
    else:
        your_options = request.session.get("your_options", False)

    if not request.session.get("word_list", False):
        word_list = []
    else:
        word_list = request.session.get("word_list", False)
    return your_options, word_list


def save_session_vars(request, your_options, word_list):
    print(f" Your returning option is --> {your_options}")
    request.session["your_options"] = your_options
    print(f" Your word_list is --> {word_list}")
    request.session["word_list"] = word_list
    return


def return_HttpResponse(request, guess, word_list, error_msg=""):
    # return HttpResponse("Hello, world. You're at the samwordle index.")
    template = loader.get_template("index.html")
    context = {"data": guess, "list": word_list, "error_msg": error_msg}
    return HttpResponse(template.render(context, request))
