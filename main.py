from replit import db
from flask import Flask, render_template, redirect, request, make_response
from functions import *

app = Flask("app")

@app.route("/")
def index():
  username = request.cookies.get("username")
  if loggedIn():
    if checkUser():
      cards = list(db[username]["cards"].keys())
      recent = list(db[username]["cards"].keys())
      recent.reverse()
      cards = " ".join(cards)
      recentlength = len(recent)
      if recentlength >= 3:
        recent = [recent[0], recent[1], recent[2]]
      return render_template("home.html", username=username, cards=cards, recent=recent, recentlength=recentlength)
    else:
      return redirect("/logout")
  else:
    return render_template("notloggedin.html")

@app.route("/login")
def login():
  if loggedIn():
    return redirect("/")
  return render_template("login.html")

@app.route("/signup")
def signup():
  if loggedIn():
    return redirect("/")
  return render_template("signup.html")

@app.route("/loginsubmit", methods=["GET", "POST"])
def loginsubmit():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    loggedIn = request.cookies.get("loggedIn")
    if username in db.keys():
      if password == db[username]["password"]:
        resp = make_response(render_template('readcookie.html'))
        resp.set_cookie("loggedIn", "true")
        resp.set_cookie("username", username)
        resp.set_cookie("password", password)
        return resp
      else:
        return render_template("message.html", message="Incorrect password.", loggedIn=loggedIn)
    else:
      return render_template("message.html", message="Account not found.", loggedIn=loggedIn)

@app.route("/createaccount", methods=["GET", "POST"])
def createaccount():
  if request.method == "POST":
    newusername = request.form.get("newusername")
    newpassword = request.form.get("newpassword")
    loggedIn = request.cookies.get("loggedIn")
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cap_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    allchars = letters + cap_letters + numbers + ['_']
    print(newusername)
    for i in newusername:
      if i not in allchars:
        return render_template("message.html", message="Username can only contain alphanumeric characters and underscores.", loggedIn=loggedIn)
    if newusername in db.keys():
      return render_template("message.html", message="Username taken.", loggedIn=loggedIn)
    if newusername == "":
      return render_template("message.html", message="Please enter a username.", loggedIn=loggedIn)
    if newpassword == "":
      return render_template("message.html", message="Please enter a password.", loggedIn=loggedIn)
    db[newusername] = {"password":newpassword, "cards":{}}
    print("new account created")
    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie("loggedIn", "true")
    resp.set_cookie("username", newusername)
    resp.set_cookie("password", newpassword)
    return resp

@app.route("/logout")
def logout():
  resp = make_response(render_template('readcookie.html'))
  resp.set_cookie("loggedIn", "false")
  resp.set_cookie("username", "None")
  resp.set_cookie("password", "None")
  return resp

@app.route("/cards")
def cards():
  username = request.cookies.get("username")
  if loggedIn():
    if checkUser():
      cards = list(db[username]["cards"].keys())
      order = request.args.get("sort")
      if order == "old":
        sort = "Oldest first"
        pass
      elif order == "a-to-z":
        cards.sort()
        sort = "A to Z"
      elif order == "z-to-a":
        cards.sort()
        cards.reverse()
        sort = "Z to A"
      else:
        cards.reverse()
        sort = "Newest first"
      cards = " ".join(cards)
      return render_template("cards.html", cards=cards, username=username, sort=sort)
    else:
      return redirect("/logout")
  else:
    return redirect("/login")
  
@app.route("/<user>/<name>/edit")
def edit(user, name):
  username = request.cookies.get("username")
  if loggedIn():
    if checkUser():
      if user in db.keys():
        if name in db[user]["cards"].keys():
          contents = db[user]["cards"][name]
          return render_template("editor.html", contents=contents, cardname=name)
      return redirect("/")
    else:
      return redirect("/logout")
  else:
    return redirect("/")

@app.route("/<user>/<name>/view")
def view(user, name):
  if user in db.keys():
    if name in db[user]["cards"].keys():
      contents = db[user]["cards"][name]
      return render_template("viewcard.html", contents=contents)
  return redirect("/")

@app.route("/<user>/<name>/save", methods=["GET", "POST"])
def save(user, name):
  if request.method == "POST":
    username = request.cookies.get("username")
    if loggedIn():
      if checkUser():
        if user in db.keys():
          if user == username:
            if name in db[user]["cards"].keys():
              contents = request.json["contents"]
              db[user]["cards"][name] = contents
              return "Saved"
        return redirect("/")
      else:
        return redirect("/logout")
    else:
      return redirect("/")

@app.route("/<user>/<name>/rename", methods=["GET", "POST"])
def rename(user, name):
  if request.method == "POST":
    username = request.cookies.get("username")
    if loggedIn():
      if checkUser():
        if user in db.keys():
          if user == username:
            if name in db[user]["cards"].keys():
              newname = request.json["newname"]
              if newname not in db[user]["cards"].keys():
                contents = db[user]["cards"][name]
                del db[user]["cards"][name]
                db[user]["cards"][newname] = contents
                return "Renamed"
        return redirect("/")
      else:
        return redirect("/logout")
    else:
      return redirect("/")

@app.route("/<user>/<name>/delete", methods=["GET", "POST"])
def delete(user, name):
  if request.method == "POST":
    username = request.cookies.get("username")
    if loggedIn():
      if checkUser():
        if user in db.keys():
          if user == username:
            if name in db[user]["cards"].keys():
              del db[user]["cards"][name]
              return "Deleted"
        return redirect("/")
      else:
        return redirect("/logout")
    else:
      return redirect("/")

@app.route("/createnewcard", methods=["GET", "POST"])
def newcard():
  if request.method == "POST":
    username = request.cookies.get("username")
    user = request.json["user"]
    newcardname = request.json["newcardname"]
    if loggedIn():
      if checkUser():
        if user == username:
          if newcardname not in db[user]["cards"].keys():
            db[user]["cards"][newcardname] = '<div id="card"></div>'
            return "Saved"
          return redirect("/")
      else:
        return redirect("logout")
    else:
      return redirect("/")

@app.route("/help")
def help():
  if checkUser():
    return render_template("help.html", loggedIn=request.cookies.get("loggedIn"))
  return redirect("/logout")

@app.errorhandler(404)
def page_not_found(e):
  if checkUser():
    return render_template("404.html", loggedIn=request.cookies.get("loggedIn"))
  return redirect("/logout")

app.run(host="0.0.0.0", port=8080)