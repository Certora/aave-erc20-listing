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

definition priveledgedFunction(method f ) returns bool = 
	f.selector == sig:mint(address,uint256).selector || 
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
    
	uint256 before = totalSupply(e);
	transfer(e, to, amount);
    uint256 after = totalSupply(e);
    assert after == before;
}

rule transferDecreasesBalanceOfSender() {
	env e;
	address from = e.msg.sender;
	address to;
	uint256 amount;
	
	uint256 before = balanceOf(e, from);
	transfer(e, to, amount);
    uint256 after = balanceOf(e, from);
    assert after <= before, "transfer didn't decrease balance of sender";
}

rule transferIncreasesBalanceOfReceiver() {
	env e;
	address to;
	uint256 amount;
	
	uint256 before = balanceOf(e, to);
	transfer(e, to, amount);
    uint256 after = balanceOf(e, to);
    assert after >= before, "transfer didn't increase balance of receiver";
}

rule transferExceedingAllowanceDoesntPass() {
	env e1;
	address owner = e1.msg.sender;
	
	env e2;
	address spender = e2.msg.sender;
	address recepient;

	uint256 allowed;
	uint256 transfered;
	
	require transfered > allowed;
	approve(e1, spender, allowed);
	if (!lastReverted) {
		transferFrom@withrevert(e2, owner, recepient, transfered);
		assert lastReverted;
	}
	else {
		assert true;
	}
}

rule burnReducesTotalSupply() {
	env e;
	address addr;
	uint256 amount;
	require amount > 0;
	
	uint256 before = totalSupply(e);
	burn(e, addr, amount);
    uint256 after = totalSupply(e);
    assert after < before;
}

rule mintIncreasesTotalSupply() {
	env e;
	address addr;
	uint256 amount;
	require amount > 0;
	
	uint256 before = totalSupply(e);
	mint(e, addr, amount);
    uint256 after = totalSupply(e);
    assert after > before;
}

rule decreaseAllowanceWorks() {
	env e1;
	address owner = e1.msg.sender;
	
	env e2;
	address spender = e2.msg.sender;
	address recepient;

	uint256 allowedBefore = allowance(e1, owner, spender);
	uint256 subtractedValue;
		
	require allowedBefore > 1 && subtractedValue > 0 && subtractedValue < allowedBefore;
	mathint newAllowance = allowedBefore - subtractedValue;
	
	uint256 transfered;
	require transfered <= allowedBefore && assert_uint256(newAllowance) < transfered;
	storage initialStorage = lastStorage;

	transferFrom@withrevert(e2, owner, recepient, transfered);
	bool firstTransferSucceeded = !lastReverted;

	decreaseAllowance@withrevert(e1, spender, subtractedValue);
	if (firstTransferSucceeded && !lastReverted) {
		transferFrom@withrevert(e2, owner, recepient, transfered) at initialStorage;
		assert lastReverted;
	}
	else {
		assert true;
	}
}



