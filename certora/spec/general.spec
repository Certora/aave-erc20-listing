using ERC20Helper as erc20helper;

methods {
    
    function totalSupply() external returns uint256 envfree;
    function balanceOf(address) external returns uint256 envfree;
	function allowance(address,address) external returns uint256 envfree;
    function approve(address,uint256) external returns bool;
	function increaseAllowance(address,uint256) external returns bool;
    function transfer(address,uint256) external returns bool;
    function transferFrom(address,address,uint256) external returns bool;

	function erc20helper.tokenBalanceOf(address, address) external returns (uint256) envfree;
}

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
rule privilegedOperation(method f, address privileged) filtered {f -> priveledgedFunction(f) }
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

rule transferKeepsTotalSupply() {
	address to;
	uint256 amount;
	env e;
    
	uint256 before = totalSupply();
	transfer(e, to, amount);
    uint256 after = totalSupply();
    assert after == before;
}

rule transferDecreasesBalanceOfSender() {
	env e;
	address from = e.msg.sender;
	address to;
	uint256 amount;
	
	require from != to;
	uint256 before = balanceOf(from);
	transfer(e, to, amount);
    uint256 after = balanceOf(from);
    assert after == assert_uint256(before - amount) , "transfer didn't decrease balance of sender";
}

rule transferIncreasesBalanceOfReceiver() {
	env e;
	address to;
	uint256 amount;
	
	require to != e.msg.sender;
	uint256 before = balanceOf(to);
	transfer(e, to, amount);
    uint256 after = balanceOf(to);
    assert after == assert_uint256(before + amount), "transfer didn't increase balance of receiver";
}

rule transferExceedingAllowanceDoesntPass() {
	address owner;
	env e;
	address spender = e.msg.sender;
	address recepient;

	uint256 allowed = allowance(owner, spender);
	uint256 transfered;
	
	require transfered > allowed;
	transferFrom@withrevert(e, owner, recepient, transfered);
	assert lastReverted;
}

//transfer from udelat stejne kontroly jako transfer

rule burnReducesTotalSupply() {
	env e;
	address addr;
	uint256 amount;
	
	uint256 before = totalSupply();
	burn(e, addr, amount);
    uint256 after = totalSupply();
    assert after == assert_uint256(before - amount);
}

rule mintIncreasesTotalSupply() {
	env e;
	address addr;
	uint256 amount;
	require amount > 0;
	
	uint256 before = totalSupply();
	mint(e, addr, amount);
    uint256 after = totalSupply();
    assert after == assert_uint256(before + amount);
}

rule burnReducesBalance() {
	env e;
	address addr;
	uint256 amount;
	
	uint256 before = balanceOf(addr);
	burn(e, addr, amount);
    uint256 after = balanceOf(addr);
    assert after == assert_uint256(before - amount);
}

rule mintIncreasesBalance() {
	env e;
	address addr;
	uint256 amount;
	require amount > 0;
	
	uint256 before = balanceOf(addr);
	mint(e, addr, amount);
    uint256 after = balanceOf(addr);
    assert after == assert_uint256(before + amount);
}

rule decreaseAllowanceWorks() {
	env e;
	address owner = e.msg.sender;
	address spender;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 subtractedValue;
		
	decreaseAllowance(e, spender, subtractedValue);
	uint256 allowedAfter = allowance(owner, spender);
	assert allowedAfter == assert_uint256(allowedBefore - subtractedValue);
	
}

rule increaseAllowanceWorks() {
	env e;
	address owner = e.msg.sender;
	address spender;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 addedValue;
		
	increaseAllowance(e, spender, addedValue);
	uint256 allowedAfter = allowance(owner, spender);
	assert allowedAfter == assert_uint256(allowedBefore + addedValue);
	
}


rule transferFromReducesAllowance() {
	env e;
	address spender = e.msg.sender;
	address owner;
	address recepient;

	uint256 allowedBefore = allowance(owner, spender);
	uint256 transfered;

	transferFrom(e, owner, recepient, transfered);
	uint256 allowedAfter = allowance(owner, spender);
	assert allowedBefore == assert_uint256(allowedAfter + transfered);

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

rule onlyAllowedMethodsMayChangeTotalSupply(method f) {
	env e;
	uint256 totalSupplyBefore = totalSupply();
	calldataarg args;
	f(e,args);
	uint256 totalSupplyAfter = totalSupply();
	assert totalSupplyAfter > totalSupplyBefore => canIncreaseTotalSupply(f), "should not increase total supply";
	assert totalSupplyAfter < totalSupplyBefore => canDecreaseTotalSupply(f), "should not decrease total supply";

}

invariant balanceOfZeroIsZero()
	balanceOf(0) == 0;

ghost mathint sum_of_balances {
	init_state axiom sum_of_balances == 0;
}

hook Sstore _balances[KEY address a] uint new_value (uint old_value) STORAGE {
	sum_of_balances = sum_of_balances + new_value - old_value;
	numberOfChangesOfBalances = numberOfChangesOfBalances + 1;
}

invariant totalSupplyIsSumOfBalances()
	to_mathint(totalSupply()) == sum_of_balances;

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