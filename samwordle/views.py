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
    if not request.session.get("guess_list", False):
        guess_list = []
    else:
        guess_list = request.session.get("guess_list", False)
    if not request.session.get("select_list", False):
        select_list = []
    else:
        select_list = request.session.get("select_list", False)
    if not request.session.get("word_list", False):
        word_list = []
    else:
        word_list = request.session.get("word_list", False)

    if not request.session.get("mask_list", False):
        mask_list = []
    else:
        mask_list = request.session.get("mask_list", False)

    # print(f"Active wordlist that is stored in session is -> {word_list}")
    return select_list, guess_list, word_list, mask_list


def save_session_vars(request, select_list, guess_list, word_list, mask_list):
    # print(f" Your Select_list is --> {select_list}")
    request.session["select_list"] = select_list
    # print(f" Your guess_list is --> {guess_list}")
    request.session["guess_list"] = guess_list
    # print(f" Your word_list is --> {word_list}")
    request.session["word_list"] = word_list
    # print(f" Your word_list is --> {mask_list}")
    request.session["mask_list"] = mask_list

    return


def return_HttpResponse(
    request, select_list, guess_list, active_word, mask_list, error_msg=""
):
    # return HttpResponse("Hello, world. You're at the samwordle index.")
    template = loader.get_template("index.html")
    context = {
        "list": select_list,
        "guess_list": guess_list,
        "error_msg": error_msg,
        "active_word": active_word,
        "mask_list": mask_list,
    }
    return HttpResponse(template.render(context, request))


def remove_duplicates(list_var):
    no_dups = []
    for items in list_var:
        if items not in no_dups:
            no_dups.append(items)
    return no_dups
    # seen = set()
    # seen_add = seen.add
    # return [x for x in list_var if not (x in seen or seen_add(x))]


# Create your views here.
def request_wordle(request):
    # def index(request):
    print("--------------------------------------------------------------------")
    print("------- S T A R T ----T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    # print(f' Your option is --> {request.session.get("your_options", False)}')
    select_list, guess_list, word_list, mask_list = retrieve_session_vars(request)
    select_list = remove_duplicates(select_list)

    print(f" Your selectlist is -->       {select_list}")
    print(f" Your masklist is -->       {mask_list}")
    # print(f" Your wordlist is -->         {guess_list}")

    u_inp = request.POST.get("your_options", "").upper()
    selected_word = request.POST.get("selected_word", "").upper()

    print("DJANGO VIEW")
    if request.method == "POST":
        print("DATA: ", request.POST.get("Colored_Word"))

    mask = ""
    for i in range(5):
        print("DATA: ", request.POST.get("mask" + str(i)))
        if request.POST.get("mask" + str(i)):
            mask = mask + request.POST.get("mask" + str(i))

    print(f" Your u_inp is -->         {u_inp}")
    print(f" Your selected_word is --> {selected_word}")
    print(f" Your mask is --> {mask}")

    u_inp = mask

    if u_inp == "XXXXX" or u_inp == "":
        u_inp = "RESET"

    if len(u_inp) != 5:
        save_session_vars(request, select_list, guess_list, word_list, mask_list)
        return return_HttpResponse(
            request,
            select_list,
            guess_list,
            selected_word,
            mask_list,
            "Press Reset the game",
        )

    if u_inp.upper() == "RESET":
        print("Resetting!!!")
        # save_session_vars(request, [], ["CRANE"], [])
        save_session_vars(
            request,
            [],
            [
                "SLATE",
                "SAUCE",
                "SLICE",
                "SHALE",
                "SAUTE",
                "SHARE",
                "SOOTY",
                "SHINE",
                "SUITE",
                "CRANE",
            ],
            [],
            [],
        )
        return return_HttpResponse(
            request,
            [],
            [
                "SLATE",
                "SAUCE",
                "SLICE",
                "SHALE",
                "SAUTE",
                "SHARE",
                "SOOTY",
                "SHINE",
                "SUITE",
                "CRANE",
            ],
            "SLATE",
            [],
            "",
        )

    if u_inp.upper() == "GGGGG":
        save_session_vars(
            request,
            [],
            [
                "SLATE",
                "SAUCE",
                "SLICE",
                "SHALE",
                "SAUTE",
                "SHARE",
                "SOOTY",
                "SHINE",
                "SUITE",
                "CRANE",
            ],
            [],
            [],
        )
        return return_HttpResponse(
            request,
            [],
            [
                "SLATE",
                "SAUCE",
                "SLICE",
                "SHALE",
                "SAUTE",
                "SHARE",
                "SOOTY",
                "SHINE",
                "SUITE",
                "CRANE",
            ],
            "SLATE",
            [],
            "",
        )

    select_list.append(selected_word)
    mask_list.append(u_inp)
    wordle = Wordle(word_list)
    wordle.wordleBank.calc_letter_probs(wordle.letters)
    guess_list = wordle.wordleBank.get_word(wordle.letters)
    input_mask = wordle.handle_input(selected_word, u_inp)

    wordle.process_word(input_mask)
    wordle.wordleBank.calc_letter_probs(wordle.letters)
    guess_list = wordle.wordleBank.get_word(wordle.letters)

    word_list = wordle.wordleBank.w_bank["words"].tolist()

    if selected_word in word_list:
        word_list.remove(selected_word)

    select_list = remove_duplicates(select_list)
    mask_list = mask_list[: len(select_list)]
    print("--------------------------------------------------------------------")
    print("------- E N D --------T H E ------P R O C E S S I N G --------------")
    print("--------------------------------------------------------------------")
    save_session_vars(request, select_list, guess_list, word_list, mask_list)
    return return_HttpResponse(
        request, select_list, guess_list, selected_word, mask_list
    )
