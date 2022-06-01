import unittest

import brownie.network
from brownie import Wei

from brownie.exceptions import VirtualMachineError

brownie.network.connect()


class ThisIsOK(Exception):
    pass


class const:
    min_pledge = Wei("0.10 ether")
    pledge_fee = Wei("0.01 ether")

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


class preparations:
    # Pledge contract setup
    deployed.pledge.configure_pledge(
        const.pledge_fee,
        const.min_pledge,
        {'from': accounts.owner}
    )

    # Approve a beneficiary
    deployed.pledge._approve_beneficiary(
        accounts.approved_beneficiary,
        True,
        {'from': accounts.owner}
    )

    # Make a pledge
    deployed.pledge.pledge(
        accounts.approved_beneficiary,
        const.min_pledge * 2,
        {
            'from': accounts.committed_benefactor,
            'value': const.pledge_fee,
        }
    )

    # Benefactor deposits WETH
    accounts.committed_benefactor.transfer(to=deployed.weth, amount="1 ether")

    # Authorize the 'Pledge' contract on benefactor's WETH
    deployed.weth.approve(
        deployed.pledge,
        "1 ether",
        {'from': accounts.committed_benefactor}
    )

class sanity_checks:
    deployed.weth.transferFrom(
        accounts.committed_benefactor,
        accounts.approved_beneficiary,
        1,
        {
            'from': accounts.committed_benefactor,
        }
    )


class Test(unittest.TestCase):
    def test_reverts_if_unapproved_beneficiary(self):
        self.assertTrue(not deployed.pledge.is_approved_beneficiary(accounts.unapproved_beneficiary))

        with self.assertRaises(VirtualMachineError):
            deployed.pledge.pledge(
                accounts.unapproved_beneficiary,
                deployed.pledge.min_pledge(),
                {
                    'gas_limit': 1_000_000,
                    'from': accounts.potential_benefactor,
                    'value': deployed.pledge.pledge_fee(),
                    'allow_revert': True,
                }
            )

    def test_reverts_if_pledge_too_small(self):
        self.assertTrue(deployed.pledge.is_approved_beneficiary(accounts.approved_beneficiary))

        insufficient_pledge = deployed.pledge.min_pledge() - 1

        with self.assertRaises(VirtualMachineError):
            deployed.pledge.pledge(
                accounts.approved_beneficiary,
                insufficient_pledge,
                {
                    'gas_limit': 1_000_000,
                    'from': accounts.potential_benefactor,
                    'value': deployed.pledge.pledge_fee(),
                    'allow_revert': True,
                }
            )

    def test_reverts_if_insufficient_fee(self):
        self.assertTrue(deployed.pledge.is_approved_beneficiary(accounts.approved_beneficiary))

        insufficient_fee = deployed.pledge.pledge_fee() - 1

        with self.assertRaises(VirtualMachineError):
            deployed.pledge.pledge(
                accounts.approved_beneficiary,
                deployed.pledge.min_pledge(),
                {
                    'gas_limit': 1_000_000,
                    'from': accounts.potential_benefactor,
                    'value': insufficient_fee,
                    'allow_revert': True,
                }
            )


    def test_cannot_approve_if_not_owner(self):
        with self.assertRaises(VirtualMachineError):
            deployed.pledge._approve_beneficiary(
                accounts.unapproved_beneficiary,
                True,
                {
                    'from': accounts.unapproved_beneficiary,
                    'gas_limit': 1_000_000,
                    'allow_revert': True,
                }
            )

    def test_cannot_withdraw_if_not_owner(self):
        # This works
        deployed.pledge._withdraw(accounts.owner, 0, {'from': accounts.owner})

        # But this raises
        with self.assertRaises(VirtualMachineError):
            deployed.pledge._withdraw(
                accounts.hacker,
                0,
                {
                    'from': accounts.hacker,
                    'gas_limit': 1_000_000,
                    'allow_revert': True,
                }
            )

    def test_cannot_payout_weth_directly_from_pledge(self):
        # ValueError: sender account not recognized
        with self.assertRaises(ValueError):
            deployed.weth.transferFrom(
                accounts.committed_benefactor,
                accounts.approved_beneficiary,
                0,
                {
                    'from': deployed.pledge,
                    'gas_limit': 1_000_000,
                    'allow_revert': True,
                }
            )

    def test_cannot_payout_weth_directly_from_owner(self):
        with self.assertRaises(VirtualMachineError):
            # Fails in the WETH contract:
            # require(allowance[src][msg.sender] >= wad)
            deployed.weth.transferFrom(
                accounts.committed_benefactor,
                accounts.approved_beneficiary,
                1,
                {
                    'from': accounts.owner,
                    'gas_limit': 1_000_000,
                    'allow_revert': True,
                }
            )


    def sandbox(self):

        # 9. Another pay-out prohibited

        with self.assertRaises(VirtualMachineError):
            tx = pledge.pay(
                benefactor.address,
                beneficiary.address,
                pledge_amount,
                {'from': owner.address, 'gas_limit': 100_000, 'allow_revert': True}
            )

            raise AssertionError("Shouldn't be here!")
