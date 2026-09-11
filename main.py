import hashlib
import time

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()  

    def calculate_hash(self):
        # Alle Felder zu einem String zusammensetzen
        block_string = (
            str(self.index) +
            str(self.timestamp) +
            str(self.data) +
            str(self.previous_hash) +
            str(self.nonce)
        )
        # SHA-256 berechnen und als Hexadezimalzahl zurückgeben
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
            target= "0" * difficulty
            while self.hash[:difficulty] != target:
                self.nonce += 1
                self.hash = self.calculate_hash()


        

    def __str__(self):
        return (
            f"Block #{self.index}\n"
            f"  Daten:         {self.data}\n"
            f"  Zeitstempel:   {self.timestamp}\n"
            f"  Previous Hash: {self.previous_hash[:20]}...\n"
            f"  Hash:          {self.hash[:20]}...\n"
            f"  Nonce:         {self.nonce}"
        )



class Blockchain:
    def __init__(self):
        self.chain = []

        Genesis=Block(index=0, data="Genesis Block", previous_hash="0")
        self.chain.append(Genesis)

    def new_block(self, data, difficulty):
        index = len(self.chain)
        previous_hash = self.chain[-1].hash
        new_block = Block(index, data, previous_hash)
        new_block.mine_block(difficulty)
        self.chain.append(new_block)
          

    def is_chain_valid(self):
        for i in range(1,len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            if current.previous_hash != previous.hash:
                return False

            if current.hash != current.calculate_hash():
                return False

        return True






    
# TestTESTTEST
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
    print("Nach Mining:", b.hash, "Nonce:", b.nonce)