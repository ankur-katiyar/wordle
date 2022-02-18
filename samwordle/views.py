from click import option
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import random
import numpy as np
import pandas as pd
from tqdm import tqdm

from samwordle.pywordle import Wordle
from samwordle.pywordle import WordBank

import json
import pickle
from django.forms.models import model_to_dict

ROWS = 6
LETTERS = 5
GAMES = 10


def retrieve_session_vars(request):
    if not request.session.get("word_list", False):
        word_list = []
    else:
        word_list = request.session.get("word_list", False)
    if not request.session.get("select_list", False):
        select_list = []
    else:
        select_list = request.session.get("select_list", False)
    return select_list, word_list


def save_session_vars(request, select_list, word_list):
    print(f" Your Select_list is --> {select_list}")
    request.session["select_list"] = select_list
    print(f" Your word_list is --> {word_list}")
    request.session["word_list"] = word_list
    return


def return_HttpResponse(request, select_list, word_list, error_msg=""):
    # return HttpResponse("Hello, world. You're at the samwordle index.")
    template = loader.get_template("index.html")
    context = {
        "list": select_list,
        "word_list": word_list,
        "error_msg": error_msg,
    }
    return HttpResponse(template.render(context, request))


# Create your views here.
def index(request):
    print("--------------------------------------------------------------------")
    print("------- S T A R T ----T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    # print(f' Your option is --> {request.session.get("your_options", False)}')
    select_list, word_list = retrieve_session_vars(request)
    print(f" Your selectlist is -->       {select_list}")
    print(f" Your wordlist is -->         {word_list}")

    u_inp = request.POST.get("your_options", "").upper()
    selected_word = request.POST.get("selected_word", "").upper()
    print(f" Your u_inp is -->         {u_inp}")
    print(f" Your selected_word is --> {selected_word}")

    if len(u_inp) != 5:
        save_session_vars(request, select_list, word_list)
        return return_HttpResponse(
            request,
            select_list,
            word_list,
            "===> Please provide a valid color mask <==",
        )

    if u_inp.upper() == "RESET":
        save_session_vars(request, [], ["CRANE"])
        return return_HttpResponse(request, [], ["CRANE"], "Game has been reset!")

    if u_inp.upper() == "GGGGG":
        save_session_vars(request, [], ["CRANE"])
        return return_HttpResponse(request, [], ["CRANE"], "New Game started!")

    select_list.append(selected_word)
    wordle = Wordle(word_list)
    wordle.wordleBank.calc_letter_probs(wordle.letters)
    word_list = wordle.wordleBank.get_word(wordle.letters)
    input_mask = wordle.handle_input(selected_word, u_inp)

    wordle.process_word(input_mask)
    wordle.wordleBank.calc_letter_probs(wordle.letters)
    word_list = wordle.wordleBank.get_word(wordle.letters)

    if selected_word in word_list:
        word_list.remove(selected_word)
    print("--------------------------------------------------------------------")
    print("------- E N D --------T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    save_session_vars(request, select_list, word_list)
    return return_HttpResponse(request, select_list, word_list)
