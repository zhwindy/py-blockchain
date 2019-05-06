#! /usr/bin/env python
# encoding=utf-8
import time
import json
import hashlib
import requests
from uuid import uuid4
from urllib.parse import urlparse


class BlockChain(object):
    """
    区块链
    """
    def __init__(self):
        self.chain = []
        self.current_tracsactions = []
        # 初始化创世区块
        self.new_block(100, prev_hash=1)
        # 已保存节点
        self.nodes = set()

    def register_nodes(self, address):
        """
        节点注册
        """
        url = urlparse(address)
        self.nodes.add(url.netloc)

    def new_transaction(self, sender, receiver, amount):
        """
        构造新交易
        """
        tx = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }
        self.current_tracsactions.append(tx)

        return self.last_block['index'] + 1

    def new_block(self, diff, prev_hash=None):
        """
        构造新区块
        """
        block = {
            "version": 2,
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "diff": diff,
            "counts": len(self.current_tracsactions),
            "transactions": self.current_tracsactions,
            "prev_hash": prev_hash if prev_hash else self.hash(self.chain[-1])
        }

        # 重置交易列表
        self.current_tracsactions = []

        self.chain.append(block)

        return block

    @staticmethod
    def hash(block):
        """
        生成区块sha-256哈希值
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_string).hexdigest()
        return block_hash

    @property
    def last_block(self):
        """
        返回区块链最新节点的索引
        """
        return self.chain[-1]

    def pow_work(self, last_diff):
        """
        工作量证明
        """
        diff = 0
        while not self.valid(last_diff, diff):
            diff += 1
        return diff

    @staticmethod
    def valid(last_diff, diff):
        """
        验证
        """
        tmp = f"{last_diff}{diff}".encode()
        hex_string = hashlib.sha256(tmp).hexdigest()

        return hex_string[:4] == "0000"

    def resolve_conflict(self):
        """
        处理一致性问题,按最长有效链原则
        """
        other_nodes = self.nodes
        new_chain = None

        this_chain_length = len(self.chain)

        for node in other_nodes:
            node_response = requests.get(f'http://{node}/chain')
            if node_response.status_code == 200:
                node_result = node_response.json()
                node_chain = node_result['blocks']
                node_chain_length = node_result['length']

                if node_chain_length > this_chain_length and self.valid_chain(node_chain):
                    new_chain = node_chain
                    this_chain_length = node_chain_length
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def valid_chain(self, chain):
        """
        验证链的有效性
        """
        length = len(chain)
        front_block = chain[0]
        index = 1
        while index < length:
            block = chain[index]
            if block['prev_hash'] != self.hash(front_block):
                return False
            if not self.valid(front_block['diff'], block['diff']):
                return False
            front_block = block
            index += 1
        return True
