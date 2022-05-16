import time

from unittest import TestCase

import brownie

from brownie import accounts
from brownie import web3 as w3

from web3 import Web3
from web3.contract import Contract


class Test(TestCase):
    def test_account_balance_and_transfer(self):
        account0 = accounts[0]
        account1 = accounts[1]

        balance_before = account0.balance()

        tx = account0.transfer(to=account1, amount="1 gwei", gas_price=0)
        self.assertEqual(1, tx.status)

        time.sleep(2)

        balance_after = account0.balance()  # does not update?!

        self.assertEqual(balance_before - "1 gwei", balance_after)

    def test_(self):
        pass

        # import web3.contract
        #
        # weth = w3.eth.contract(address=weth.address, abi=weth.abi)
        #
        # weth.functions.deposit().transact({'from': account.address, 'value': w3.toWei(1, 'ether')})
        # weth.functions.withdraw(wad=w3.toWei(1, 'ether')).transact({'from': account.address})
