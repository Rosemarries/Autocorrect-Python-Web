from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import pandas as pd
import actions

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/", methods = [ "POST", "GET" ])
def result():
    # need to fix this one!!!
    if request.method == "POST":
        word = request.form["word"]
        
        word_l = actions.save_vocab()
        probabilities = actions.get_probabilities(actions.get_count(word_l, word))
        calculate = actions.calculate(word, word_l, probabilities)
        if word in word_l:
            return render_template("result.html", tables=[f"We have {word} in our dictionary!"], titles="Result")
        return render_template("result.html", tables=[calculate.to_html(classes="data")], titles="Result")