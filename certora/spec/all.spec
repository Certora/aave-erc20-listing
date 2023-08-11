using ERC20Helper as erc20helper;

methods {
    
    function totalSupply() external returns uint256 envfree;
    function balanceOf(address) external returns uint256 envfree;
	function allowance(address,address) external returns uint256 envfree;
    function approve(address,uint256) external returns bool;
	function increaseAllowance(address,uint256) external returns bool;
    function transfer(address,uint256) external returns bool;
    function transferFrom(address,address,uint256) external returns bool;

	function _owner() external returns address;

	function erc20helper.tokenBalanceOf(address, address) external returns (uint256) envfree;
}


//
//
// Rules that were here originally presented
//
//

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

definition canIncreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:increaseAllowance(address,uint256).selector;

definition canDecreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:decreaseAllowance(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector;

definition canIncreaseBalance(method f ) returns bool = 
	f.selector == sig:mint(address,uint256).selector || 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector;

definition canDecreaseBalance(method f ) returns bool = 
	f.selector == sig:burn(address,uint256).selector || 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector;

definition priveledgedFunction(method f ) returns bool = 
	f.selector == sig:mint(address,uint256).selector || 
	f.selector == sig:burn(address,uint256).selector;

definition canIncreaseTotalSupply(method f ) returns bool = 
	f.selector == sig:mint(address,uint256).selector;

definition canDecreaseTotalSupply(method f ) returns bool = 
	f.selector == sig:burn(address,uint256).selector;


// rule noRevert(method f) filtered {f -> nonReveritngFunction(f) }
// {
// 	env e;
// 	calldataarg arg;
//     //consider auto filtering for non-payable functions 
// 	require e.msg.value == 0; 
// 	f@withrevert(e, arg); 
// 	assert !lastReverted, "method should not revert";
// }

// /* 
//     Property: Checks if a function can be frontrun 
//     Notice: Can be enhanced to check more than one function as rules can be double-parameteric
// */ 
// rule simpleFrontRunning(method f, method g) filtered { f-> !f.isView, g-> !g.isView }
// {
// 	env e1;
// 	calldataarg arg;

// 	storage initialStorage = lastStorage;
// 	f(e1, arg); 
	

// 	env e2;
// 	calldataarg arg2;
// 	require e2.msg.sender != e1.msg.sender;
// 	g(e2, arg2) at initialStorage; 

// 	f@withrevert(e1, arg);
// 	bool succeeded = !lastReverted;

// 	assert succeeded, "should be called also if frontrunned";
// }

// /** 
//     @title -   This rule find which functions are privileged.
//     @notice A function is privileged if there is only one address that can call it.
//     @dev The rules finds this by finding which functions can be called by two different users.
// */
// rule privilegedOperation(method f, address privileged) filtered {f -> priveledgedFunction(f) }
// {
// 	env e1;
// 	calldataarg arg;
// 	require e1.msg.sender == privileged;

// 	storage initialStorage = lastStorage;
// 	f@withrevert(e1, arg); // privileged succeeds executing candidate privileged operation.
// 	bool firstSucceeded = !lastReverted;

// 	env e2;
// 	calldataarg arg2;
// 	require e2.msg.sender != privileged;
// 	f@withrevert(e2, arg2) at initialStorage; // unprivileged
// 	bool secondSucceeded = !lastReverted;

// 	assert  !(firstSucceeded && secondSucceeded), "function is privileged";
// }

//can be removed
// rule decreaseInSystemEth(method f) {
   
//     uint256 before = nativeBalances[currentContract];

//     env e;
// 	calldataarg arg;
//     f(e, arg);

//     uint256 after = nativeBalances[currentContract];

//     assert after >= before ||  false ; /* fill in cases where eth can decrease */ 
// }

//Can be removed
// rule decreaseInERC20(method f) {
//     address token;
//     uint256 before = erc20helper.tokenBalanceOf(token, currentContract);

//     env e;
// 	calldataarg arg;
//     f(e, arg);

//     uint256 after = erc20helper.tokenBalanceOf(token, currentContract);

//     assert after >= before ||  false ; /* fill in cases eth can decrease */ 
// } 

//
//
// Our additional rules
//
//


//
//In the following part, we check if individual functions from the contract:
// 1. change the storage (balance, allowance,...) as we expect
// 2. revert if and only if we think they should revert
//
// Functions to cover: 
// - transfer(address recipient, uint256 amount)					DONE
// - approve(address spender, uint256 amount)						DONE
// - transferFrom(sender, address recipient, uint256 amount)		DONE
// - increaseAllowance(address spender, uint256 addedValue)			DONE
// - decreaseAllowance(address spender, uint256 subtractedValue)	DONE
// - mint(address account, uint256 amount)							DONE
// - burn(address account, uint256 amount)							DONE



rule burnRevertingConditions() {
    env e;
    address account;
    uint256 amount;
	require e.msg.value == 0;

    bool zeroAddress = account == 0;
    bool notEnoughBalance = balanceOf(account) < amount;
	bool notEnoughSupply = totalSupply(e) < amount;
	bool notTheOwner = e.msg.sender != _owner(e);
    bool shouldRevert = zeroAddress || notEnoughBalance || notEnoughSupply || notTheOwner;

    burn@withrevert(e, account, amount);
	assert lastReverted <=> shouldRevert;    
}

rule burnChangesBalanceCorrectly() {
    env e;
	address addr;
	uint256 amount;
    	
	uint256 before = balanceOf(addr);
	burn(e, addr, amount);
    assert balanceOf(addr) == assert_uint256(before - amount);
}

rule mintRevertingConditions() {
    env e;
    address account;
    uint256 amount;

	require e.msg.value == 0;

    bool zeroAddress = account == 0;
    bool balanceWouldOverflow = balanceOf(account) + amount > max_uint;
	bool totalSupplyWouldOverflow = totalSupply(e) + amount > max_uint;
    bool notTheOwner = e.msg.sender != _owner(e);
    bool shouldRevert = zeroAddress || balanceWouldOverflow || totalSupplyWouldOverflow || notTheOwner;

    mint@withrevert(e, account, amount);
	assert lastReverted <=> shouldRevert;    
}

rule mintChangesBalanceCorrectly() {
	env e;
	address addr;
	uint256 amount;

	uint256 before = balanceOf(addr);
	mint(e, addr, amount);
    assert balanceOf(addr) == assert_uint256(before + amount);
}


rule decreaseAllowanceChangesAllowanceCorrectly() {
	env e;
	address owner = e.msg.sender;
	address spender;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 subtractedValue;

	decreaseAllowance(e, spender, subtractedValue);
	assert allowance(owner, spender) == assert_uint256(allowedBefore - subtractedValue);	
}


rule decreaseAllowanceRevertingConditions() {
    env e;
	address spender;
	uint256 subtractedValue;
	require e.msg.value == 0;

	bool insufficientAllowance = allowance(e.msg.sender, spender) < subtractedValue;
	bool zeroAddress = e.msg.sender == 0 || spender == 0;
	bool shouldRevert = insufficientAllowance || zeroAddress;

	decreaseAllowance@withrevert(e, spender, subtractedValue);
	assert lastReverted <=> shouldRevert;
}


rule increaseAllowanceChangesAllowanceCorrectly() {
	env e;
	address owner = e.msg.sender;
	address spender;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 addedValue;
		
	increaseAllowance(e, spender, addedValue);
	assert allowance(owner, spender) == assert_uint256(allowedBefore + addedValue);	
}



rule increaseAllowanceRevertingConditions() {
    env e;
	address owner = e.msg.sender;
	address spender;
	require e.msg.value == 0;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 addedValue;

	bool wouldOverflow = allowedBefore + addedValue > max_uint;
	bool zeroAddress = e.msg.sender == 0 || spender == 0;
	bool shouldRevert = wouldOverflow || zeroAddress;

	increaseAllowance@withrevert(e, spender, addedValue);
	assert lastReverted <=> shouldRevert;
}

rule transferFromChangesBalanceAndAllowanceCorrectly() {
	env e;
	address spender = e.msg.sender;
	address owner;
	address recipient;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 ownerBalanceBefore = balanceOf(owner);
	uint256 recipientBalanceBefore = balanceOf(recipient);
	uint256 transfered;

	transferFrom(e, owner, recipient, transfered);

	assert allowedBefore == assert_uint256(allowance(owner, spender) + transfered);

	if(owner == recipient) {
		assert assert_uint256(ownerBalanceBefore) == balanceOf(owner);
	} else { 
		assert assert_uint256(ownerBalanceBefore - transfered) == balanceOf(owner);
		assert assert_uint256(recipientBalanceBefore + transfered) == balanceOf(recipient);
	}
}

//TODO: make sure the rule passes
rule transferFromRevertingConditions() {
    address owner;
	env e;
	require e.msg.value == 0;
	address spender = e.msg.sender;
	address recipient;

	uint256 allowed = allowance(owner, spender);
	uint256 transfered;

    bool zeroAddress = owner == 0 || recipient == 0;
    bool allowanceIsLow = allowed < transfered;
    bool notEnoughBalance = balanceOf(owner) < transfered;
    bool overflow = balanceOf(recipient) + transfered > max_uint;

    bool shouldRevert = zeroAddress || allowanceIsLow || notEnoughBalance || overflow;

    transferFrom@withrevert(e, owner, recipient, transfered);   
	assert lastReverted <=> shouldRevert;	
}


rule approveSetsAllowance() {
	env e;
	address spender;
	address owner = e.msg.sender;
	uint amount;

	approve(e, spender, amount);
	uint256 allowed = allowance(owner, spender);
	assert allowed == amount;
}

rule approveRevertingConditions() {
    env e;
	require e.msg.value == 0;
	address spender;
	address owner = e.msg.sender;
	uint amount;

	bool zeroAddress = owner == 0 || spender == 0;
	bool shouldRevert = zeroAddress;
	

	approve@withrevert(e, spender, amount);
	assert lastReverted <=> shouldRevert;
}


rule transferChangesBalanceCorrectly() {
	env e;
    address recipient;
    uint256 amount;

    mathint balanceOfRecipientBefore = balanceOf(recipient);
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);

    transfer(e, recipient, amount);

	if(e.msg.sender != recipient) {
		assert balanceOf(e, recipient) == assert_uint256(balanceOfRecipientBefore + amount);
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore - amount);
	} else {
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore);
	}
}

