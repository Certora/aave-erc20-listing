using ERC20Helper as erc20helper;

methods {
    function _.name() external => DISPATCHER(true);
    function _.symbol() external => DISPATCHER(true);
    function _.decimals() external => DISPATCHER(true);
    function _.totalSupply() external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.allowance(address,address) external => DISPATCHER(true);
    function _.approve(address,uint256) external => DISPATCHER(true);
    function _.transfer(address,uint256) external => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external => DISPATCHER(true);

	function erc20helper.tokenBalanceOf(address, address) external returns (uint256) envfree;

	function _.mint(address,uint256) external => DISPATCHER(true);
	function _.burn(address,uint256) external => DISPATCHER(true);
	function _.owner() external => DISPATCHER(true);
}

/*

	Functions to cover:
	- balanceOf
		- maybe, it is just a getter, so probably not
	- transfer (DONE for now)
		- rules: transferDoesTheTransfer
		- we check the possibly revert causes
		- we check that the balance is indeed transfered
		- the fact that it cannot change the totalSupply is covered by another rule & invariant
		- we check that transfer does not affect a third 
	- approve (TODO)
		- rules:
		- check revert causes
		- check nonzero address (a revert cause)
		- check that it does not affect a third party
	

*/

/*
	Assume we want to do two seemingly independet transfers:
	1. transfer [amount_A] from [e_A.msg.sender] to [to_A], and
	2. transfer [amount_B] from [e_B.msg.sender] to [to_B],
	such that [e_A.msg.sender != e_B.msg.sender] and [to_A != to_B]. 
	This rule checks that the fact whether the transfer A reverts or not
	does not depend on the order of the two transfers. (the case for B follows).
*/
rule orderOfIndependentTransfersDoesNotAffectReverting(
	env e_A, 
	address to_A, 
	uint256 amount_A,
	env e_B, 
	address to_B,
	uint256 amount_B
) {
	require (e_A.msg.sender != e_B.msg.sender) || 
		(to_mathint(balanceOf(e_A, e_A.msg.sender)) >= amount_A + amount_B);
	require to_B != e_A.msg.sender;
	require (to_A != to_B) ||
		(to_mathint(balanceOf(e_A, to_A)) + amount_A + amount_B <= max_uint);


	storage initialStorage = lastStorage;

	transfer@withrevert(e_A, to_A, amount_A);
	bool ARevertedAtS1 = lastReverted;

	transfer(e_B, to_B, amount_B) at initialStorage;
	transfer@withrevert(e_A, to_A, amount_A);
	bool ARevertedAtS2 = lastReverted;

	assert (ARevertedAtS1 == ARevertedAtS2);
	// the other assert, over B, should be symteric, so no need to prove.
}

/*
	Here we cover only the case where e.msg.sender != to. The case when e.msg.sender is handled by [transferToMyself].
	In particular, we check that:
		1. we cover all the rever cases
		2. the amount is indeed transfered
*/

rule transferDoesTheTransfer(address to, uint256 amount) {
	env e;

	require e.msg.sender != to;
	uint256 initialFromBalance = balanceOf(e, e.msg.sender);
	uint256 initialToBalance = balanceOf(e, to);
	
	bool insufficientFunds = initialFromBalance < amount;
	//the overflow should not be possible if the invariant [somOfBalancesEqualsTotalSupply] holds.
	//So, alternatively, we should require the invariant here. 
	bool wouldOverflow =  initialToBalance + amount > max_uint;
	bool nonZeroAddress = (e.msg.sender == 0) || (to == 0 );
	
	transfer@withrevert(e, to, amount);

	if(lastReverted){	
		//check that it reverted due to one of the expected cases
		assert insufficientFunds || wouldOverflow || nonZeroAddress;
	} else {
		//check that none of the cases that we belive should trigger a revert did not apply
		assert !(insufficientFunds || wouldOverflow || nonZeroAddress);		
		//check that the balance was indeed transfered
		assert to_mathint(balanceOf(e, to)) == initialToBalance + amount;
		assert to_mathint(balanceOf(e, e.msg.sender)) == initialFromBalance - amount;		
	}
}

