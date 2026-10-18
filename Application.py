"""
Blockchain-Simulation mit GUI
=============================
Starten:  python gui.py      (Datei liegt im selben Ordner wie main.py)

Drei Buttons, drei Szenarien. Jedes läuft Schritt für Schritt ab: erst wächst die
Kette eine Weile normal (Block für Block), und erst dann passiert das Besondere.

  NORMAL           Kette wächst, wird geprüft, dann fälscht jemand einen alten Block
  Double Spending  Alice will dieselben Coins zweimal ausgeben
  51% Attacke      Angreifer baut heimlich eine längere Kette und ersetzt die ehrliche

Jeder Block wird als Karte gezeichnet:
  - Kopf:           Blocknummer und Uhrzeit
  - Hash:           die führenden Nullen (grün) sind das Ergebnis des Minings
  - Vorher:         Hash des Vorgängers. Der Pfeil zeigt auf diesen Vorgänger.
  - Nonce:          so viele Versuche brauchte das Mining
  - Transaktionen:  der Inhalt des Blocks
  - goldener Rahmen = neuer Block, roter Rahmen = die Prüfung schlägt an

Die Logik (Block, Ledger, Blockchain) kommt unverändert aus main.py.
Bedienung: 'Weiter' / 'Zurück' (auch Leertaste und Pfeiltasten) gehen Schritt für Schritt
durch. 'Auto' läuft selbstständig weiter, Tempo mit dem Regler.

Aufbau des Codes: Jedes Szenario ist ein Generator. Jedes `yield frame(...)` ist ein
Schritt (Titel, Erklärtext, zu zeichnende Ketten). Die GUI zeigt den Schritt und ruft
nach einer Pause den nächsten auf.
"""

import copy
import io
import tkinter as tk
import tkinter.font as tkfont
from contextlib import redirect_stdout

from main import Blockchain

DIFFICULTY = 3         # 3 Nullen: schnell, aber die Nullen im Hash sind gut sichtbar
PAUSE_BLOCK = 750      # ms, wenn nur ein neuer Block erscheint
PAUSE_TEXT = 2300      # ms, wenn etwas erklärt wird

# Farben
BLAU, GRAU, ROT, GRUEN, GOLD = "#1f4e9c", "#6b7280", "#c62828", "#1a7f37", "#e0a800"
HINTERGRUND, KARTE, TEXT, ROT_HELL, RAND = "#f4f6fa", "#ffffff", "#1f2933", "#fdecea", "#c3cad5"

# Masse der Block-Karten
CARD_W, CARD_H = 214, 190
GAP, PAD = 46, 18
LABEL_H, ROW_GAP = 30, 24

PROBLEM_HASH = "Hash passt nicht zum Inhalt"
PROBLEM_LINK = "Verweis auf Vorgänger falsch"


# ---------------------------------------------------------------------------
# Bausteine für die Schritte
# ---------------------------------------------------------------------------
def z(text, tag="text"):
    """Eine Textzeile für das Infofeld. tag: text | gut (grün) | schlecht (rot)"""
    return (text, tag)


def frame(titel, text=(), rows=(), pause=PAUSE_TEXT, saldo=None):
    # deepcopy = Schnappschuss: Beim Zurückblättern soll der Zustand von damals
    # erscheinen, auch wenn ein Block später gefälscht wurde.
    return {"titel": titel, "text": list(text), "rows": copy.deepcopy(list(rows)),
            "pause": pause, "saldo": saldo}


def row(label, chain, neu=(), ghosts=(), gedimmt=False):
    """Eine Zeile mit Block-Karten. neu = Indizes, die golden umrandet werden."""
    return {"label": label, "chain": list(chain), "neu": set(neu),
            "ghosts": list(ghosts), "gedimmt": gedimmt}


def saldo_text(bc):
    return "Kontostände:   " + "   |   ".join(
        f"{name}: {betrag}" for name, betrag in bc.ledger.balances.items())


