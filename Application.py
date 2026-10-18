"""
Einfache GUI für die Blockchain-Simulation
==========================================
Starten:  python gui.py      (Datei liegt im selben Ordner wie main.py)

Drei Buttons, drei Szenarien. Jedes Szenario läuft Schritt für Schritt ab
(alle ~1.2 Sekunden erscheint der nächste Schritt) und erklärt, was gerade passiert.

  NORMAL           Kette aufbauen, prüfen, danach eine Fälschung erkennen
  Double Spending  Alice will dieselben 10 zweimal ausgeben
  51% Attacke      Angreifer baut heimlich eine längere Kette und ersetzt die ehrliche

Aufbau: Jedes Szenario ist ein "Generator". Jedes `yield` ist ein Schritt, der
angezeigt wird. Die GUI ruft nach einer Pause den nächsten Schritt auf.
Die ganze Logik (Block, Ledger, Blockchain) kommt unverändert aus main.py.
"""

import io
import tkinter as tk
import tkinter.font as tkfont
from contextlib import redirect_stdout
from tkinter import scrolledtext

from main import Blockchain

DIFFICULTY = 3          # 3 Nullen: schnell, aber die Nullen im Hash sind gut sichtbar
SCHRITT_PAUSE_MS = 1200


# ---------------------------------------------------------------------------
# Hilfsfunktionen: bauen die Textzeilen für die Anzeige
# Eine Zeile ist immer (text, tag). Der Tag bestimmt Farbe/Schrift.
# ---------------------------------------------------------------------------
def z(text, tag="text"):
    return (text, tag)


def kette_zeilen(bc, titel):
    zeilen = [z(f"{titel} ({len(bc.chain)} Blöcke)", "titel")]
    for block in bc.chain:
        inhalt = "; ".join(str(tx) for tx in block.transactions) or "(keine Transaktionen)"
        zeilen.append(z(
            f"  Block {block.index} | Hash {block.hash[:12]}... | "
            f"Nonce {block.nonce:>5} | {inhalt}"
        ))
    return zeilen


def stand_zeile(bc):
    teile = ", ".join(f"{name} {betrag}" for name, betrag in bc.ledger.balances.items())
    return z("Kontostände: " + teile)


def ausgabe_von(funktion, *args):
    """Führt eine Funktion aus und fängt ihre print()-Ausgaben ab (z.B. 'Fehler: ...')."""
    puffer = io.StringIO()
    with redirect_stdout(puffer):
        ergebnis = funktion(*args)
    meldungen = [m for m in puffer.getvalue().splitlines() if m.strip()]
    return ergebnis, meldungen


# ---------------------------------------------------------------------------
# Szenario 1: NORMAL
# ---------------------------------------------------------------------------
def szenario_normal():
    bc = Blockchain()
    bc.add_account("Alice", 10)
    bc.add_account("Bob", 0)
    bc.add_account("Charlie", 0)
    yield [z("1) Normale Blockchain", "titel"),
           z("Startguthaben festgelegt. Die Kette besteht nur aus dem Genesis-Block."),
           stand_zeile(bc)] + kette_zeilen(bc, "Kette")

    bc.new_block([("Alice", "Bob", 5)], DIFFICULTY)
    yield [z("2) Alice schickt Bob 5.", "titel"),
           z("Der Block wird gemined: der Hash beginnt mit Nullen. Die Nonce zeigt,"),
           z("wie oft probiert werden musste (Proof-of-Work)."),
           stand_zeile(bc)] + kette_zeilen(bc, "Kette")

    bc.new_block([("Bob", "Charlie", 2)], DIFFICULTY)
    yield [z("3) Bob schickt Charlie 2.", "titel"),
           z("Jeder Block enthält den Hash seines Vorgängers. So entsteht die Kette."),
           stand_zeile(bc)] + kette_zeilen(bc, "Kette")

    yield [z("4) Kette prüfen", "titel"),
           z(f"Ist die Kette gültig? {'JA' if bc.is_chain_valid() else 'NEIN'}", "gut")]

    bc.chain[1].transactions[0].amount = 500
    yield [z("5) Jemand fälscht Block 1 nachträglich: aus 5 wird 500.", "titel")] + \
          kette_zeilen(bc, "Gefälschte Kette")

    if bc.is_chain_valid():
        yield [z("6) Kette erneut prüfen", "titel"),
               z("Ist die Kette gültig? JA", "schlecht"),
               z("ACHTUNG: Die Fälschung wurde NICHT erkannt. Der Hash eines Blocks muss vom", "schlecht"),
               z("Inhalt seiner Transaktionen abhängen (Fehler in main.py, siehe Test-Datei).", "schlecht")]
    else:
        yield [z("6) Kette erneut prüfen", "titel"),
               z("Ist die Kette gültig? NEIN", "gut"),
               z("Der Hash von Block 1 passt nicht mehr zu seinem Inhalt. Die Fälschung fliegt auf.")]