/*
	Check that:
		1. If I transfer the tokens to myself, my balance does not change. 
		2. that we cover all revert cases.
*/
rule transferToMyself(uint256 amount) {
	env e;
	uint256 balanceBefore = balanceOf(e, e.msg.sender);
	bool zeroAddress = e.msg.sender == 0;
	transfer@withrevert(e, e.msg.sender, amount);
	if(lastReverted) {	
		assert zeroAddress || balanceBefore < amount;
	} else {
		assert !(zeroAddress || balanceBefore < amount);
		assert balanceOf(e, e.msg.sender) == balanceBefore;
	}
	
}



/*
	The below function just calls (dispatch) all methods (an arbitrary one) from the contract, 
	using given [env e], [address from] and [address to].
	We use this function in several rules, including: . The usecase is typically to show that 
	the call of the function does not affect a "property" of a third party (i.e. != e.msg.sender, from, to),
	such as the balance or allowance.  

*/
function callFunctionWithParams(env e, method f, address from, address to) {
	uint256 amount;

	if (f.selector == sig:transfer(address, uint256).selector) {
		transfer(e, to, amount);
	} else if (f.selector == sig:allowance(address, address).selector) {
		allowance(e, from, to);
	} else if (f.selector == sig:approve(address, uint256).selector) {
		approve(e, to, amount);
	} else if (f.selector == sig:transferFrom(address, address, uint256).selector) {
		transferFrom(e, from, to, amount);
	} else if (f.selector == sig:increaseAllowance(address, uint256).selector) {
		increaseAllowance(e, to, amount);
	} else if (f.selector == sig:decreaseAllowance(address, uint256).selector) {
		decreaseAllowance(e, to, amount);
	} else if (f.selector == sig:mint(address, uint256).selector) {
		mint(e, to, amount);
	} else if (f.selector == sig:burn(address, uint256).selector) {
		burn(e, from, amount);
	} else {
		calldataarg args;
		f(e, args);
	}
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the balance of [thirdParty].
	Intuitively, we target e.g. the case where a transfer of tokens [from] -> [to]
	changes the balance of [thirdParty]. 
*/
rule doesNotAffectAThirdPartyBalance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 thirdBalanceBefore = balanceOf(e, thirdParty);
	callFunctionWithParams(e, f, from, to);

	assert balanceOf(e, thirdParty) == thirdBalanceBefore;
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the allowance of [thirdParty] w.r.t a [thirdPartySpender].
*/
rule doesNotAffectAThirdPartyAllowance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;
	address thirdPartySpender;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 spenderAllowanceBefore = allowance(e, thirdParty, thirdPartySpender);
	callFunctionWithParams(e, f, from, to);

	assert allowance(e, thirdParty, thirdPartySpender) == spenderAllowanceBefore;
}



ghost mathint sumOfBalances {
	init_state axiom sumOfBalances == 0;
}

hook Sstore _balances[KEY address addr] uint256 new_balance (uint256 old_balance) STORAGE {	
	sumOfBalances = sumOfBalances + to_mathint(new_balance) - to_mathint(old_balance);
}

hook Sload uint256 v _balances[KEY address addr] STORAGE {	
	require to_mathint(v) <= sumOfBalances;
}

invariant somOfBalancesEqualsTotalSupply(env e)
	sumOfBalances == to_mathint(totalSupply(e));




/*
	List of functions we assume are allowd to change the [totalSupply]
*/

definition canChangeTotalSupply(method f ) returns bool = 
	f.selector == sig:mint(address,uint256).selector ||
	f.selector == sig:burn(address,uint256).selector
	;

/*
	Functions that are not not allowed to change the [totalSupply] (via [canChangeTotalSupply()])
	do not change the total balance.
*/
rule totalSuppyDoesNotChange(method f) filtered {f -> !canChangeTotalSupply(f) } 
{		
	env e;
	calldataarg args;

	uint256 before = totalSupply(e);
	f(e,args);
    uint256 after = totalSupply(e);
	assert before == after;
}

/*
	Mint is one of the functions that can change the total balance (can it?). So, we check whether it does it correctly.
*/
rule mintIncreasesTheTotalBalanceCorrectly(address to, uint256 amount) {
	env e;
	
	uint256 before = totalSupply(e); //Question: how does the type cast work here?
	mint(e, to, amount);
	uint256 after = totalSupply(e);
	
	assert assert_uint256(before + amount) == after; 
}