def ausgabe_von(funktion, *args):
    """Führt eine Funktion aus und fängt ihre print()-Ausgaben ab."""
    puffer = io.StringIO()
    with redirect_stdout(puffer):
        ergebnis = funktion(*args)
    meldungen = [m for m in puffer.getvalue().splitlines() if m.strip()]
    return ergebnis, meldungen


def probleme(chain, i):
    """Was stimmt bei Block i nicht? (genau die Prüfungen von is_chain_valid)"""
    if i == 0:
        return []
    block, vorgaenger = chain[i], chain[i - 1]
    gefunden = []
    if block.hash != block.calculate_hash():
        gefunden.append(PROBLEM_HASH)
    if block.previous_hash != vorgaenger.hash:
        gefunden.append(PROBLEM_LINK)
    return gefunden


def tx_zeilen(block):
    if block.index == 0:
        return ["(Startblock)"]
    zeilen = []
    for tx in block.transactions:
        text = f"{tx.sender} → {tx.receiver}: {tx.amount}"
        zeilen.append(text if len(text) <= 26 else text[:25] + "…")
    if len(zeilen) > 3:
        zeilen = zeilen[:2] + [f"+ {len(zeilen) - 2} weitere"]
    return zeilen or ["(leer)"]


# ---------------------------------------------------------------------------
# Zeichnen (nur Canvas-Befehle, deshalb auch ohne Fenster testbar)
# ---------------------------------------------------------------------------
def zeichne_block(c, fonts, x, y, block, fehler, neu, gedimmt):
    if fehler:
        rand, breite = ROT, 3
    elif neu:
        rand, breite = GOLD, 3
    else:
        rand, breite = RAND, 1
    extra = {"dash": (4, 3)} if gedimmt else {}
    c.create_rectangle(x, y, x + CARD_W, y + CARD_H, fill=KARTE, outline=rand,
                       width=breite, **extra)

    # Kopf
    if gedimmt:
        kopf = "#9aa5b5"
    elif fehler:
        kopf = ROT
    elif block.index == 0:
        kopf = GRAU
    else:
        kopf = BLAU
    c.create_rectangle(x, y, x + CARD_W, y + 26, fill=kopf, outline=kopf)
    name = "Genesis" if block.index == 0 else f"Block #{block.index}"
    c.create_text(x + 10, y + 13, text=name, anchor="w", font=fonts.fett, fill="white")
    c.create_text(x + CARD_W - 10, y + 13, text=block.dateandtime[:8], anchor="e",
                  font=fonts.klein, fill="white")

    lx = x + 10
    vx = lx + fonts.mono.measure("Vorher: ")

    # Hash: führende Nullen grün und fett (= das Ergebnis des Minings)
    y1 = y + 42
    c.create_text(lx, y1, text="Hash:", anchor="w", font=fonts.mono, fill=GRAU)
    h = block.hash[:12]
    nullen = len(h) - len(h.lstrip("0"))
    if nullen:
        c.create_text(vx, y1, text=h[:nullen], anchor="w", font=fonts.mono_fett, fill=GRUEN)
    c.create_text(vx + fonts.mono_fett.measure(h[:nullen]), y1, text=h[nullen:] + "…",
                  anchor="w", font=fonts.mono, fill=TEXT)

    # Hash des Vorgängers
    y2 = y + 60
    link_kaputt = PROBLEM_LINK in fehler
    c.create_text(lx, y2, text="Vorher:", anchor="w", font=fonts.mono, fill=GRAU)
    vorher = "–" if block.index == 0 else block.previous_hash[:12] + "…"
    c.create_text(vx, y2, text=vorher, anchor="w", font=fonts.mono,
                  fill=ROT if link_kaputt else TEXT)

    # Nonce
    y3 = y + 78
    c.create_text(lx, y3, text="Nonce:", anchor="w", font=fonts.mono, fill=GRAU)
    c.create_text(vx, y3, text=str(block.nonce), anchor="w", font=fonts.mono, fill=TEXT)

    # Transaktionen
    c.create_line(x + 8, y + 94, x + CARD_W - 8, y + 94, fill="#e2e6ee")
    c.create_text(lx, y + 106, text="Transaktionen:", anchor="w", font=fonts.mono_fett,
                  fill=TEXT)
    for n, zeile in enumerate(tx_zeilen(block)):
        c.create_text(lx, y + 124 + n * 16, text=zeile, anchor="w", font=fonts.mono,
                      fill=TEXT)

    # Fehlerband
    if fehler:
        c.create_rectangle(x + 3, y + CARD_H - 26, x + CARD_W - 3, y + CARD_H - 3,
                           fill=ROT_HELL, outline="")
        c.create_text(x + CARD_W / 2, y + CARD_H - 14, text="✗ " + fehler[0],
                      anchor="center", font=fonts.klein, fill=ROT)