rule transferRevertingConditions {
	env e;
	address recipient;
	uint256 amount;
    require e.msg.value == 0;

	bool senderBalanceTooLow = balanceOf(e.msg.sender) < amount;
    bool zeroRecipient = recipient == 0;
    bool zeroSender = e.msg.sender == 0;
    bool senderIsRecipient = e.msg.sender == recipient;

    bool recipientBalanceOverflows = balanceOf(recipient) + amount > max_uint256 && !senderIsRecipient;

    bool shouldRevert = senderBalanceTooLow || zeroRecipient || zeroSender || recipientBalanceOverflows;

	transfer@withrevert(e, recipient, amount);
	assert lastReverted <=> shouldRevert;
}



//
// In the following part, we check for every variable (e.g. balances or allowance) that:
// 1. they can be changed only by privileged methods, and
// 2. the privileged methods might change variables corresponding only to the users 
// 	that call the methods
//


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
	The below function just calls (dispatch) all methods (an arbitrary one) from the contract, 
	using given [env e], [address from] and [address to].
	We use this function in several rules, including: . The usecase is typically to show that 
	the call of the function does not affect a "property" of a third party (i.e. != e.msg.sender, from, to),
	such as the balance or allowance.  

*/
function callFunctionWithParams(env e, method f, address from, address to) {
	uint256 amount;

	if (f.selector == sig:transfer(address, uint256).selector) {
		require from == e.msg.sender;
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


rule onlyAllowedMethodsMayChangeBalance(method f) {
	env e;
	address addr;
	uint256 balanceBefore = balanceOf(addr);
	calldataarg args;
	f(e,args);
	uint256 balanceAfter = balanceOf(addr);
	assert balanceAfter > balanceBefore => canIncreaseBalance(f), "should not increase balance";
	assert balanceAfter < balanceBefore => canDecreaseBalance(f), "should not decrease balance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
rule whoCanChangeBalance(method f) filtered {f -> canDecreaseBalance(f) || canIncreaseBalance(f) } {
	env e;
	address mightChange;
	address shouldNotChange;
	require mightChange != shouldNotChange;
	uint256 balanceBefore = balanceOf(shouldNotChange);
	
	uint256 amount;
	address receiver;
	require receiver != shouldNotChange;

	if(f.selector == sig:burn(address,uint256).selector) {
		burn(e, mightChange, amount);
	} else if(f.selector == sig:transfer(address,uint256).selector) {
		require e.msg.sender == mightChange;
		transfer(e, receiver, amount);
	} else if(f.selector == sig:transferFrom(address,address,uint256).selector) {
		transferFrom(e, mightChange, receiver, amount);
	} else if(f.selector == sig:mint(address,uint256).selector) {
		mint(e, mightChange, amount);
	} else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	assert balanceBefore == balanceOf(shouldNotChange);
}


rule onlyAllowedMethodsMayChangeAllowance(method f) {
	env e;
	address addr1;
	address addr2;
	uint256 allowanceBefore = allowance(addr1, addr2);
	calldataarg args;
	f(e,args);
	uint256 allowanceAfter = allowance(addr1, addr2);
	assert allowanceAfter > allowanceBefore => canIncreaseAllowance(f), "should not increase allowance";
	assert allowanceAfter < allowanceBefore => canDecreaseAllowance(f), "should not decrease allowance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
rule whoCanChangeAllowance(method f) filtered {f -> canDecreaseAllowance(f) || canIncreaseAllowance(f) } {
	env e;
	address owner;
	address spender;
	uint256 amountToChange;	

	address otherOwner;
	address otherSpender;
	uint256 theOtherAllowance = allowance(otherOwner, otherSpender);

	if(f.selector == sig:approve(address,uint256).selector) {		
		require owner == e.msg.sender;
		uint256 newAllowance;
		require to_mathint(amountToChange) == allowance(owner, spender) - newAllowance;
		approve(e, spender, newAllowance);
	} else if(f.selector == sig:increaseAllowance(address,uint256).selector) {
		require owner == e.msg.sender;
		increaseAllowance(e, spender, amountToChange);
	} else if(f.selector == sig:transferFrom(address,address,uint256).selector) {
		address recipient;
		require e.msg.sender == spender;
		transferFrom(e, owner, recipient, amountToChange);
	} else if(f.selector == sig:decreaseAllowance(address,uint256).selector) {
		require owner == e.msg.sender;
		decreaseAllowance(e, spender, amountToChange);
	} else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	uint256 newAllowanceOfTheOther = allowance(otherOwner, otherSpender);

	assert theOtherAllowance != newAllowanceOfTheOther <=>
		(otherSpender == spender && otherOwner == owner && amountToChange > 0);
}




rule onlyAllowedMethodsMayChangeTotalSupply(method f) {
	env e;
	uint256 totalSupplyBefore = totalSupply();
	calldataarg args;
	f(e,args);
	uint256 totalSupplyAfter = totalSupply();
	assert totalSupplyAfter > totalSupplyBefore => canIncreaseTotalSupply(f), "should not increase total supply";
	assert totalSupplyAfter < totalSupplyBefore => canDecreaseTotalSupply(f), "should not decrease total supply";
}


//
// Misc additional rules and invariants
//



invariant balanceOfZeroIsZero()
	balanceOf(0) == 0;

ghost mathint sumOfBalances {
	init_state axiom sumOfBalances == 0;
}

ghost mathint totalWithdraw {
	init_state axiom totalWithdraw == 0;
}

ghost mathint totalDeposit {
	init_state axiom totalDeposit == 0;
}
ghost mapping(address => bool) increasedBalances;


hook Sstore _balances[KEY address a] uint new_value (uint old_value) STORAGE {
	sumOfBalances = sumOfBalances + new_value - old_value;
	numberOfChangesOfBalances = numberOfChangesOfBalances + 1;

	if (new_value >= old_value) {
		totalDeposit = totalDeposit + new_value - old_value;
		increasedBalances[a] = true;
	} else {
		totalWithdraw = totalWithdraw + old_value - new_value;
		increasedBalances[a] = false;
	}
}

invariant totalSupplyIsSumOfBalances()
	to_mathint(totalSupply()) == sumOfBalances;

ghost mathint numberOfChangesOfBalances {
	init_state axiom numberOfChangesOfBalances == 0;
}

rule noMethodChangesMoreThanTwoBalances(method f) {
	env e;
	mathint numberOfChangesOfBalancesBefore = numberOfChangesOfBalances;
	calldataarg args;
	f(e,args);
	mathint numberOfChangesOfBalancesAfter = numberOfChangesOfBalances;
	assert numberOfChangesOfBalancesAfter <= numberOfChangesOfBalancesBefore + 2;
}

// We are checking just that if transfer(10) works, then also transfer(5);transfer(5) works. 
//We do not check the other direction (does not make sense becase of overflow reverts, i.e. does not hold)
rule transferIsOneWayAdditive() {
	env e;
	address recipient;
	uint256 amount_a; uint amount_b;
	mathint sum = amount_a + amount_b;
	require sum < max_uint256;
	storage init = lastStorage; // saves storage
	
	transfer(e, recipient, assert_uint256(sum));
	storage after1 = lastStorage;

	transfer@withrevert(e, recipient, amount_a) at init; // restores storage
		assert !lastReverted;	//if the transfer passed with sum, it should pass with both summands individually
	transfer@withrevert(e, recipient, amount_b);
		assert !lastReverted;
	storage after2 = lastStorage;

	assert after1[currentContract] == after2[currentContract];
}

//TODO: consider adding other additive rules

/*
	Property: Increase of an allowance followed by its decrease results in the same allowance as was at the beginning of transaction.
*/
rule IncreaseAllowanceAndDecreaseAllowanceAreInverse {
	uint256 allowance;	
	address other;
	env e;

    storage initialStorage = lastStorage;

	uint256 beforeIncrease1 = allowance(e, e.msg.sender, other);
	increaseAllowance(e, other, allowance);
	decreaseAllowance(e, other, allowance);	
	assert beforeIncrease1 == allowance(e, e.msg.sender, other);

    uint256 beforeIncrease2 = allowance(e, e.msg.sender, other) at initialStorage;	
	decreaseAllowance(e, other, allowance);	
	increaseAllowance(e, other, allowance);
    assert beforeIncrease2 == allowance(e, e.msg.sender, other);
}


definition isMintOrBurn(method f) returns bool =
       f.selector == sig:burn(address,uint256).selector || f.selector == sig:mint(address,uint256).selector;

/*
	Property: Burn after mint, or mint after burn with the same amount should not change balance of the account.
	Notice: Rule takes the method f and according to its type chooses to perform burn or mint.
*/
rule mintOrBurn(method f) filtered {f -> isMintOrBurn(f)} {
	address account;
	uint256 amount;
	env e;

    storage initialStorage = lastStorage;

	uint256 accountBefore = balanceOf(e, account);
	mint(e, account, amount);
	burn(e, account, amount);
	assert accountBefore == balanceOf(e, account);

	uint256 accountBeforeBurn = balanceOf(e, account) at initialStorage;
	burn(e, account, amount);
	mint(e, account, amount);
	assert accountBeforeBurn == balanceOf(e, account);
}


/*
  Property: all deposits must be greater or equal to withdraws for all methods with exception of burn
  Notice: in case of burn, one can burn from initial _totalSupply
*/

invariant positiveBalance()
	totalWithdraw <= totalDeposit
	filtered {f -> f.selector != sig:burn(address,uint256).selector}



rule whoCanIncreaseBalance_mint() {
	//the mint case
	address addr1;
	address addr2;
	uint256 amount; 
	env e;
	uint256 balance2Before = balanceOf(addr2);
	require addr1 != addr2;

	mint(e, addr1, amount); 
	assert balanceOf(addr2) == balance2Before;
}

rule whoCanIncreaseBalance_transfer() {
	//the mint case
	address addr1;
	address addr2;
	uint256 amount; 
	env e;
	uint256 balance2Before = balanceOf(addr2);
	require addr1 != addr2;

	mint(e, addr1, amount); 
	assert balanceOf(addr2) == balance2Before;
}