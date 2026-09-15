import hashlib
import time
from datetime import datetime

class Ledger:
    def __init__(self):
        self.balances = {}

    def add_account(self, name, starting_balance): #Problem mit selbem namen!!
        self.balances[name] = starting_balance
    
    def get_balance(self, name):
        return self.balances[name]
            
    def transfer(self, sender, receiver, amount):
        if self.balances[sender] < amount:
            raise ValueError("Nicht genug Guthaben")
        if receiver not in self.balances:
            self.balances[receiver] = 0
        else:
            self.balances[sender]-=amount
            self.balances[receiver]+=amount
            #wer noch nicht im dictionary is und geld bekommt-> später.
        return Transaction(sender, receiver, amount)  # jetzt nur noch ein "Beleg"


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
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.dateandtime = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S %d-%m-%Y")
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()  

    def calculate_hash(self):
        # Alle Felder zu einem String zusammensetzen
        block_string = (
            str(self.index) +
            str(self.dateandtime) +
            str(self.transactions) +
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
        txn_strings = "\n".join(str(tx) for tx in self.transactions)
        return (
            f"Block #{self.index}\n"
            f"  Daten:\n       {txn_strings}\n"
            f"  Zeitstempel:   {self.dateandtime}\n"
            f"  Previous Hash: {self.previous_hash[:20]}...\n"
            f"  Hash:          {self.hash[:20]}...\n"
            f"  Nonce:         {self.nonce}"
        )



class Blockchain:
    def __init__(self):
        self.chain = []
        self.ledger = Ledger()

        Genesis=Block(index=0, transactions=["Genesis Block"], previous_hash="0")
        self.chain.append(Genesis)

    def new_block(self, transaction_data, difficulty): #transaction data not yet transactions
        valid_transactions = []

        for sender, receiver, amount in transaction_data:
            try:
                tx = self.ledger.transfer(sender, receiver, amount)
                valid_transactions.append(tx)
            except ValueError as e:
                print(f"Fehler: {sender} -> {receiver} ({amount}) - {e}")

        index = len(self.chain)
        previous_hash = self.chain[-1].hash
        new_block = Block(index, valid_transactions, previous_hash)
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


