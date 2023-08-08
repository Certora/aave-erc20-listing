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

ghost mathint sumOfBalances {
	init_state axiom sumOfBalances == 0;
}

hook Sstore _balances[KEY address addr] uint256 new_balance (uint256 old_balance) STORAGE {
	sumOfBalances = sumOfBalances + to_mathint(new_balance) - to_mathint(old_balance);
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