def zeichne_abgelehnt(c, fonts, x, y, tx_text, grund):
    hoehe = 108
    c.create_rectangle(x, y, x + CARD_W, y + hoehe, fill=ROT_HELL, outline=ROT,
                       width=2, dash=(5, 3))
    c.create_text(x + 10, y + 16, text="ABGELEHNT", anchor="w", font=fonts.fett, fill=ROT)
    c.create_text(x + 10, y + 44, text=tx_text, anchor="w", font=fonts.mono, fill=TEXT)
    c.create_text(x + 10, y + 68, text=grund, anchor="w", font=fonts.klein, fill=ROT)
    c.create_text(x + 10, y + 88, text="kommt nicht in den Block", anchor="w",
                  font=fonts.klein, fill=GRAU)


def zeichne(c, fonts, rows):
    """Zeichnet alle Zeilen. Gibt (Breite, Höhe) der gesamten Zeichnung zurück."""
    c.delete("all")
    breite, y = 0, PAD
    for r in rows:
        c.create_text(PAD, y + 4, text=r["label"], anchor="nw", font=fonts.fett, fill=TEXT)
        oben = y + LABEL_H
        chain = r["chain"]
        x = PAD
        for i, block in enumerate(chain):
            fehler = [] if r["gedimmt"] else probleme(chain, i)
            if i > 0:
                # Pfeil zeigt vom Block auf seinen Vorgänger
                c.create_line(x, oben + 13, x - GAP, oben + 13, arrow="last", width=2,
                              fill=ROT if PROBLEM_LINK in fehler else GRAU)
            zeichne_block(c, fonts, x, oben, block, fehler, i in r["neu"], r["gedimmt"])
            x += CARD_W + GAP
        for tx_text, grund in r["ghosts"]:
            c.create_line(x, oben + 13, x - GAP, oben + 13, arrow="last", width=2,
                          fill=ROT, dash=(4, 3))
            zeichne_abgelehnt(c, fonts, x, oben, tx_text, grund)
            x += CARD_W + GAP
        breite = max(breite, x)
        y = oben + CARD_H + ROW_GAP
    c.configure(scrollregion=(0, 0, breite + PAD, y))
    return breite, y


