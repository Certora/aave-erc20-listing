ghost mapping(address => uint256) balances;
ghost mathint sumOfBalances {
    init_state axiom sumOfBalances == 0;
}

hook Sstore _balances[KEY address u] uint256 newBalance (uint256 oldBalance) STORAGE {
    balances[u] = newBalance;
    sumOfBalances = sumOfBalances + newBalance - oldBalance;
}

//hook Sload uint256 balance _balances[KEY address u] STORAGE {
//    balances[u] = _balances[u];
//}

// totalSupply == sum of all balances

invariant sumOfBalancesEqualsTotalSupply(env e)
    to_mathint(totalSupply(e)) == sumOfBalances;

// Correct transfer is possible
// Unit test
rule transferIsPossible {
	address recipient;
	uint256 amount;
	env e;
    require e.msg.value == 0;

	uint256 balance_sender_before = balanceOf@withrevert(e, e.msg.sender);
    assert !lastReverted, "balanceOf reverted";

	require (recipient != 0);
    require (e.msg.sender != 0);
    require (balance_sender_before >= amount);
    require (recipient != e.msg.sender);

    approve@withrevert(e, e.msg.sender, amount);
    assert !lastReverted, "approve reverted";
	require (allowance(e, e.msg.sender, e.msg.sender) >= amount);
    
    require balanceOf(e, recipient) == balances[recipient];
    require totalSupply(e) - amount >= 0; // In mathint
    require assert_uint256(totalSupply(e) - amount) >= balances[recipient];

	transfer@withrevert(e, recipient, amount);
	assert !lastReverted, "transfer reverted when ${e.msg.sender} sent to ${recipient}";

}

// Unit test
// Risk analysis
rule noFeeOnTransferFrom(address sender, address receiver, uint256 amount) {
    env e;
    require e.msg.value == 0;

    require sender != receiver;
    require sender != 0;
    require receiver != 0;
    require e.msg.sender != 0;

    require balanceOf(e, sender) >= amount;
    require allowance(e, sender, e.msg.sender) >= amount;
    uint256 balanceBefore = balanceOf(e, receiver);

    require totalSupply(e) - amount >= 0;
    require assert_uint256(totalSupply(e) - amount) >= balanceBefore;

    transferFrom@withrevert(e, sender, receiver, amount);

    uint256 balanceAfter = balanceOf(e, receiver);
    assert balanceAfter == assert_uint256(balanceBefore + amount), "balance after is incorrect";
}

// Cannot send more than spending limit
// risk analysis
rule noOverspending(address spender, address receiver, uint256 limit) {
    env e;
    require e.msg.value == 0;
    require spender != 0;
    require receiver != 0;
    require e.msg.sender != 0;

    approve@withrevert(e, spender, limit);
    assert !lastReverted, "approve failed";

    uint256 actual;

    require actual > limit;

    env e2;
    require e2.msg.sender != e.msg.sender;
    require e2.msg.sender == spender;
    require e2.msg.value == 0;

    transferFrom@withrevert(e2, e.msg.sender, receiver, actual);
    assert lastReverted, "Overspent";
}

// Authorised spender can spend
// Unit test
rule authorisedCanSpend(address spender, address receiver) {
    env e;
    require e.msg.value == 0;
    require spender != 0;
    require receiver != 0;
    require e.msg.sender != 0;

    uint256 limit;

    approve@withrevert(e, spender, limit);
    assert !lastReverted, "approve failed";

    env e2;
    require e2.msg.sender != e.msg.sender;
    require e2.msg.sender == spender;
    require e2.msg.value == 0;

    uint256 actual;
    require actual <= limit;

    require balanceOf(e, e.msg.sender) >= limit;

    require totalSupply(e) - actual >= 0;
    require assert_uint256(totalSupply(e) - actual) >= balanceOf(e2, receiver);


    transferFrom@withrevert(e2, e.msg.sender, receiver, actual);
    assert !lastReverted, "authorised transfer failed";
}

// Unit test
rule transferFromDoesntChangeTotalSupply(address alice, address bob, uint256 amount) {
    env e;
    require e.msg.value == 0;
    uint256 supplyBefore = totalSupply@withrevert(e);

    transferFrom@withrevert(e, alice, bob, amount);

    uint256 supplyAfter = totalSupply@withrevert(e);

    assert supplyBefore == supplyAfter;
}

// Unit test
rule mintIncreasesTotalSupply() {
    address destination;
    uint256 amount;

    env e;
    require e.msg.sender == currentContract.deployer;
    require e.msg.value == 0;
    require destination != 0;

    uint256 prevTotalSupply = totalSupply@withrevert(e);
    assert !lastReverted, "first totalSupply reverted";
    require prevTotalSupply + amount <= max_uint256;

    uint256 destinationFunds = balanceOf@withrevert(e, destination);
    assert !lastReverted, "balanceOf destitination reverted";
    require destinationFunds <= prevTotalSupply;

    mint@withrevert(e, destination, amount);
    assert !lastReverted, "mint reverted";

    env e2;
    require e2.msg.value == 0;

    uint256 newTotalSupply = totalSupply@withrevert(e2);
    assert !lastReverted, "second totalSupply reverted";

    assert newTotalSupply == assert_uint256(prevTotalSupply + amount);
}

// Only deployer can mint
// Unit test
// risk analysis
rule onlyDeployerCanMint() {
    address destination;
    uint256 amount;
    address nonDeployer;

    require nonDeployer != currentContract.deployer;

    env e;
    require e.msg.sender == nonDeployer;
    mint@withrevert(e, destination, amount);
    assert lastReverted, "nondeployer could mint";
}