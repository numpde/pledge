import unittest

import brownie.network
from brownie import Wei

from brownie.exceptions import VirtualMachineError


def connect():
    try:
        brownie.network.disconnect()
    except ConnectionError:
        pass
    finally:
        brownie.network.connect()


connect()


class ThisIsOK(Exception):
    pass


class const:
    min_pledge = Wei("0.0110 ether")
    pledge_fee = Wei("0.0011 ether")


class accounts:
    from brownie import accounts as _

    # Owner account
    owner = _[0]

    # Benefactor accounts
    committed_benefactor = _[1]
    potential_benefactor = _[2]

    # Beneficiary accounts
    approved_beneficiary = _[5]
    unapproved_beneficiary = _[6]

    # Random address
    hacker = _[9]


class deployed:
    import brownie.network.contract

    # Deploy contract: WETH9

    # from brownie import WETH9
    assert isinstance(brownie.WETH9, brownie.network.contract.ContractContainer)

    weth = brownie.WETH9.deploy({'from': accounts.owner})
    assert isinstance(weth, brownie.network.contract.ProjectContract)

    # Deploy contract: Pledge

    # from brownie import Pledge
    assert isinstance(brownie.Pledge, brownie.network.contract.ContractContainer)

    pledge = brownie.Pledge.deploy(weth.address, {'from': accounts.owner})
    assert isinstance(pledge, brownie.network.contract.ProjectContract)


class Tests(unittest.TestCase):
    def test_weth_address_is_correct(self):
        configured_weth_address = deployed.pledge.weth_address()
        self.assertEqual(deployed.weth.address, configured_weth_address)


class TestConfigure(unittest.TestCase):
    def test_configure_works(self):
        pledge_fee = deployed.pledge.pledge_fee() + 1
        min_pledge = deployed.pledge.min_pledge() + 1

        deployed.pledge.configure_pledge(
            pledge_fee,
            min_pledge,
            {'from': accounts.owner}
        )

        # connect()

        pledge = brownie.Pledge.at(address=deployed.pledge.address)

        self.assertEqual(pledge_fee, pledge.pledge_fee())
        self.assertEqual(min_pledge, pledge.min_pledge())


# class preparations:
#     pass  # see file *_stress.py
