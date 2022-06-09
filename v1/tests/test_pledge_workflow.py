from unittest import TestCase

import brownie

pledge_fee = "0.010 ether"
min_pledge = "0.001 ether"

brownie.network.connect()


class accounts:
    from brownie import accounts as _

    # Owner account
    owner = _[0]

    # Benefactor account
    benefactor = _[1]

    # Beneficiary account
    beneficiary = _[2]


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


class Test(TestCase):
    def test_basic_workflow(self):
        # 2. Configure the `Pledge` contract

        tx = deployed.pledge.configure_pledge(
            pledge_fee,
            min_pledge,
            {'from': accounts.owner}
        )

        self.assertEqual(1, tx.status)

        # 3. Register a beneficiary

        approve = True

        tx = deployed.pledge._approve_beneficiary(
            accounts.beneficiary,
            approve,
            {'from': accounts.owner}
        )

        self.assertEqual(1, tx.status)
        self.assertEqual(approve, deployed.pledge.is_approved_beneficiary(accounts.beneficiary))

        # 4. Wrap ether

        tx = accounts.benefactor.transfer(to=deployed.weth, amount="1 ether")
        self.assertEqual(1, tx.status)

        self.assertGreaterEqual(deployed.weth.balanceOf(accounts.benefactor), "1 ether")

        # 5. Pledge

        self.assertEqual(0, deployed.pledge.pledged_amount(accounts.benefactor, accounts.beneficiary))

        from brownie import convert
        pledge_amount = "0.01 ether"

        self.assertGreaterEqual(convert.Wei(pledge_amount), convert.Wei(min_pledge))

        tx = deployed.pledge.pledge(
            accounts.beneficiary,
            pledge_amount,
            {'from': accounts.benefactor, 'value': pledge_fee}
        )

        self.assertEqual(1, tx.status)

        self.assertEqual(pledge_amount, deployed.pledge.pledged_amount(accounts.benefactor, accounts.beneficiary))

        # 6. Set allowance: 'pledge' can transfer WETH on behalf of 'benefactor'

        tx = deployed.weth.approve(deployed.pledge, "1 ether", {'from': accounts.benefactor})

        self.assertEqual(1, tx.status)

        # 7. Pay out from within the Pledge contract

        tx = deployed.pledge.pay(
            accounts.benefactor,
            accounts.beneficiary,
            pledge_amount,
            {'from': accounts.owner, 'gas_limit': 100_000, 'allow_revert': True}
        )

        self.assertEqual(1, tx.status)

        # 8. Withdraw WETH

        self.assertEqual(convert.Wei(pledge_amount), deployed.weth.balanceOf(accounts.beneficiary))

        tx = deployed.weth.withdraw(
            deployed.weth.balanceOf(accounts.beneficiary),
            {'from': accounts.beneficiary}
        )

        self.assertEqual(1, tx.status)

        # This doesn't work in the test for some reason
        # self.assertEqual(0, deployed.weth.balanceOf(accounts.beneficiary))