rule mintCanBeDoneOnAnyAddresWithAnyReasonableAmount(address to, uint256 amount) {
	env e;

	require e.msg.sender == _owner(e);
	//we can, instead, require the invariant somOfBalancesEqualsTotalSupply here I suppose. But that might be a too strong requirement. 
	require totalSupply(e) + amount < max_uint; 
	require balanceOf(e, to) + amount < max_uint;
	require to != 0;
	
	mint@withrevert(e, to, amount);

	assert !lastReverted;
}

/*
	Burn is one of the functions that can change the total balance (can it?). So, we check whether it does it correctly.
*/
rule burnDecreasesTheTotalBalanceCorrectly(address from, uint256 amount) {
	env e;
	
	uint256 before = totalSupply(e); 
	burn(e, from, amount);
	uint256 after = totalSupply(e);
	
	assert amount <= before; //just checking if the compiler (with safe math) handles underflows correctly
	assert assert_uint256(before - amount) == after; 
}

rule burnCanBeDoneOnAnyAddresWithAnyReasonableAmount(address from, uint256 amount) {
	env e;

	require e.msg.sender == _owner(e);
	require balanceOf(e, from) >= amount;
	//we can, instead, require the invariant somOfBalancesEqualsTotalSupply here I suppose. But that might be a too strong requirement. 
	require amount <= totalSupply(e); 
	require from != 0;
	
	burn@withrevert(e, from, amount);

	assert !lastReverted;
}


/*
*
*	THE ORIGINAL SPEC
*
*/


/* 
	Property: Find and show a path for each method.
*/
rule reachability(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	satisfy true;
}

/* 
   	Property: Define and check functions that should never revert
	Notice:  use f.selector to state which functions should not revert,e.g.f.selector == sig:balanceOf(address).selector 
*/  
definition nonReveritngFunction(method f ) returns bool = true; 

rule noRevert(method f) filtered {f -> nonReveritngFunction(f) }
{
	env e;
	calldataarg arg;
    //consider auto filtering for non-payable functions 
	require e.msg.value == 0; 
	f@withrevert(e, arg); 
	assert !lastReverted, "method should not revert";
}


/* 
    Property: Checks if a function can be frontrun 
    Notice: Can be enhanced to check more than one function as rules can be double-parameteric
*/ 
rule simpleFrontRunning(method f, method g) filtered { f-> !f.isView, g-> !g.isView }
{
	env e1;
	calldataarg arg;

	storage initialStorage = lastStorage;
	f(e1, arg); 
	

	env e2;
	calldataarg arg2;
	require e2.msg.sender != e1.msg.sender;
	g(e2, arg2) at initialStorage; 

	f@withrevert(e1, arg);
	bool succeeded = !lastReverted;

	assert succeeded, "should be called also if frontrunned";
}


/** 
    @title -   This rule find which functions are privileged.
    @notice A function is privileged if there is only one address that can call it.
    @dev The rules finds this by finding which functions can be called by two different users.
*/

rule privilegedOperation(method f, address privileged)
{
	env e1;
	calldataarg arg;
	require e1.msg.sender == privileged;

	storage initialStorage = lastStorage;
	f@withrevert(e1, arg); // privileged succeeds executing candidate privileged operation.
	bool firstSucceeded = !lastReverted;

	env e2;
	calldataarg arg2;
	require e2.msg.sender != privileged;
	f@withrevert(e2, arg2) at initialStorage; // unprivileged
	bool secondSucceeded = !lastReverted;

	assert  !(firstSucceeded && secondSucceeded), "function is privileged";
}


rule decreaseInSystemEth(method f) {
   
    uint256 before = nativeBalances[currentContract];

    env e;
	calldataarg arg;
    f(e, arg);

    uint256 after = nativeBalances[currentContract];

    assert after >= before ||  false ; /* fill in cases where eth can decrease */ 
}


rule decreaseInERC20(method f) {
    address token;
    uint256 before = erc20helper.tokenBalanceOf(token, currentContract);

    env e;
	calldataarg arg;
    f(e, arg);

    uint256 after = erc20helper.tokenBalanceOf(token, currentContract);

    assert after >= before ||  false ; /* fill in cases eth can decrease */ 

} 