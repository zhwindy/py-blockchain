#!/usr/bin/env python
# encoding=utf-8
import sys
import json
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain import BlockChain

app = Flask(__name__)

node_symbal = str(uuid4()).replace("-", "")

blockchain = BlockChain()


@app.route("/", methods=['GET'])
def main():
    """
    首页
    """
    response = 'Welcome to simple blockchain demo \r\n'

    return response


@app.route("/mine", methods=['GET'])
def mine():
    """
    挖矿
    """
    last_block = blockchain.last_block
    prev_diff = last_block['diff']
    diff = blockchain.pow_work(prev_diff)
    # 添加coinbase交易
    blockchain.new_transaction(
        sender="0",
        receiver=node_symbal,
        amount=50)
    block = blockchain.new_block(diff)

    return f"mine a block {block}", 200


@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    """
    生成新交易
    """
    request_data = request.get_json()
    required = ['sender', 'receiver', 'amount']
    if not all(k in request_data for k in required):
        return "Error: missing params", 400
    sender, receiver, amount = request_data['sender'], request_data['receiver'], request_data['amount']
    index = blockchain.new_transaction(sender, receiver, amount)
    response = {"Message": f"Transactions add to block {index}"}

    return jsonify(response), 200


@app.route("/chain", methods=['GET'])
def chain():
    """
    获取区块链信息
    """
    chain = blockchain.chain
    response = {
        "length": len(chain),
        "blocks": chain
    }
    return jsonify(response), 200


@app.route("/node/register", methods=['POST'])
def node_register():
    """
    注册节点
    """
    data = request.get_json()
    nodes = data.get("nodes")
    if not nodes:
        return "Error: please add right node list", 400

    for node in nodes:
        blockchain.register_nodes(node)

    response = {
        "Message": "Node are added",
        "nodes": [node for node in blockchain.nodes],
        "total_nodes": len(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route("/node/resolve", methods=['GET'])
def consensus():
    """
    共识算法
    """
    result = blockchain.resolve_conflict()
    if result:
        response = {
            "Message": "Our chian is replaced",
            "Newchain": blockchain.chain
        }
    else:
        response = {
            "Message": "Our chian is the best chain",
            "chain": blockchain.chain
        }

    return jsonify(response), 200


if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        port = 5000
    app.run(host='0.0.0.0', port=port)