# ---------------------------------------------------------------------------
# Szenario 1: NORMAL
# ---------------------------------------------------------------------------
def szenario_normal():
    bc = Blockchain()
    for name, betrag in [("Alice", 20), ("Bob", 10), ("Charlie", 5), ("Dana", 0)]:
        bc.add_account(name, betrag)
    yield frame("1) Normale Blockchain",
                [z("Startguthaben sind festgelegt, die Kette besteht erst aus dem Genesis-Block."),
                 z("Gleich werden nacheinander Blöcke gemined und angehängt.")],
                [row("Kette", bc.chain)], saldo=saldo_text(bc))

    bloecke = [
        [("Alice", "Bob", 5)],
        [("Bob", "Charlie", 3)],
        [("Charlie", "Dana", 4)],
        [("Alice", "Dana", 6), ("Bob", "Alice", 2)],
        [("Dana", "Bob", 5)],
        [("Alice", "Charlie", 3)],
    ]
    erklaerung = {
        1: "Die grünen Nullen am Anfang des Hashs sind das Ergebnis des Minings "
           "(Proof-of-Work). Die Nonce zeigt, wie viele Versuche nötig waren.",
        2: "'Vorher' ist der Hash des Vorgängers. Der Pfeil zeigt auf den Block, "
           "auf den sich dieser Block bezieht. So entsteht die Kette.",
    }
    for nr, daten in enumerate(bloecke, 1):
        bc.new_block(daten, DIFFICULTY)
        block = bc.chain[-1]
        text = erklaerung.get(nr, f"Block {nr} wurde nach {block.nonce} Versuchen gemined.")
        yield frame(f"2) Die Kette wächst: Block {nr} von {len(bloecke)}", [z(text)],
                    [row("Kette", bc.chain, neu={nr})],
                    pause=PAUSE_TEXT if nr in erklaerung else PAUSE_BLOCK,
                    saldo=saldo_text(bc))

    gueltig = bc.is_chain_valid()
    yield frame("3) Prüfung der Kette",
                [z(f"Ist die Kette gültig? {'JA' if gueltig else 'NEIN'}",
                   "gut" if gueltig else "schlecht"),
                 z("Jetzt versucht jemand, einen alten Block nachträglich zu verändern.")],
                [row("Kette", bc.chain)], saldo=saldo_text(bc))

    ziel = bc.chain[2]
    alter_betrag = ziel.transactions[0].amount
    ziel.transactions[0].amount = 300
    if bc.is_chain_valid():
        yield frame("4) Fälschung von Block 2",
                    [z("ACHTUNG: Die Fälschung wurde NICHT erkannt.", "schlecht"),
                     z("Der Hash eines Blocks muss vom Inhalt seiner Transaktionen abhängen. "
                       "Das ist noch ein Fehler in main.py (siehe test_blockchain.py).",
                       "schlecht")],
                    [row("Kette (gefälscht)", bc.chain)], saldo=saldo_text(bc))
        return
    yield frame(f"4) Jemand fälscht Block 2: aus {alter_betrag} wird 300",
                [z("Die Prüfung schlägt sofort an: Der gespeicherte Hash passt nicht mehr "
                   "zum veränderten Inhalt.", "gut")],
                [row("Kette (gefälscht)", bc.chain)], saldo=saldo_text(bc))

    ziel.hash = ziel.calculate_hash()
    yield frame("5) Der Fälscher berechnet den Hash von Block 2 neu",
                [z("Block 2 passt jetzt wieder zu sich selbst, aber:"),
                 z("• sein Hash beginnt nicht mehr mit Nullen (er wurde nicht gemined)",
                   "schlecht"),
                 z("• Block 3 verweist noch auf den alten Hash von Block 2", "schlecht"),
                 z("Er müsste alle folgenden Blöcke neu minen und dabei schneller sein als "
                   "der Rest des Netzwerks.")],
                [row("Kette (gefälscht)", bc.chain)], pause=PAUSE_TEXT * 1.6,
                saldo=saldo_text(bc))

    gueltig = bc.is_chain_valid()
    yield frame("6) Ergebnis",
                [z(f"Ist die Kette gültig? {'JA' if gueltig else 'NEIN'}",
                   "schlecht" if gueltig else "gut"),
                 z("Eine nachträgliche Änderung bricht die Kette ab dieser Stelle. Deshalb ist "
                   "eine Blockchain fälschungssicher.")],
                [row("Kette (gefälscht)", bc.chain)], saldo=saldo_text(bc))


