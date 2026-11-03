import os
import random
import unicodedata
import difflib

jugadors = []

def normalitza(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def busca_jugador(entrada):
    for j in jugadors:
        if entrada == j["nom_norm"]:
            return j
        if entrada in j["nom_norm"].split():
            return j
    return None


def suggereix_jugador(entrada_raw):
    entrada_norm = normalitza(entrada_raw)

    noms_norm = [j["nom_norm"] for j in jugadors]

    coincidencies = difflib.get_close_matches(
        entrada_norm,
        noms_norm,
        n=1,
        cutoff=0.6
    )

    if coincidencies:
        for j in jugadors:
            if j["nom_norm"] == coincidencies[0]:
                return j["nom"]
    return None



ruta = os.path.join(os.path.dirname(__file__), "jugadors_joc.txt")

with open(ruta, "r", encoding="utf-8") as f:
    for linia in f:
        linia = linia.strip()
        if not linia:
            continue

        dades = linia.replace("–", ";").replace("-", ";").split(";")
        dades = [d.strip() for d in dades]

        if len(dades) != 6:
            continue

        nom, posicio, edat, club, Lliga, pais = dades

        try:
            edat = int(edat)
        except:
            continue

        jugadors.append({
            "nom": nom,
            "nom_norm": normalitza(nom),
            "posicio": posicio,
            "edat": edat,
            "club": club,
            "Lliga": Lliga,
            "pais": pais
        })


if not jugadors:
    print(" No s'han carregat jugadors")
    exit()



def jugar():
    secret = random.choice(jugadors)
    intents = 0

    print("Endevina el jugador!")
    print("Pots escriure nom o cognom.")
    print("Tens 8 intents.")
    print("Si en algun moment et vols rendir, escriu 'rendit' i et revelarem el jugador secret")

    while intents < 8:

        entrada_raw = input(f"Intent {intents + 1}: ")

        if entrada_raw.lower().strip() == "rendit":
            print("T'has rendit! Tant complicat era?!?")
            print(f"El jugador secret era: {secret['nom']}")
            return

        entrada = normalitza(entrada_raw)

        trobat = busca_jugador(entrada)

        if not trobat:
            suggerit = suggereix_jugador(entrada_raw)

            print("Jugador no trobat.")

            if suggerit:
                resposta = input(f"Vols dir {suggerit}? (s/n): ")

                if resposta.lower() == "s":
                    entrada = normalitza(suggerit)
                    trobat = busca_jugador(entrada)
                else:
                    continue
            else:
                continue

        if trobat["nom_norm"] == secret["nom_norm"]:
            print("HAS ENCERTAT!")
            print(f"Era: {secret['nom']}")
            print(f"En {intents + 1} intents!")
            return

        intents += 1

        print(f"Has triat: {trobat['nom']}")
        print("Pistes:")

        print("✅ Mateix club" if trobat["club"] == secret["club"] else "❌ Club diferent")
        print("✅ Mateix país" if trobat["pais"] == secret["pais"] else "❌ País diferent")
        print("✅ Mateixa posició" if trobat["posicio"] == secret["posicio"] else "❌ Posició diferent")
        print("✅ Mateixa lliga" if trobat["Lliga"] == secret["Lliga"] else "❌ Lliga diferent")

        if trobat["edat"] < secret["edat"]:
            print("⬆️ Més gran")
        elif trobat["edat"] > secret["edat"]:
            print("⬇️ Més jove")
        else:
            print("✅ Mateixa edat")

        print()

    print(f"Has perdut. Era: {secret['nom']}")

def menu():

    while True:
        print("========================")
        print("Adivina el jugador!")
        print("========================")
        print("1. Jugar")
        print("2. Normes")
        print("3. Sortir")

        opcio = input("Escull una opció: ")

        if opcio == "1":
            jugar()

        elif opcio == "2":
            print("NORMES DEL JOC:")
            print("Benvingut al joc d’endevinar el jugador secret!")
            print("- Has d’endevinar el jugador secret")
            print("- Pots escriure nom o cognom")
            print("- Tens 8 intents")
            print("- Si en algun moment et vols rendir, escriu 'rendit' i et revelarem el jugador secret")
            print("- El joc et dona pistes (club, país, posició,Lliga, edat)")

        elif opcio == "3":
            print("Adeu!")
            break

        else:
            print("Opció no vàlida")



menu()