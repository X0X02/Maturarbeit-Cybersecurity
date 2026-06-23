import hashlib
import time

class Block:
    def __init__(self, index, data, previous_hash, nonce):
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

    def __str__(self):
        return (
            f"Block #{self.index}\n"
            f"  Daten:         {self.data}\n"
            f"  Zeitstempel:   {self.timestamp}\n"
            f"  Previous Hash: {self.previous_hash[:20]}...\n"
            f"  Hash:          {self.hash[:20]}...\n"
            f"  Nonce:         {self.nonce}"
        )





# Test
if __name__ == "__main__":
    block = Block(index=0, data="Alice -> Bob: 10 BTC", previous_hash="0")
    print(block)
    
    # Zeigt, dass eine Änderung den Hash verändert
    print("\nHash vorher:", block.hash[:30])
    block.data = "Alice -> Bob: 100 BTC"        # Manipulation!
    block.hash = block.calculate_hash()
    print("Hash nachher:", block.hash[:30])
    print("→ anderer Hash!")
