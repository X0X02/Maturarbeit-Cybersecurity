from main import *



# Tests 10.09.26
"""
if __name__ == "__main__":
    block = Block(index=0, data="Alice -> Bob: 10 BTC", previous_hash="0")
    print(block)
    
    # Zeigt, dass Hash verändert wird.
    print("\nHash vorher:", block.hash[:30])
    block.data = "Alice -> Bob: 100 BTC"      
    block.hash = block.calculate_hash()
    print("Hash nachher:", block.hash[:30])
    print("→ anderer Hash!")

if __name__ == "__main__":
    bc = Blockchain()
    bc.new_block("Alice -> Bob: 5 BTC")
    bc.new_block("Bob -> Charlie: 2 BTC")

    for block in bc.chain:
        print(block)
        print()

if __name__ == "__main__":
    bc = Blockchain()
    bc.new_block("Alice -> Bob: 5 BTC")
    bc.new_block("Bob -> Charlie: 2 BTC")

    print("Ist die Kette gültig?", bc.is_chain_valid())

    # Jetzt manipulieren wir heimlich einen Block
    bc.chain[1].data = "Alice -> Bob: 500 BTC"
    print("Nach Manipulation:", bc.is_chain_valid()) 

if __name__ == "__main__":
    b = Block(index=0, data="Test", previous_hash="0")
    print("Vor Mining:", b.hash, "Nonce:", b.nonce)
    b.mine_block(4)
    print("Nach Mining:", b.hash, "Nonce:", b.nonce)"""
#Tests 13.09.26
"""
if __name__ == "__main__":
    #Test 1 Gültigkeit und Manipulation
    bc = Blockchain()
    bc.new_block("Alice -> Bob: 5 BTC", difficulty = 4)
    bc.new_block("Bob -> Charlie: 3 BTC", difficulty= 4)

    print ("Ist die Kette gültig?", bc.is_chain_valid())
    bc.chain[1].data = "Alice -> Bob: <5 BTC"
    print ("Ist die Kette gültig?", bc.is_chain_valid())

    # Test 2 Test mit 15 Blöcken
    bc2 = Blockchain()
    for i in range (14):
        bc2.new_block(f"Transaktion #{i+1}", difficulty=4)
        print(bc2)
    print("\nAnzahl Blöcke:", len(bc2.chain))
    print("Ist die grosse Kette gültig?", bc2.is_chain_valid())

#später mit unittest modul & mehr transaktionen usw mit "echten daten"

tx = Transaction("Alice", "Bob", 5)
block = Block(index=1, transactions=tx, previous_hash="0")
print(block)


tx1 = Transaction("Alice", "Bob", 5)
tx2 = Transaction("Bob", "Charlie", 2)
block = Block(index=1, transactions=[tx1, tx2], previous_hash="0")
print(block)
"""


"""

balances = {"Alice": 10, "Bob": 0, "Charlie": 0}

tx1 = Transaction("Alice", "Bob", 10, balances)
print("Nach tx1:", balances)

tx2 = Transaction("Alice", "Charlie", 10, balances)  # sollte fehlschlagen!


balances = {"Alice": 10, "Bob": 0, "Charlie": 0}
versuche = [
    ("Alice", "Bob", 10),
    ("Alice", "Charlie", 10),
]

for sender, receiver, amount in versuche:
    try:
        tx = Transaction(sender, receiver, amount, balances)
        print("✅ Erfolgreich:", tx)
    except ValueError as e:
        print(f"❌ Abgelehnt: {sender} -> {receiver} ({amount}) — {e}")


print("\nEndstand:", balances)


ledger = Ledger()
ledger.add_account("Alice", 10)
ledger.add_account("Bob", 0)
print(ledger.get_balance("Alice"))   # sollte 10 zeigen
tx = ledger.transfer("Alice", "Bob", 5)
print(ledger.get_balance("Alice"), ledger.get_balance("Bob"))  # 5, 5

"""


bc = Blockchain()
bc.ledger.add_account("Alice", 10)
bc.ledger.add_account("Bob", 0)
bc.ledger.add_account("Charlie", 0)

bc.new_block([
    ("Alice", "Bob", 10),
    ("Alice", "Charlie", 10),   # sollte abgelehnt werden
], difficulty=4)

print(bc.chain[-1])
print("Kontostände:", bc.ledger.balances)
print("Kette gültig?", bc.is_chain_valid())