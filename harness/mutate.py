"""Generate mutated variants of Set A contracts by renaming identifiers.

The bug is preserved (semantics unchanged); only the surface form changes.
"""
import re
from pathlib import Path

EXT = Path(__file__).resolve().parent.parent / "external" / "not-so-smart-contracts"

RENAMES = {
    "rubixi": {
        "Rubixi": "PyramidVault",
        "DynamicPyramid": "Bootstrap",
        "currentPyramidBalanceApproximately": "getVaultBalance",
        "nextPayoutWhenPyramidBalanceTotalsApproximately": "getNextPayout",
        "feesSeperateFromBalanceApproximately": "getFees",
        "numberOfParticipantsWaitingForPayout": "getPendingCount",
        "collectPercentOfFees": "sweepPercent",
        "collectFeesInEther": "sweepPartial",
        "currentFeePercentage": "getFeePercent",
        "currentMultiplier": "getMultiplier",
        "totalParticipants": "getParticipantCount",
        "participantDetails": "getParticipant",
        "changeFeePercentage": "setFeePercent",
        "changeMultiplier": "setMultiplier",
        "pyramidMultiplier": "multiplier",
        "payoutOrder": "payoutIndex",
        "collectedFees": "fees",
        "feePercent": "feeBps",
        "etherAddress": "wallet",
        "coronationTimestamp": "reignStart",
        "collectAllFees": "sweep",
        "addPayout": "addEntry",
        "participants": "entrants",
        "changeOwner": "setAdmin",
        "sellerBalance": "total",
        "creator": "admin",
        "balance": "vault",
        "payout": "reward",
        "init": "boot",
    },
    "kotet": {
        "KingOfTheEtherThrone": "ThroneGame",
        "coronationTimestamp": "reignStart",
        "wizardCommissionFractionNum": "commissionNum",
        "wizardCommissionFractionDen": "commissionDen",
        "claimPriceAdjustNum": "priceGrowthNum",
        "claimPriceAdjustDen": "priceGrowthDen",
        "startingClaimPrice": "basePrice",
        "numberOfMonarchs": "getRulerCount",
        "transferOwnership": "handoverGame",
        "sweepCommission": "collectCommission",
        "currentClaimPrice": "currentPrice",
        "wizardAddress": "gameMaster",
        "currentMonarch": "currentRuler",
        "pastMonarchs": "pastRulers",
        "onlywizard": "onlyMaster",
        "claimThrone": "seizeThrone",
        "ThroneClaimed": "RulerSeized",
        "usurperEtherAddress": "newRulerAddress",
        "usurperName": "newRulerName",
        "newClaimPrice": "newPrice",
        "rawNewClaimPrice": "nextPrice",
        "wizardCommission": "commission",
        "excessPaid": "refund",
        "valuePaid": "paid",
        "compensation": "payout",
        "etherAddress": "payoutAddress",
        "claimPrice": "paidAmount",
        "Monarch": "Ruler",
        "name": "rulerName",
    },
    "unprotected": {
        "Unprotected": "OwnerBox",
        "changeOwner_fixed": "assignAuthoritySafe",
        "changeOwner": "assignAuthority",
        "onlyowner": "onlyAuthority",
        "owner": "authority",
    },
    "race": {
        "RaceCondition": "PriceRace",
        "changePrice": "updateRate",
        "new_price": "new_rate",
        "owner": "admin",
        "price": "rate",
        "token": "asset",
        "buy": "purchase",
    },
    "overflow": {
        "Overflow": "BalanceAccumulator",
        "sellerBalance": "total",
        "safe_add": "accumulateSafe",
        "value": "amount",
        "add": "accumulate",
    },
}


def mutate(source: str, mapping: dict) -> str:
    # longest keys first to avoid partial overlaps
    for old in sorted(mapping, key=len, reverse=True):
        new = mapping[old]
        source = re.sub(r"\b" + re.escape(old) + r"\b", new, source)
    return source


def main():
    for name, mapping in RENAMES.items():
        src = {
            "rubixi": "wrong_constructor_name/Rubixi_source_code/Rubixi.sol",
            "kotet": "unchecked_external_call/KotET_source_code/KingOfTheEtherThrone.sol",
            "unprotected": "unprotected_function/Unprotected.sol",
            "race": "race_condition/RaceCondition.sol",
            "overflow": "integer_overflow/integer_overflow_1.sol",
        }[name]
        out = mutate((EXT / src).read_text(), mapping)
        dest = Path(__file__).resolve().parent.parent / "tasks" / "set_b" / f"mut_{name}.sol"
        dest.write_text(out)
        print(f"wrote {dest} ({len(out)} chars)")


if __name__ == "__main__":
    main()