# ---------------------------------------------------------------------------
# Szenario 2: DOUBLE SPENDING
# ---------------------------------------------------------------------------
def szenario_double_spending():
    bc = Blockchain()
    for name, betrag in [("Alice", 10), ("Bob", 5), ("Charlie", 0), ("Dana", 0)]:
        bc.add_account(name, betrag)
    yield frame("1) Double Spending",
                [z("Zuerst läuft die Kette ganz normal, mit ehrlichen Zahlungen.")],
                [row("Kette", bc.chain)], saldo=saldo_text(bc))

    fueller = [
        [("Bob", "Charlie", 2)],
        [("Alice", "Dana", 1)],
        [("Charlie", "Dana", 1), ("Dana", "Bob", 1)],
        [("Bob", "Alice", 2)],
        [("Dana", "Charlie", 1)],
    ]
    for nr, daten in enumerate(fueller, 1):
        bc.new_block(daten, DIFFICULTY)
        yield frame(f"2) Die Kette wächst: Block {nr} von {len(fueller)}",
                    [z(f"Block {nr} wurde nach {bc.chain[-1].nonce} Versuchen gemined.")],
                    [row("Kette", bc.chain, neu={nr})], pause=PAUSE_BLOCK,
                    saldo=saldo_text(bc))

    betrag = bc.ledger.balances["Alice"]
    yield frame(f"3) Alice besitzt {betrag}",
                [z(f"Alice versucht, diese {betrag} gleichzeitig an Bob UND an Charlie zu "
                   "schicken.", "schlecht"),
                 z("Beide Zahlungen warten auf den nächsten Block.")],
                [row("Kette", bc.chain)], saldo=saldo_text(bc))

    versuch = [("Alice", "Bob", betrag), ("Alice", "Charlie", betrag)]
    _, meldungen = ausgabe_von(bc.new_block, versuch, DIFFICULTY)
    angenommen = {(tx.sender, tx.receiver, tx.amount) for tx in bc.chain[-1].transactions}
    abgelehnt = [t for t in versuch if t not in angenommen]
    gruende = [m.split(" - ")[-1] for m in meldungen]
    ghosts = [(f"{s} → {r}: {a}", gruende[i] if i < len(gruende) else "abgelehnt")
              for i, (s, r, a) in enumerate(abgelehnt)]
    yield frame("4) Das System prüft jede Zahlung der Reihe nach",
                [z("Die erste Zahlung wird angenommen und sofort gebucht.", "gut"),
                 z("Danach hat Alice 0. Die zweite Zahlung scheitert.", "schlecht")],
                [row("Kette", bc.chain, neu={len(bc.chain) - 1}, ghosts=ghosts)],
                saldo=saldo_text(bc))

    gueltig = bc.is_chain_valid()
    yield frame("5) Ergebnis",
                [z("Double Spending verhindert: Dieselben Coins wurden nur einmal ausgegeben.",
                   "gut"),
                 z("Das Ledger vergleicht jede Zahlung mit dem aktuellen Kontostand, bevor sie "
                   "in einen Block darf."),
                 z(f"Ist die Kette gültig? {'JA' if gueltig else 'NEIN'}",
                   "gut" if gueltig else "schlecht")],
                [row("Kette", bc.chain, ghosts=ghosts)], saldo=saldo_text(bc))


