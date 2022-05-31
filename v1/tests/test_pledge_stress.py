import unittest

import brownie.network

from brownie.exceptions import VirtualMachineError

brownie.network.connect()


class ThisIsOK(Exception):
    pass


class accounts:
    from brownie import accounts as _

    # Owner account
    owner = _[0]

    # Benefactor account
    benefactor = _[1]

    # Beneficiary accounts
    approved_beneficiary = _[5]
    unapproved_beneficiary = _[6]


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
    deployed.pledge._approve_beneficiary.transact(
        accounts.approved_beneficiary,
        True,
        {'from': accounts.owner}
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
                    'from': accounts.benefactor,
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
                    'from': accounts.benefactor,
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
                    'from': accounts.benefactor,
                    'value': insufficient_fee,
                    'allow_revert': True,
                }
            )


    def test_cannot_approve_if_nonowner(self):
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

    def test_cannot_withdraw_if_nonowner(self):
        deployed.pledge._withdraw(accounts.owner, 0, {'from': accounts.owner})

        with self.assertRaises(VirtualMachineError):
            deployed.pledge._withdraw(
                accounts.benefactor,
                0,
                {
                    'gas_limit': 1_000_000,
                    'from': accounts.benefactor,
                    'allow_revert': True,
                }
            )

    def sandbox(self):
        # 7. Pay out raw: prohibited

        with self.assertRaises(ValueError):
            deployed.weth.transferFrom(
                accounts.benefactor,
                beneficiary.address,
                pledge_amount,
                {'from': deployed.pledge}
            )

        with self.assertRaises(ValueError):
            weth.transferFrom(benefactor.address, beneficiary.address, pledge_amount, {'from': owner})

        # 9. Another pay-out prohibited

        with self.assertRaises(VirtualMachineError):
            tx = pledge.pay(
                benefactor.address,
                beneficiary.address,
                pledge_amount,
                {'from': owner.address, 'gas_limit': 100_000, 'allow_revert': True}
            )

            raise AssertionError("Shouldn't be here!")
