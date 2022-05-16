from unittest import TestCase

import brownie.network.contract

from brownie import network, accounts

from web3 import Web3
from web3.contract import Contract


class Test(TestCase):
    def test_deploy_contract_weth9(self):
        account = accounts[0]

        from brownie import WETH9
        assert isinstance(WETH9, brownie.network.contract.ContractContainer)

        weth = WETH9.deploy({'from': account})
        assert isinstance(weth, brownie.network.contract.ProjectContract)

    def test_deploy_contract_pledge(self):
        account = accounts[0]

        from brownie import Pledge
        assert isinstance(Pledge, brownie.network.contract.ContractContainer)

        pledge = Pledge.deploy({'from': account})
        assert isinstance(pledge, brownie.network.contract.ProjectContract)