# ---------------------------------------------------------------------------
# Szenario 2: DOUBLE SPENDING
# ---------------------------------------------------------------------------
def szenario_double_spending():
    bc = Blockchain()
    bc.add_account("Alice", 10)
    bc.add_account("Bob", 0)
    bc.add_account("Charlie", 0)
    yield [z("1) Double Spending", "titel"),
           z("Alice hat 10. Sie versucht, dieselben 10 zweimal auszugeben:"),
           z("einmal an Bob und einmal an Charlie.", "schlecht"),
           stand_zeile(bc)]

    versuch = [("Alice", "Bob", 10), ("Alice", "Charlie", 10)]
    _, meldungen = ausgabe_von(bc.new_block, versuch, DIFFICULTY)
    angenommen = {(tx.sender, tx.receiver, tx.amount) for tx in bc.chain[-1].transactions}

    zeilen = [z("2) Das System prüft jede Transaktion der Reihe nach", "titel")]
    for s, r, a in versuch:
        if (s, r, a) in angenommen:
            zeilen.append(z(f"  {s} -> {r} : {a}   ANGENOMMEN", "gut"))
        else:
            zeilen.append(z(f"  {s} -> {r} : {a}   ABGELEHNT", "schlecht"))
    zeilen += [z(f"  Meldung: {m}", "schlecht") for m in meldungen]
    yield zeilen

    yield [z("3) Ergebnis", "titel"),
           z("Nur eine Zahlung ist im Block. Nach der ersten Zahlung hatte Alice 0,"),
           z("deshalb scheitert die zweite. Das Ledger bucht sofort um und prüft dann."),
           stand_zeile(bc)] + kette_zeilen(bc, "Kette")