# ---------------------------------------------------------------------------
# Szenario 3: 51%-ATTACKE
# ---------------------------------------------------------------------------
def szenario_51():
    bc = Blockchain()
    for name, betrag in [("Alice", 10), ("Alice2", 0), ("Bob", 5), ("Händler", 0),
                         ("Dana", 0)]:
        bc.add_account(name, betrag)
    yield frame("1) Ausgangslage",
                [z("Alle Teilnehmer haben dieselbe Kette. Alice ist die spätere Angreiferin, "
                   "Alice2 ist ihr zweites Konto.")],
                [row("Gemeinsame Kette", bc.chain)], saldo=saldo_text(bc))

    gemeinsam = [
        [("Bob", "Dana", 2)],
        [("Alice", "Bob", 1)],
        [("Dana", "Bob", 1)],
        [("Bob", "Dana", 1)],
    ]
    for nr, daten in enumerate(gemeinsam, 1):
        bc.new_block(daten, DIFFICULTY)
        yield frame(f"2) Die Kette wächst: Block {nr} von {len(gemeinsam)}",
                    [z(f"Block {nr} wurde nach {bc.chain[-1].nonce} Versuchen gemined.")],
                    [row("Gemeinsame Kette", bc.chain, neu={nr})], pause=PAUSE_BLOCK,
                    saldo=saldo_text(bc))

    angreifer = bc.fork()
    yield frame("3) Der Angreifer kopiert die Kette (Fork)",
                [z("Alice kontrolliert mehr als 50% der Rechenleistung."),
                 z("Ab jetzt mined sie heimlich eine eigene Kette (untere Zeile).",
                   "schlecht")],
                [row("Ehrliche Kette (Netzwerk)", bc.chain),
                 row("Kette des Angreifers (geheim)", angreifer.chain)],
                saldo=saldo_text(bc))

    def rennen(titel, text, neu_ehrlich=(), neu_angreifer=()):
        return frame(titel, text,
                     [row("Ehrliche Kette (Netzwerk)", bc.chain, neu=neu_ehrlich),
                      row("Kette des Angreifers (geheim)", angreifer.chain,
                          neu=neu_angreifer)],
                     pause=PAUSE_TEXT, saldo=saldo_text(bc))

    bc.new_block([("Alice", "Händler", 3)], DIFFICULTY)
    n = len(bc.chain) - 1
    yield rennen("4) Alice bezahlt den Händler (ehrliche Kette)",
                 [z("Der Händler sieht die Zahlung von 3 im Netzwerk.")], neu_ehrlich={n})

    angreifer.new_block([("Alice", "Alice2", 3)], DIFFICULTY)
    yield rennen("5) Heimlich: Alice schickt dieselben 3 an sich selbst (Alice2)",
                 [z("Das passiert nur in der geheimen Kette. Das Netzwerk sieht nichts davon.",
                    "schlecht")], neu_angreifer={n})

    bc.new_block([("Bob", "Dana", 1)], DIFFICULTY)
    yield rennen("6) Die ehrliche Kette wächst weiter",
                 [z("Der Händler sieht seine Zahlung zweifach bestätigt und liefert die Ware.")],
                 neu_ehrlich={n + 1})

    angreifer.new_block([("Bob", "Dana", 2)], DIFFICULTY)
    yield rennen("7) Der Angreifer mined weiter", [z("Noch ist seine Kette nicht länger.")],
                 neu_angreifer={n + 1})

    angreifer.new_block([("Alice2", "Dana", 1)], DIFFICULTY)
    yield rennen("8) Der Angreifer überholt die ehrliche Kette",
                 [z(f"Ehrliche Kette: {len(bc.chain)} Blöcke    "
                    f"Angreifer: {len(angreifer.chain)} Blöcke", "schlecht"),
                  z("Mit mehr als 50% der Rechenleistung schafft er mehr Blöcke als alle "
                    "anderen zusammen.")], neu_angreifer={n + 2})

    alt = list(bc.chain)
    erfolg, meldungen = ausgabe_von(bc.receive_chain, angreifer)
    if not erfolg:
        yield frame("9) Angriff abgelehnt",
                    [z("Die Kette des Angreifers wurde nicht übernommen:", "schlecht")] +
                    [z(f"  {m}", "schlecht") for m in meldungen] +
                    [z("Laut Plan sollte sie gültig sein, also liegt ein Fehler in main.py "
                       "vor (siehe test_fork_is_valid_copy in test_blockchain.py).",
                       "schlecht")],
                    [row("Ehrliche Kette (Netzwerk)", bc.chain),
                     row("Kette des Angreifers", angreifer.chain)], saldo=saldo_text(bc))
        return

    yield frame("9) Der Angreifer veröffentlicht seine Kette",
                [z("Regel: Die längste gültige Kette gewinnt."),
                 z("Das Netzwerk wechselt zur Kette des Angreifers.", "schlecht")],
                [row("Netzwerk (jetzt die Kette des Angreifers)", bc.chain),
                 row("Verworfen: die bisherige ehrliche Kette (Händlers Zahlung steckt hier)",
                     alt, gedimmt=True)],
                saldo=saldo_text(bc))

    yield frame("10) Ergebnis",
                [z(f"Der Händler hat jetzt {bc.ledger.balances.get('Händler', 0)}. "
                   "Seine Zahlung ist rückwirkend verschwunden.", "schlecht"),
                 z("Alice hat die Ware UND ihre Coins (jetzt auf Alice2): Double Spending "
                   "durch eine 51%-Attacke.", "schlecht")],
                [row("Netzwerk", bc.chain)], saldo=saldo_text(bc))


