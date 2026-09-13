import hashlib
import time
from datetime import datetime

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.data = f"{sender} -> {receiver} : {amount}"
        self.timestamp=time.time()
        self.dateandtime = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S %d-%m-%Y")
    def __str__(self):
        return self.data

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.dateandtime = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S %d-%m-%Y")
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()  

    def calculate_hash(self):
        # Alle Felder zu einem String zusammensetzen
        block_string = (
            str(self.index) +
            str(self.dateandtime) +
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
            f"  Zeitstempel:   {self.dateandtime}\n"
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