# ---------------------------------------------------------------------------
# Szenario 3: 51%-ATTACKE
# ---------------------------------------------------------------------------
def szenario_51():
    bc = Blockchain()
    bc.add_account("Alice", 10)
    bc.add_account("Bob", 0)
    bc.add_account("Händler", 0)
    bc.new_block([("Alice", "Bob", 5)], DIFFICULTY)
    yield [z("1) Ausgangslage", "titel"),
           z("Alice hat Bob 5 geschickt. Alle sehen dieselbe Kette."),
           stand_zeile(bc)] + kette_zeilen(bc, "Gemeinsame Kette")

    angreifer = bc.fork()
    yield [z("2) Der Angreifer (Alice) kopiert die Kette", "titel"),
           z("Ab hier existieren zwei getrennte Kopien (Fork).")]

    bc.new_block([("Alice", "Händler", 3)], DIFFICULTY)
    yield [z("3) Ehrliche Kette: Alice bezahlt den Händler 3", "titel"),
           z("Der Händler sieht die Zahlung in der Kette und liefert die Ware."),
           stand_zeile(bc)] + kette_zeilen(bc, "Ehrliche Kette")

    angreifer.new_block([("Bob", "Alice", 1)], DIFFICULTY)
    angreifer.new_block([("Alice", "Bob", 1)], DIFFICULTY)
    yield [z("4) Angreifer mined heimlich 2 Blöcke OHNE die Zahlung an den Händler", "titel"),
           z("Mit mehr als 50% der Rechenleistung schafft er mehr Blöcke als die anderen."),
           stand_zeile(angreifer)] + kette_zeilen(angreifer, "Kette des Angreifers")

    yield [z("5) Vergleich", "titel"),
           z(f"Ehrliche Kette: {len(bc.chain)} Blöcke    Angreifer-Kette: {len(angreifer.chain)} Blöcke",
             "schlecht"),
           z("Die Kette des Angreifers ist länger.")]

    erfolg, meldungen = ausgabe_von(bc.receive_chain, angreifer)
    yield [z("6) Angreifer veröffentlicht seine Kette", "titel"),
           z("Regel: Die längste gültige Kette gewinnt. Das Netzwerk wechselt.")] + \
          [z(f"  {m}", "schlecht") for m in meldungen]

    if erfolg:
        yield [z("7) Ergebnis", "titel"),
               z(f"Händler hat jetzt {bc.ledger.get_balance('Händler')}. "
                 "Seine Zahlung ist rückwirkend verschwunden.", "schlecht"),
               z("Alice hat die Ware UND ihr Geld: Double Spending durch 51%-Attacke."),
               stand_zeile(bc)] + kette_zeilen(bc, "Kette nach dem Angriff")
    else:
        yield [z("7) Ergebnis: Angriff abgelehnt", "titel"),
               z("Die Kette des Angreifers wurde nicht übernommen. Laut Plan sollte sie gültig sein,",
                 "schlecht"),
               z("also liegt ein Fehler in main.py vor (siehe Test-Datei: test_fork_is_valid_copy).",
                 "schlecht"),
               stand_zeile(bc)] + kette_zeilen(bc, "Ehrliche Kette (unverändert)")


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.generator = None
        root.title("Blockchain-Simulation")
        root.geometry("900x600")

        leiste = tk.Frame(root)
        leiste.pack(fill="x", padx=10, pady=10)
        self.knoepfe = []
        for text, szenario in [("NORMAL", szenario_normal),
                               ("Double Spending", szenario_double_spending),
                               ("51% Attacke", szenario_51)]:
            knopf = tk.Button(leiste, text=text, width=18, height=2,
                              command=lambda s=szenario: self.starte(s))
            knopf.pack(side="left", padx=5)
            self.knoepfe.append(knopf)

        self.ausgabe = scrolledtext.ScrolledText(root, font="TkFixedFont", wrap="word",
                                                 state="disabled")
        self.ausgabe.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.fett = tkfont.nametofont("TkFixedFont").copy()
        self.fett.configure(weight="bold")
        self.ausgabe.tag_configure("titel", foreground="#1f4e9c", font=self.fett)
        self.ausgabe.tag_configure("gut", foreground="#1a7f37")
        self.ausgabe.tag_configure("schlecht", foreground="#c62828")

        self.schreibe([z("Wähle ein Szenario.", "titel")])

    def schreibe(self, zeilen, leeren=False):
        self.ausgabe.configure(state="normal")
        if leeren:
            self.ausgabe.delete("1.0", "end")
        for text, tag in zeilen:
            self.ausgabe.insert("end", text + "\n", tag)
        self.ausgabe.insert("end", "\n")
        self.ausgabe.see("end")
        self.ausgabe.configure(state="disabled")

    def knoepfe_setzen(self, aktiv):
        for knopf in self.knoepfe:
            knopf.configure(state="normal" if aktiv else "disabled")

    def starte(self, szenario):
        self.generator = szenario()
        self.knoepfe_setzen(False)
        self.ausgabe.configure(state="normal")
        self.ausgabe.delete("1.0", "end")
        self.ausgabe.configure(state="disabled")
        self.naechster_schritt()

    def naechster_schritt(self):
        try:
            zeilen = next(self.generator)
        except StopIteration:
            self.knoepfe_setzen(True)
            return
        except Exception as fehler:
            self.schreibe([z(f"Fehler im Szenario: {fehler!r}", "schlecht")])
            self.knoepfe_setzen(True)
            return
        self.schreibe(zeilen)
        self.root.after(SCHRITT_PAUSE_MS, self.naechster_schritt)


if __name__ == "__main__":
    fenster = tk.Tk()
    App(fenster)
    fenster.mainloop()