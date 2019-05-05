#! /usr/bin/env python
# encoding=utf-8

import time


class BlockChain(object):
    """
    区块链
    """
    def __init__(self):
        self.chain = []
        self.current_tracsactions = []
        # 初始化创世区块
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """
        生成创世区块
        """
        sender = 0
        receiver = ""
        amount = 1
        self.new_transactions(sender, receiver, amount)
        genesis_block = self.new_block(0)
        self.chain.append(genesis_block)

    def new_transactions(self, sender, receiver, amount):
        """
        构造新交易
        """
        tx = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }
        self.current_tracsactions.append(tx)

    def new_block(self, index):
        """
        构造新区块
        """
        block = {
            "version": 2,
            "index": index,
            "timestamp": time.time(),
            "diff": 100,
            "counts": len(self.current_tracsactions),
            "transactions": self.current_tracsactions
        }

        return block

    def add_block(self):
        """
        添加新区块到链上
        """
        index = self.last_block + 1
        block = self.new_block(index)
        self.chain.append(block)

    @property
    def last_block(self):
        """
        返回区块链最新节点的索引
        """
        return self.chain[-1]['index']
