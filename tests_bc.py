from main import Block, Blockchain



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
    print("\nAnzahl Blöcke:", len(bc2.chain))
    print("Ist die grosse Kette gültig?", bc2.is_chain_valid())


