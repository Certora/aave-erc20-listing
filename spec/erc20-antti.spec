//methods {
//    function balanceOf(address) external returns (uint256) envfree;
//    function totalSupply() external returns uint256 envfree;
//}

// Fails in a way I don't understand.  My theory is that it's because `e.msg.sender=ERC20` and `ERC20=ERC20`
rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
    env e;
    require alice != bob;
    require e.msg.value == 0;

    require allowance(e, alice, e.msg.sender) >= amount;
    uint256 balanceBefore = balanceOf(e, bob);

    transferFrom@withrevert(e, alice, bob, amount);

    uint256 balanceAfter = balanceOf(e, bob);
    assert balanceAfter == assert_uint256(balanceBefore + amount);
}

// This one passes.  Probably not vacuously?
rule transferFromDoesntChangeTotalSupply(address alice, address bob, uint256 amount) {
    env e;
    require e.msg.value == 0;
    uint256 supplyBefore = totalSupply@withrevert(e);

    transferFrom@withrevert(e, alice, bob, amount);

    uint256 supplyAfter = totalSupply@withrevert(e);

    assert supplyBefore == supplyAfter;
}

// This passes
rule weird(address alice, address bob, uint256 amount) {
    env e;
    require e.msg.value == 0;

    uint256 balanceBefore = balanceOf@withrevert(e, alice);
    assert !lastReverted;
}

// This passes
rule totalSupplyRevert {
    env e;
    require e.msg.value == 0;
    totalSupply@withrevert(e);
    assert !lastReverted;
}

// This fails, but I don't know why.
rule transferRevert {
	address recipient;
	uint256 amount;
	env e;
    require e.msg.value == 0;

	uint256 balance_sender_before = balanceOf@withrevert(e, e.msg.sender);
    assert !lastReverted, "balanceOf reverted";

    // Need to require here something like ERC20 != e.msg.sender.
    // ERC20 is an address where the contract is deployed, probably.
    // What is this in e?

	require (recipient != 0);
    require (e.msg.sender != 0);
    require (balance_sender_before >= amount);
    require (recipient != e.msg.sender);

    approve@withrevert(e, e.msg.sender, amount);
    assert !lastReverted, "approve reverted";
	require (allowance(e, e.msg.sender, e.msg.sender) >= amount);

	transfer@withrevert(e, recipient, amount);
	assert !lastReverted, "transfer reverted when ${e.msg.sender} sent to ${recipient}";
}

