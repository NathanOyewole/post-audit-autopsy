"""Build the eval task set.

Set A: compact real/relevant vulnerable contracts.
Set B: mutated variants (same bugs, renamed/restructured, size-matched).
Set C: large real contracts (complexity control).
Controls: benign contracts.
"""
import json
from pathlib import Path

import mutate as mut

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "external" / "not-so-smart-contracts"
TASKS = ROOT / "tasks"


def read(p):
    return (EXT / p).read_text()


def rename_text(text, mapping):
    return mut.mutate(text, mapping)


# (id, source path, reference, rename-map key)
SET_A_SPECS = [
    (
        "rubixi",
        "wrong_constructor_name/Rubixi_source_code/Rubixi.sol",
        {
            "root_cause": "The contract was written for Solidity <0.5 and names its constructor `DynamicPyramid` instead of `Rubixi`. Because the contract is actually named `Rubixi`, the constructor never runs, so `creator` is never set. The fallback function calls the private `init()` path, and the old-style constructor name mismatch means the privileged initialization can be triggered by anyone.",
            "impact": "An attacker can become the creator/admin and drain collected fees, or hijack the contract's privileged functions.",
            "exploit": "Call the function that was meant to be the constructor (DynamicPyramid) to set creator = attacker, then call collectAllFees()/changeOwner() as the owner.",
            "fix": "Rename the constructor to match the contract name (or use the `constructor` keyword) so it runs exactly once at deploy and only the deployer becomes creator; make init() protected.",
        },
        "rubixi",
    ),
    (
        "kotet",
        "unchecked_external_call/KotET_source_code/KingOfTheEtherThrone.sol",
        {
            "root_cause": "The contract uses low-level `.send()` without checking the return value (claimThrone refunds and compensation, and sweepCommission). If the recipient is a contract that rejects ETH, the send silently fails while the contract's state has already advanced, breaking accounting and potentially locking funds.",
            "impact": "Funds can become permanently stuck or the throne accounting can desync, letting an attacker claim more than entitled or lock compensation.",
            "exploit": "A monarch sets their compensation address to a contract that reverts on receive, causing the payout send to fail silently while the contract still marks the payout as made.",
            "fix": "Check the return value of every external call; use `require(addr.send(...))` or `(bool ok, ) = addr.call{value: ...}(''); require(ok);`.",
        },
        "kotet",
    ),
    (
        "unprotected",
        "unprotected_function/Unprotected.sol",
        {
            "root_cause": "changeOwner() has no access-control modifier. Anyone can call it and set themselves (or any address) as the owner, since `onlyowner` is defined but never applied to the state-changing function.",
            "impact": "Full loss of privileged control over the contract; the attacker becomes the owner and can perform any owner-only action.",
            "exploit": "Call changeOwner(attackerAddress) from any wallet; the owner is overwritten with no authorization check.",
            "fix": "Apply the `onlyowner` modifier to changeOwner (as in changeOwner_fixed), or use OpenZeppelin Ownable with onlyOwner.",
        },
        "unprotected",
    ),
    (
        "race",
        "race_condition/RaceCondition.sol",
        {
            "root_cause": "buy() is front-runnable: it pulls tokens at the current `price` and only then updates `price` and `owner`. The owner can front-run a buyer with changePrice() to raise the price, or a buyer can front-run the owner's changePrice() to buy at the old price.",
            "impact": "The owner can extract more tokens than a buyer expects, or a buyer can buy at a stale price, breaking the intended pricing.",
            "exploit": "The owner sees buy(new_price) in the mempool and submits changePrice(higher) with a higher gas price so it mines first; the buyer then pays the higher price while the contract state updates afterward.",
            "fix": "Use commit-reveal or an atomic price update; require the caller to accept the current price in the same transaction and update state before external calls.",
        },
        "race",
    ),
    (
        "overflow",
        "integer_overflow/integer_overflow_1.sol",
        {
            "root_cause": "Compiled with Solidity ^0.4.15, which has no built-in overflow checks. add() does `sellerBalance += value` with no require that the sum did not wrap, so a large value overflows the total.",
            "impact": "An attacker can overflow the balance accounting, wrapping the total and corrupting the contract's state.",
            "exploit": "Call add(type(uint).max) to wrap sellerBalance to a small value, desyncing the accounting.",
            "fix": "Use Solidity ^0.8.0 (built-in checks) or SafeMath, or add `require(sellerBalance + value >= sellerBalance)` as in safe_add().",
        },
        "overflow",
    ),
]

