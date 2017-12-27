from time import time
from urllib.parse import urlparse
from app.models.blockchain import  Blockchain
import hashlib
import json

import requests
"""
This is the Blockchain
Service functions implementation
"""

def register_node(blockchain, address):
    """
    Add a new node to the list of nodes

    :param address: Address of node. Eg. 'http://192.168.0.5:5000'
    """

    parsed_url = urlparse(address)
    blockchain.nodes.add(parsed_url.netloc)

def valid_chain(chain):
    """
    Determine if a given blockchain is valid

    :param chain: A blockchain
    :return: True if valid, False if not
    """

    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
        block = chain[current_index]
        print(f'{last_block}')
        print(f'{block}')
        print("\n-----------\n")
        # Check that the hash of the block is correct
        if block['previous_hash'] != hash(last_block):
            return False

        # Check that the Proof of Work is correct
        if not valid_proof(last_block['proof'], block['proof']):
            return False

        last_block = block
        current_index += 1

    return True

def resolve_conflicts(blockchain):
    """
    This is our consensus algorithm, it resolves conflicts
    by replacing our chain with the longest one in the network.

    :return: True if our chain was replaced, False if not
    """

    neighbours = blockchain.nodes
    new_chain = None

    # We're only looking for chains longer than ours
    max_length = len(blockchain.chain)

    # Grab and verify the chains from all the nodes in our network
    for node in neighbours:
        response = requests.get(f'http://{node}/chain')

        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']

            # Check if the length is longer and the chain is valid
            if length > max_length and valid_chain(chain):
                max_length = length
                new_chain = chain

    # Replace our chain if we discovered a new, valid chain longer than ours
    if new_chain:
        blockchain.chain = new_chain
        return True

    return False

def new_block(blockchain, proof, previous_hash):
    """
    Create a new Block in the Blockchain

    :param proof: The proof given by the Proof of Work algorithm
    :param previous_hash: Hash of previous Block
    :return: New Block
    """

    block = {
        'index': len(blockchain.chain) + 1,
        'timestamp': time(),
        'transactions': blockchain.current_transactions,
        'proof': proof,
        'previous_hash': previous_hash or hash(blockchain.chain[-1]),
    }

    # Reset the current list of transactions
    current_transactions = []

    blockchain.chain.append(block)
    return block

def add_transaction(blockchain, sender, recipient, amount):
    """
    Creates a new transaction to go into the next mined Block

    :param sender: Address of the Sender
    :param recipient: Address of the Recipient
    :param amount: Amount
    :return: The index of the Block that will hold this transaction
    """
    blockchain.current_transactions.append({
        'sender': sender,
        'recipient': recipient,
        'amount': amount,
    })
    print(blockchain)
    return 5#blockchain.chain[-1]['index'] + 1

@property
def last_block(blockchain):
    return blockchain.chain[-1]

@staticmethod
def hash(block):
    """
    Creates a SHA-256 hash of a Block

    :param block: Block
    """

    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def proof_of_work(last_proof):
    """
    Simple Proof of Work Algorithm:
     - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
     - p is the previous proof, and p' is the new proof
    """

    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof += 1

    return proof

@staticmethod
def valid_proof(last_proof, proof):
    """
    Validates the Proof

    :param last_proof: Previous Proof
    :param proof: Current Proof
    :return: True if correct, False if not.
    """

    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"
