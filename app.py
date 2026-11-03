
import os
import random
import unicodedata
import difflib

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clau-local-canvia-la")

def normalitza(text):
    text = unicodedata.normalize("NFD", text.lower().strip())
    return "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

def carrega_jugadors():
    jugadors = []
    ruta = os.path.join(os.path.dirname(__file__), "jugadors_joc.txt")

    with open(ruta, encoding="utf-8") as fitxer:
        for linia in fitxer:
            print(linia)
            dades = [
                d.strip()
                for d in linia.strip()
                .replace("–", ";")
                .replace("-", ";")
                .split(";")
            ]

            if len(dades) != 5:
                continue

            nom, posicio, edat, club, pais = dades

            try:
                edat = int(edat)
            except ValueError:
                continue

            jugadors.append({
                "nom": nom,
                "nom_norm": normalitza(nom),
                "posicio": posicio,
                "edat": edat,
                "club": club,
                "pais": pais
            })

    return jugadors

JUGADORS = carrega_jugadors()

def nova_partida():
    session.clear()
    session["secret"] = random.randrange(len(JUGADORS))
    session["intents"] = 0
    session["resultats"] = []
    session["estat"] = "jugant"
    session["missatge"] = ""

@app.route("/")
def inici():
    if not JUGADORS:
        return "No hi ha futbolistes vàlids a jugadors_joc.txt.", 500

    if "secret" not in session:
        nova_partida()

    return render_template(
        "index.html",
        intents=session["intents"],
        resultats=session["resultats"],
        estat=session["estat"],
        missatge=session.get("missatge", ""),
        secret=JUGADORS[session["secret"]]
    )

@app.route("/endevinar", methods=["POST"])
def endevinar():
    if not JUGADORS:
        return "No hi ha futbolistes carregats.", 500

    if "secret" not in session:
        nova_partida()

    if session["estat"] != "jugant":
        return redirect(url_for("inici"))

    entrada = normalitza(request.form.get("jugador", ""))

    if not entrada:
        session["missatge"] = "Escriu el nom d'un futbolista."
        return redirect(url_for("inici"))

    trobat = next(
        (
            j for j in JUGADORS
            if entrada == j["nom_norm"]
            or entrada in j["nom_norm"].split()
        ),
        None
    )

    if trobat is None:
        coincidencies = difflib.get_close_matches(
            entrada,
            [j["nom_norm"] for j in JUGADORS],
            n=1,
            cutoff=0.6
        )

        if coincidencies:
            suggerit = next(
                j["nom"] for j in JUGADORS
                if j["nom_norm"] == coincidencies[0]
            )
            session["missatge"] = (
                f"No s'ha trobat el jugador. "
                f"Potser volies dir {suggerit}?"
            )
        else:
            session["missatge"] = "Jugador no trobat. Torna-ho a provar."

        return redirect(url_for("inici"))

    secret = JUGADORS[session["secret"]]

    session["missatge"] = ""
    session["intents"] += 1

    if trobat["nom_norm"] == secret["nom_norm"]:
        session["estat"] = "guanyat"
        session["missatge"] = (
            f"Has encertat! Era {secret['nom']}. "
            f"Intents utilitzats: {session['intents']}."
        )
        return redirect(url_for("inici"))

    pistes = {
        "club": trobat["club"] == secret["club"],
        "pais": trobat["pais"] == secret["pais"],
        "posicio": trobat["posicio"] == secret["posicio"],
        "edat": (
            "igual" if trobat["edat"] == secret["edat"]
            else "mes_gran" if trobat["edat"] < secret["edat"]
            else "mes_jove"
        )
    }

    resultats = session["resultats"]
    resultats.insert(0, {
        "nom": trobat["nom"],
        "pistes": pistes
    })
    session["resultats"] = resultats

    if session["intents"] >= 8:
        session["estat"] = "perdut"
        session["missatge"] = (
            f"S'han acabat els intents. "
            f"El jugador secret era {secret['nom']}."
        )

    return redirect(url_for("inici"))

@app.route("/nova")
def nova():
    nova_partida()
    return redirect(url_for("inici"))

if __name__ == "__main__":
    app.run(debug=True)

