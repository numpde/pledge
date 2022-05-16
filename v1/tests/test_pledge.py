from unittest import TestCase

import brownie.network.contract

from brownie import network, accounts

pledge_fee = "0.010 ether"
min_pledge = "0.001 ether"

# # https://support.savethechildren.org/site/SPageNavigator/donation__crypto.html
# beneficiary = "0xc51E4E60566e95BCa6407aE9352BbCd3698972CE"


class Test(TestCase):
    def test_basic_workflow(self):
        # Owner account
        owner = accounts[0]

        # Benefactor account
        benefactor = accounts[1]

        # Beneficiary account
        beneficiary = accounts[2]

        # 1. Setup

        # Deploy contract: WETH9

        from brownie import WETH9
        self.assertIsInstance(WETH9, brownie.network.contract.ContractContainer)

        weth = WETH9.deploy({'from': owner})
        self.assertIsInstance(weth, brownie.network.contract.ProjectContract)

        # Deploy contract: Pledge

        from brownie import Pledge
        self.assertIsInstance(Pledge, brownie.network.contract.ContractContainer)

        pledge = Pledge.deploy({'from': owner})
        self.assertIsInstance(pledge, brownie.network.contract.ProjectContract)

        # 2. Configure the `Pledge` contract

        tx = pledge.configure.transact(weth.address, pledge_fee, min_pledge, {'from': accounts[0].address})
        self.assertEqual(1, tx.status)

        # 3. Register a beneficiary

        self.assertTrue(not pledge.is_approved_beneficiary(beneficiary))

        for approve in [True, False, True]:
            tx = pledge._approve_beneficiary.transact(beneficiary, approve, {'from': accounts[0].address})
            self.assertEqual(1, tx.status)
            self.assertEqual(approve, pledge.is_approved_beneficiary(beneficiary))

        # 4. Wrap ether

        tx = benefactor.transfer(to=weth.address, amount="1 ether")
        self.assertEqual(1, tx.status)

        self.assertGreaterEqual(weth.balanceOf(benefactor.address), "1 ether")

        # 5. Pledge

        self.assertEqual(0, pledge.pledged_amount(benefactor.address, beneficiary.address))

        from brownie import convert
        pledge_amount = "0.01 ether"

        self.assertGreaterEqual(convert.Wei(pledge_amount), convert.Wei(min_pledge))

        tx = pledge.pledge(beneficiary.address, pledge_amount, {'from': benefactor.address, 'value': pledge_fee})
        self.assertEqual(1, tx.status)

        self.assertEqual(pledge_amount, pledge.pledged_amount(benefactor.address, beneficiary.address))

        # 6. Set allowance: 'pledge' can transfer WETH on behalf of 'benefactor'

        tx = weth.approve(pledge.address, "1 ether", {'from': benefactor.address})
        self.assertEqual(1, tx.status)

        # 7. Pay out raw: prohibited

        with self.assertRaises(ValueError):
            weth.transferFrom(benefactor.address, beneficiary.address, pledge_amount, {'from': pledge})

        with self.assertRaises(ValueError):
            weth.transferFrom(benefactor.address, beneficiary.address, pledge_amount, {'from': owner})

        # 8. Pay out from within the Pledge contract

        # https://eth-brownie.readthedocs.io/en/stable/core-contracts.html#transaction-parameters
        tx = pledge.pay(benefactor.address, beneficiary.address, {'from': owner.address, 'gas_limit': 80_000, 'allow_revert': True})
        self.assertEqual(1, tx.status)