# ---------------------------------------------------------------------------
# Fenster
# ---------------------------------------------------------------------------
class Fonts:
    def __init__(self):
        fest = tkfont.nametofont("TkFixedFont")
        normal = tkfont.nametofont("TkDefaultFont")
        self.mono = fest.copy()
        self.mono.configure(size=9)
        self.mono_fett = fest.copy()
        self.mono_fett.configure(size=9, weight="bold")
        self.fett = normal.copy()
        self.fett.configure(size=10, weight="bold")
        self.klein = normal.copy()
        self.klein.configure(size=8)
        self.titel = normal.copy()
        self.titel.configure(size=12, weight="bold")
        self.normal = normal.copy()
        self.normal.configure(size=10)


class App:
    def __init__(self, root):
        self.root = root
        self.generator = None
        self.verlauf = []      # alle bisher gezeigten Schritte
        self.pos = -1          # welcher Schritt gerade angezeigt wird
        self.ende = False
        self.timer = None      # läuft nur im Auto-Modus
        root.title("Blockchain-Simulation")
        root.geometry("1150x780")
        root.configure(bg=HINTERGRUND)
        self.fonts = Fonts()

        oben = tk.Frame(root, bg=HINTERGRUND)
        oben.pack(fill="x", padx=12, pady=(12, 6))
        for text, szenario in [("NORMAL", szenario_normal),
                               ("Double Spending", szenario_double_spending),
                               ("51% Attacke", szenario_51)]:
            tk.Button(oben, text=text, width=18, height=2,
                      command=lambda s=szenario: self.starte(s)).pack(side="left", padx=(0, 8))

        nav = tk.Frame(root, bg=HINTERGRUND)
        nav.pack(fill="x", padx=12, pady=(0, 6))
        self.b_zurueck = tk.Button(nav, text="◀ Zurück", width=12, command=self.zurueck,
                                   state="disabled")
        self.b_zurueck.pack(side="left", padx=(0, 8))
        self.b_weiter = tk.Button(nav, text="Weiter ▶", width=12, command=self.weiter,
                                  state="disabled")
        self.b_weiter.pack(side="left", padx=(0, 8))
        self.b_auto = tk.Button(nav, text="▶ Auto", width=10, command=self.auto_umschalten,
                                state="disabled")
        self.b_auto.pack(side="left", padx=(0, 8))
        self.schritt = tk.Label(nav, text="", bg=HINTERGRUND, fg=GRAU, width=10, anchor="w")
        self.schritt.pack(side="left", padx=(8, 0))
        tk.Label(nav, text="Auto-Tempo", bg=HINTERGRUND).pack(side="left", padx=(20, 4))
        self.tempo = tk.Scale(nav, from_=0.3, to=3.0, resolution=0.1, orient="horizontal",
                              length=150, bg=HINTERGRUND, highlightthickness=0)
        self.tempo.set(0.7)
        self.tempo.pack(side="left")
        # Tastatur: Pfeile oder Leertaste
        root.bind("<Right>", lambda e: self.weiter())
        root.bind("<space>", lambda e: self.weiter())
        root.bind("<Left>", lambda e: self.zurueck())

        self.info = tk.Text(root, height=6, wrap="word", state="disabled", relief="flat",
                            padx=12, pady=8, font=self.fonts.normal)
        self.info.pack(fill="x", padx=12)
        self.info.tag_configure("titel", font=self.fonts.titel, foreground=BLAU)
        self.info.tag_configure("gut", foreground=GRUEN)
        self.info.tag_configure("schlecht", foreground=ROT)

        mitte = tk.Frame(root)
        mitte.pack(fill="both", expand=True, padx=12, pady=8)
        self.canvas = tk.Canvas(mitte, bg=HINTERGRUND, highlightthickness=1,
                                highlightbackground=RAND, xscrollincrement=40,
                                yscrollincrement=20)
        sx = tk.Scrollbar(mitte, orient="horizontal", command=self.canvas.xview)
        sy = tk.Scrollbar(mitte, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.pack(side="bottom", fill="x")
        sy.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            -3 if e.delta > 0 else 3, "units"))
        self.canvas.bind("<Shift-MouseWheel>", lambda e: self.canvas.xview_scroll(
            -3 if e.delta > 0 else 3, "units"))

        self.saldo = tk.Label(root, anchor="w", font=self.fonts.fett, bg=HINTERGRUND)
        self.saldo.pack(fill="x", padx=14)
        tk.Label(root, anchor="w", bg=HINTERGRUND, fg=GRAU, font=self.fonts.klein,
                 text="Pfeil: Block verweist auf den Hash seines Vorgängers   |   grüne Nullen: "
                      "Proof-of-Work   |   goldener Rahmen: neuer Block   |   roter Rahmen: "
                      "Prüfung schlägt an").pack(fill="x", padx=14, pady=(0, 8))

        self.zeige(frame("Wähle ein Szenario.",
                         [z("Danach gehst du mit 'Weiter' (oder Leertaste / Pfeiltasten) Schritt "
                            "für Schritt durch. So hast du so viel Zeit zum Lesen, wie du willst."),
                          z("Die Kette läuft zuerst eine Weile normal, danach passiert etwas."),
                          z("Mit 'Auto' läuft es von selbst weiter, Tempo einstellbar.")]))

    def zeige(self, f):
        self.info.configure(state="normal")
        self.info.delete("1.0", "end")
        self.info.insert("end", f["titel"] + "\n", "titel")
        for text, tag in f["text"]:
            self.info.insert("end", text + "\n", tag)
        self.info.configure(state="disabled")
        self.saldo.configure(text=f["saldo"] or "")
        breite, _ = zeichne(self.canvas, self.fonts, f["rows"])
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(1.0 if breite > self.canvas.winfo_width() else 0)

    # --- Steuerung: Weiter / Zurück / Auto -----------------------------------
    def starte(self, szenario):
        self.stoppe_auto()
        self.generator = szenario()
        self.verlauf, self.pos, self.ende = [], -1, False
        self.vor()

    def vor(self):
        """Zeigt den nächsten Schritt. Gibt True zurück, wenn es einen gab."""
        if self.generator is None:
            return False
        if self.pos + 1 < len(self.verlauf):          # schon gesehen (nach Zurück)
            self.pos += 1
        else:
            try:
                f = next(self.generator)
            except StopIteration:
                self.ende = True
                self.aktualisiere_knoepfe()
                return False
            except Exception as fehler:
                self.ende = True
                self.zeige(frame("Fehler im Szenario", [z(repr(fehler), "schlecht")]))
                self.aktualisiere_knoepfe()
                return False
            self.verlauf.append(f)
            self.pos += 1
        self.zeige(self.verlauf[self.pos])
        self.aktualisiere_knoepfe()
        return True

    def weiter(self):
        self.stoppe_auto()
        self.vor()

    def zurueck(self):
        self.stoppe_auto()
        if self.pos > 0:
            self.pos -= 1
            self.zeige(self.verlauf[self.pos])
        self.aktualisiere_knoepfe()

    def auto_umschalten(self):
        if self.timer is not None:
            self.stoppe_auto()
        elif self.generator is not None:
            self.plane_auto()
        self.aktualisiere_knoepfe()

    def plane_auto(self):
        pause = self.verlauf[self.pos]["pause"] if self.pos >= 0 else 1000
        self.timer = self.root.after(int(pause / self.tempo.get()), self.auto_schritt)

    def auto_schritt(self):
        self.timer = None
        if self.vor():
            self.plane_auto()
        self.aktualisiere_knoepfe()

    def stoppe_auto(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def aktualisiere_knoepfe(self):
        am_ende = self.ende and self.pos >= len(self.verlauf) - 1
        aktiv = self.generator is not None
        self.b_zurueck.configure(state="normal" if self.pos > 0 else "disabled")
        self.b_weiter.configure(state="normal" if aktiv and not am_ende else "disabled")
        self.b_auto.configure(state="normal" if aktiv and not am_ende else "disabled",
                              text="⏸ Pause" if self.timer is not None else "▶ Auto")
        self.schritt.configure(text=f"Schritt {self.pos + 1}" if self.pos >= 0 else "")


if __name__ == "__main__":
    fenster = tk.Tk()
    App(fenster)
    fenster.mainloop()