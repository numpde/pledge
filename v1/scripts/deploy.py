from brownie import accounts
from brownie import Pledge
from brownie import WETH9

def main():
    Pledge.deploy({'from': accounts[0]})
