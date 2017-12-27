"""
This is the Blockchain
View methods implementation:
An API to achieve all our
blockchain app transactions
"""

from flask import Blueprint, jsonify, request
from app.models.blockchain import Blockchain
from app.services.blockchain_service import hash, last_block, new_block, add_transaction, proof_of_work, register_node, resolve_conflicts, valid_chain
from uuid import uuid4

blockchain_view = Blueprint('blockchain_view', __name__)


# Instantiate the Blockchain
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

@blockchain_view.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.chain[-1]
    last_proof = last_block['proof']
    proof = proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    new_transaction(
        sender="0",
        recipient=str(uuid4()).replace('-', ''),
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = hash(last_block)
    block = new_block(proof, blockchain, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@blockchain_view.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = add_transaction(blockchain, values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@blockchain_view.route('/chain', methods=['GET'])
def full_chain():
    # Create the genesis block
    new_block(blockchain, previous_hash='1', proof=100)
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@blockchain_view.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@blockchain_view.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

