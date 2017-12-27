"""
This is the Blockchain
Model class implementation
"""

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

    def __repr__(self):
        return '<Blockchain(chain={self.chain!r}, current_transactions={self.current_transactions!r})>'.format(self=self)