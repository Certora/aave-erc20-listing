using ERC20Helper as erc20helper;

methods {
    function _.name() external => DISPATCHER(true);
    function _.symbol() external => DISPATCHER(true);
    function _owner() external returns address envfree;
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

/*
   Property: Checks that the sum of balances is still same after a tranfer from sender to receipent.
*/
rule transferPreserveBalance {
	address recipient;
	uint amount;
	env e;

	mathint balance_sender_before = balanceOf(e, e.msg.sender);
    mathint balance_recipient_before = balanceOf(e, recipient);

	transfer(e, recipient, amount);

	mathint balance_sender_after = balanceOf(e,e.msg.sender);
    mathint balance_recipient_after = balanceOf(e, recipient);

	assert balance_sender_before + balance_recipient_before == balance_sender_after + balance_recipient_after;
}

/*
	Property: Checks precondition which guarantees that transer will not revert.c
*/
rule transferRevert {
	address recipient;
	uint256 amount;
	env e;

	uint256 balance_sender_before = balanceOf(e, e.msg.sender);
	require (recipient != 0 && e.msg.sender != 0 && balance_sender_before >= amount
	&& e.msg.value != 0 && allowance(e, e.msg.sender, e.msg.sender) >= amount);

	transfer@withrevert(e, recipient, amount);
	assert !lastReverted;
}

/*
	Property: Increase of an allowance followed by its decrease results in the same allowance as was at the beginning of transaction.
*/
rule nonDisappearingAllowance {
	uint256 allowance;
	address other;
	env e;

	uint256 beforeIncrease = allowance(e, e.msg.sender, other);
	increaseAllowance(e, other, allowance);
	decreaseAllowance(e, other, allowance);
	uint256 afterDecrease = allowance(e, e.msg.sender, other);

	assert beforeIncrease == afterDecrease;
}

/*
  Property: A transfer performed between operations manipulating allowance does not influence allowance
  Notice: we consider change of allowance between sender and receipent which should be changed by transfer
*/
rule allowanceNonChangedByTransaction {
	uint256 allowance;
	address recipient;
	uint256 amount;
	env e;

	uint256 beforeIncrease = allowance(e, e.msg.sender, recipient);
	increaseAllowance(e, recipient, allowance);
	transfer(e, recipient, amount);
	decreaseAllowance(e, recipient, allowance);
	uint256 afterDecrease = allowance(e, e.msg.sender, recipient);

	assert beforeIncrease == afterDecrease;
}

/*
  Property: If sender doesn't have an allowance high enough, transferFrom fails. Then the allowance is increased
            and transferFrom should proceed sucessfully.
*/
rule allowanceAndTransfer {
	uint256 allowance;
	address sender;
	address recipient;
	uint256 amount;
	env e;

	uint256 balance_sender_before = balanceOf(e, e.msg.sender);

	require (recipient != 0 && sender != 0 && balance_sender_before >= amount && e.msg.value != 0);
	transferFrom@withrevert(e, sender, recipient, amount);
	assert lastReverted;

	uint256 amount_new = assert_uint256(amount+1);
	increaseAllowance(e, sender, amount_new);
	require (recipient != 0 && sender != 0 && balance_sender_before >= amount && e.msg.value != 0);
	transferFrom@withrevert(e, sender, recipient, amount);
	assert lastReverted;
}

/*
    Checks if the method f is mint or burn.
*/
definition isMintOrBurn(method f) returns bool =
	f.selector == sig:burn(address,uint256).selector || f.selector == sig:mint(address,uint256).selector;

/*
	The function performs mint (if state is true), otherwise performs burn and returns reverted state
*/
function mintOrBurnBasedOnState(env e, address account, uint256 amount, bool state) returns bool {
	if (state) {
		mint(e, account, amount);
		return false;
	} else {
		burn(e, account, amount);
		return true;
	}
}

/*
	Property: Burn after mint, or mint after burn with the same amount should not change balance of the account.
	Notice: Rule takes the method f and according to its type chooses to perform burn or mint.
*/
rule mintOrBurn(method f) filtered {f -> isMintOrBurn(f)} {
	address account;
	uint256 amount;
	bool state = f.selector == sig:mint(address, uint256).selector;
	env e;
	mathint nondet_choice;

	mathint account_before = balanceOf(e, account);
	bool next_state = mintOrBurnBasedOnState(e, account, amount, state);
	mintOrBurnBasedOnState(e, account, amount, next_state);
	mathint account_after = balanceOf(e, account);

	assert(account_before == account_after);
}

///// UNIT TEST /////
/*
  Property: Checks that the allowance between sender and msg.sender is changed correctly by transfer
*/
rule allowanceSetByTransfer {
	address recipient;
	address sender;
	uint256 amount;
	env e;
	storage initial = lastStorage;

	mathint allowanceBefore = allowance(e, sender, e.msg.sender);
	transferFrom@withrevert(e, sender, recipient, amount);
	bool succeeded = !lastReverted;
	mathint allowanceAfter = allowance(e, sender, e.msg.sender);
	
	assert succeeded => (allowanceBefore - amount == allowanceAfter || e.msg.sender == sender);
}

//// SYSTEM STATE ////
/*
  Property: all deposits must be greater or equal to withdraws for all methods with exception of burn
  Notice: in case of burn, one can burn from initial _totalSupply
*/
ghost mathint totalWithdraw {
	init_state axiom totalWithdraw == 0;
}

ghost mathint totalDeposit {
	init_state axiom totalDeposit == 0;
}
ghost mapping(address => bool) increasedBalances;

hook Sstore _balances[KEY address a] uint256 newBalance (uint256 oldBalance) STORAGE {
	if (newBalance >= oldBalance) {
		totalDeposit = totalDeposit + newBalance - oldBalance;
		increasedBalances[a] = true;
	} else {
		totalWithdraw = totalWithdraw + oldBalance - newBalance;
		increasedBalances[a] = false;
	}
}

invariant positiveBalance()
	totalWithdraw <= totalDeposit
	filtered {f -> f.selector != sig:burn(address,uint256).selector}

//// HIGH LEVEL RULE & RISK ANALYSIS ////
/*
 	Property: There must be a way how to eventually increase a balance of someonelse than the owner
	Note: The rule just checks if implementation is not scam.
 */

definition canIncrease(method f) returns bool =
	f.selector == sig:mint(address,uint256).selector || f.selector == sig:transfer(address,uint256).selector || f.selector == sig:transferFrom(address, address, uint256).selector;

rule mustIncreaseAccount(method f) filtered {f -> canIncrease(f)} {
	env e;
	calldataarg args;

	f(e,args);

	address a;
	address owner = _owner();
	
	require(a != owner);
	satisfy !increasedBalances[a];
 }


ghost bool allowanceStore;
ghost address allowanceOwner;
ghost address allowanceSender;
ghost uint256 allowanceValue;
hook Sload uint256 v _allowances[KEY address a][KEY address b] STORAGE {
	allowanceOwner = a;
	allowanceSender = b;
	allowanceValue = v;
}

hook Sstore _allowances[KEY address a][KEY address b] uint256 v STORAGE {
	allowanceStore = true;
}

/*
    Property: If one checks allowance of two addressed, the allowances mapping must be accessed.
*/
rule allowanceAccessAllowances() {
	address owner;
	address sender;
	env e;

	require(allowanceStore == false);
	uint256 v = allowance(e, owner, sender);
	assert(allowanceOwner == owner);
	assert(allowanceSender == sender);
	assert(v == allowanceValue);
	assert(allowanceStore == false);
}

/*
	Property: If a balance is changed, a called method is transfer, transferFrom, mint, or burn.
*/
rule balanceChanged(method f) {
	env e;
	calldataarg args;

	storage storageBefore = lastStorage;
	f(e, args);
	storage storageAfter = lastStorage;
	address a;
	assert((balanceOf(e, a) at storageBefore != balanceOf(e, a) at storageAfter) => (canIncrease(f) || f.selector == sig:burn(address,uint256).selector));
}