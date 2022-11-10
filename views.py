from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import cgi
import actions

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/result", methods = [ "POST", "GET" ])
def result():
    # need to fix this one!!!
    if request.method == "POST":
        form = cgi.FieldStorage()
        word = form.getvalue("word")
        
        word_l = actions.save_vocab()
        probabilities = actions.get_probabilities(actions.get_count(word_l, word))
        calculate = actions.calculate(word, word_l, probabilities)
        if word in word_l:
            return render_template("result.html", result = f"We have {word} in our dictionary!")
        return render_template("result.html", result = calculate)