SET_C_SPECS = [
    (
        "dao",
        "reentrancy/DAO_source_code/DAO.sol",
        {
            "root_cause": "Classic reentrancy: the split/withdraw path sends ETH to the caller before updating the caller's token balance (checks-effects-interactions violated). A malicious contract's fallback can re-enter recursively while the balance still reflects the old value.",
            "impact": "An attacker can drain a large portion of the DAO's ETH. This led to ~$60M loss and the ETH/ETC hard fork.",
            "exploit": "A token holder deploys a contract whose fallback re-enters the DAO's split/withdraw function repeatedly, claiming more ETH than its balance allows before the state is updated.",
            "fix": "Follow checks-effects-interactions: update balances before sending ETH, and/or add a reentrancy guard.",
        },
    ),
    (
        "spankchain",
        "reentrancy/SpankChain_source_code/SpankChain.sol",
        {
            "root_cause": "Reentrancy in the payment/channel logic: an external call to the caller is made before the internal accounting is finalized, allowing a malicious token contract (or callback) to re-enter and mint/transfer more tokens than it should.",
            "impact": "Attacker can drain the token contract or mint tokens beyond their entitlement.",
            "exploit": "A caller uses a malicious token with a transfer hook to re-enter the SpankChain token functions during a transfer, exploiting stale balances.",
            "fix": "Apply checks-effects-interactions and a reentrancy guard to all state-changing external functions.",
        },
    ),
]

CONTROLS = [
    (
        "ctl_erc20",
        '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint) public balanceOf;
    uint public totalSupply;

    constructor(uint supply) {
        totalSupply = supply;
        balanceOf[msg.sender] = supply;
    }

    function transfer(address to, uint amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "insufficient");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}
''',
        {
            "root_cause": "No vulnerability. Balance is checked before subtraction and updated atomically; no external calls, no privileged functions.",
            "impact": "None.",
            "exploit": "None.",
            "fix": "None required.",
        },
    ),
    (
        "ctl_vault",
        '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SafeVault {
    mapping(address => uint) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        balances[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
    }
}
''',
        {
            "root_cause": "No vulnerability. The balance is decremented before the external call (checks-effects-interactions), and the amount is bounded by the caller's balance.",
            "impact": "None.",
            "exploit": "None.",
            "fix": "None required.",
        },
    ),
]


def write(tid, set_name, name, source, reference, source_file=""):
    d = TASKS / set_name
    d.mkdir(parents=True, exist_ok=True)
    with open(d / f"{tid}.json", "w") as f:
        json.dump({
            "id": tid, "name": name, "set": set_name,
            "source": source, "reference": reference, "source_file": source_file,
        }, f, indent=2)
    print(f"wrote {set_name}/{tid}.json ({len(source)} chars)")


def main():
    for tid, path, ref, map_key in SET_A_SPECS:
        write(tid, "set_a", tid, read(path), ref, f"external/not-so-smart-contracts/{path}")
    for tid, path, ref, map_key in SET_A_SPECS:
        mapping = mut.RENAMES[map_key]
        src = mut.mutate(read(path), mapping)
        ref_b = {k: rename_text(v, mapping) for k, v in ref.items()}
        write(f"mut_{tid}", "set_b", f"mutated {tid}", src, ref_b, f"mutated from {path}")
    for tid, path, ref in SET_C_SPECS:
        write(tid, "set_c", tid, read(path), ref, f"external/not-so-smart-contracts/{path}")
    for tid, src, ref in CONTROLS:
        write(tid, "controls", tid, src, ref, "hand-written benign")


if __name__ == "__main__":
    main()
