from itertools import count
from brownie import Wei, reverts
import eth_abi
from brownie.convert import to_bytes
from useful_methods import genericStateOfStrat,genericStateOfVault
import random
import brownie
from pytest import approx

def test_opsss_lvie(accounts, chain, interface, Contract, AffiliateTokenGatedUpgradeable, Vault, Registry):
    vault = Vault.at('0xA696a63cc78DfFa1a63E9E50587C197387FF6C7E')
    registry = Registry.at('0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804')

    acc = accounts.at(vault.governance(), force=True)

    underStrat = interface.StrategyAPI('0xF0252a99691D591A5A458b9b4931bF1025BF6Ac3')
    whale = accounts.at('0xccF4429DB6322D5C611ee964527D42E5d685DD6a', force=True)
    minow = accounts[0]
    wbtc = interface.ERC20(vault.token())

    print (vault.governance())

    wrapper = acc.deploy(AffiliateTokenGatedUpgradeable)
    wrapper.initialize(vault.token(), registry, "hi", "ss", acc, True, vault)
    
    depositA = 1 * 1e8
    wbtc.transfer(minow, 1*1e8, {'from': whale})
    balanceBefore = wbtc.balanceOf(whale)
    wbtc.approve(wrapper, 2**256-1, {'from': minow})
    wrapper.depositFor(minow, depositA, {'from': minow})

    #now share price is divergent
    underStrat.harvest({'from': acc})
    chain.mine(1)
    chain.sleep(1)
    wbtc.approve(wrapper, 2**256-1, {'from': whale})
    wrapper.depositFor(whale, depositA, {'from': whale})
    assert wrapper.balanceOf(whale) < wrapper.balanceOf(minow)

    chain.sleep(100000)
    chain.mine(1)
    wrapper.withdraw( {'from': whale})
    assert wbtc.balanceOf(whale) + 10 > balanceBefore and wbtc.balanceOf(whale) - 10 < balanceBefore
    wrapper.withdraw( {'from': minow})
    assert wbtc.balanceOf(minow) > depositA + 100