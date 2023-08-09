// using ERC20Helper as erc20helper;

methods {
    function balanceOf(address) external returns uint256 envfree;
    function transfer(address, uint256) external returns bool; // transfer(recipient,amount) trasnfers amount from msg.sender to recipient
    function allowance(address, address) external returns uint256 envfree; // allowance(owner, spender) returns the amount of allowance
    function approve(address, uint256) external returns bool; // approve(spender,amount) approves the allowance for the spender
    function transferFrom(address, address, uint256) external returns bool; // transferFrom(sender, recipient, amount) transfers tokens if there is sufficient allowance
    function totalSupply() external returns uint256 envfree;
    function increaseAllowance(address, uint256) external returns bool; // increases allowance of spender from msg.sender
    function decreaseAllowance(address, uint256) external returns bool; // decreases allowance of spender
    function mint(address, uint256) external;
    function burn(address, uint256) external;

    function _owner() external returns address envfree;


    // function _.name() external => DISPATCHER(true);
    // function _.symbol() external => DISPATCHER(true);
    // function _.decimals() external => DISPATCHER(true);
    // function _.totalSupply() external => DISPATCHER(true);
    // function _.balanceOf(address) external => DISPATCHER(true);
    // function _.allowance(address,address) external => DISPATCHER(true);
    // function _.approve(address,uint256) external => DISPATCHER(true);
    // function _.transfer(address,uint256) external => DISPATCHER(true);
    // function _.transferFrom(address,address,uint256) external => DISPATCHER(true);

	// function erc20helper.tokenBalanceOf(address, address) external returns (uint256) envfree;
}

function ownerOnlyOperation(method f) returns bool {
    return f.selector == sig:mint(address, uint256).selector || f.selector == sig:burn(address, uint256).selector;
}


rule totalSupplyChangesByMintOrBurnOnly(method f) {
    env e;
    calldataarg args;

    mathint totalSupplyBefore = totalSupply();
    f(e,args);
    mathint totalSupplyAfter = totalSupply();

    // assert (totalSupplyBefore != totalSupplyAfter) => (f.selector == sig:mint(address,uint256).selector || f.selector == sig:burn(address,uint256).selector);
    assert (totalSupplyBefore > totalSupplyAfter) => (f.selector == sig:burn(address,uint256).selector);
    assert (totalSupplyBefore < totalSupplyAfter) => (f.selector == sig:mint(address,uint256).selector);
}


rule transferRecipientCannotBeZero() {
    env e;

    address account;
    uint256 amount;

    transfer(e, account, amount);

    assert account != 0;
}

rule balanceChangesByMintBurnOrTransferOnly(method f) {
    env e;
    calldataarg args;
    address account;

    mathint balanceBefore = balanceOf(account);
    f(e,args);
    mathint balanceAfter = balanceOf(account);

    assert (balanceBefore > balanceAfter) => (
        f.selector == sig:burn(address,uint256).selector ||
        (f.selector == sig:transfer(address,uint256).selector && account == e.msg.sender) ||
        f.selector == sig:transferFrom(address,address,uint256).selector
    );

    assert (balanceBefore < balanceAfter) => (
        f.selector == sig:mint(address,uint256).selector ||
        f.selector == sig:transfer(address,uint256).selector ||
        f.selector == sig:transferFrom(address,address,uint256).selector
    );
}

rule transferIncreasesBalanceByAmount() {
    env e;
    address account;
    uint256 amount;

    require account != e.msg.sender;

    mathint balanceBefore = balanceOf(account);
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);

    transfer(e,account,amount);
    assert balanceOfSenderBefore >= to_mathint(amount);
    
    mathint balanceAfter = balanceOf(account);
    mathint balanceOfSenderAfter = balanceOf(e.msg.sender);

    assert balanceAfter == balanceBefore + amount;
    assert balanceOfSenderAfter == balanceOfSenderBefore - amount;
}

rule transferToMyselfDoesNotChangeBalance() {
    env e;
    address account;
    uint256 amount;
    require account == e.msg.sender;

    mathint balanceBefore = balanceOf(account);

    transfer(e,account,amount);
    assert balanceBefore >= to_mathint(amount);
    
    mathint balanceAfter = balanceOf(account);

    assert balanceAfter == balanceBefore;
}

rule transferDoesNotEffectUnintendedAccounts() {
    env e;
    address account;
    address unintendedAccount;
    uint256 amount;

    require account != unintendedAccount;
    require e.msg.sender != unintendedAccount;

    mathint balanceBefore = balanceOf(unintendedAccount);

    transfer(e,account,amount);

    mathint balanceAfter = balanceOf(unintendedAccount);

    assert balanceBefore == balanceAfter;
}

rule transferFromIncreasesBalanceByAmount() {
    env e;
    address sender;
    address recipient;
    uint256 amount;
    
    require recipient != sender;

    mathint balanceOfRecipientBefore = balanceOf(recipient);
    mathint balanceOfSenderBefore = balanceOf(sender);
    mathint allowanceBefore = allowance(sender, e.msg.sender);

    transferFrom(e,sender, recipient, amount);
    assert sender != 0 && recipient != 0;
    assert balanceOfSenderBefore >= to_mathint(amount);
    assert allowanceBefore >= to_mathint(amount);

    mathint balanceOfRecipientAfter = balanceOf(recipient);
    mathint balanceOfSenderAfter = balanceOf(sender);
    mathint allowanceAfter = allowance(sender,e.msg.sender);

    assert balanceOfRecipientAfter == balanceOfRecipientBefore + amount;
    assert balanceOfSenderAfter == balanceOfSenderBefore - amount;
    assert allowanceAfter == allowanceBefore - amount;
}


rule transferFromDoesNotUpdateBalanceIfSenderIsRecipient() {
    env e;
    address owner;
    uint256 amount;

    mathint balanceBefore = balanceOf(owner);
    mathint allowanceBefore = allowance(owner, e.msg.sender);

    transferFrom(e, owner, owner, amount);
    assert owner != 0;
    assert balanceBefore >= to_mathint(amount);
    assert allowanceBefore >= to_mathint(amount);

    mathint balanceAfter = balanceOf(owner);
    mathint allowanceAfter = allowance(owner,e.msg.sender);

    assert balanceBefore == balanceAfter;
    assert allowanceAfter == allowanceBefore - amount;
}


rule transferFromDoesNotEffectUnintendedAccounts() {
    env e;
    address sender;
    address recipient;
    address unintendedAccount;
    uint256 amount;

    require sender != unintendedAccount;
    require recipient != unintendedAccount;

    mathint balanceBefore = balanceOf(unintendedAccount);

    transferFrom(e,sender, recipient, amount);

    mathint balanceAfter = balanceOf(unintendedAccount);

    assert balanceBefore == balanceAfter;
}

rule onlyOwnerFunctionsCanBeCalledByOwnerOnly(method f) {
    env e;
    calldataarg args;
    require ownerOnlyOperation(f);

    f(e,args);
    assert e.msg.sender == _owner();
}



rule increaseAllowanceSetsAllowancesAsExpected() {
    env e;
    address spender;
    address randomAccount;
    address randomAccount2;
    uint256 amount;

    mathint allowanceBefore = allowance(e.msg.sender, spender);
    mathint anotherAllowanceBefore = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceBefore = allowance(randomAccount, randomAccount2);

    increaseAllowance(e, spender, amount);
    assert spender != 0;

    mathint allowanceAfter = allowance(e.msg.sender, spender);
    mathint anotherAllowanceAfter = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceAfter = allowance(randomAccount, randomAccount2);

    assert allowanceAfter == allowanceBefore + amount;
    assert randomAccount != spender => anotherAllowanceAfter == anotherAllowanceBefore;
    assert randomAccount != e.msg.sender => randomAllowanceBefore == randomAllowanceAfter;
}



rule decreaseAllowanceSetsAllowancesAsExpected() {
    env e;
    address spender;
    address randomAccount;
    address randomAccount2;
    uint256 amount;

    require e.msg.sender != randomAccount;

    mathint allowanceBefore = allowance(e.msg.sender, spender);
    mathint anotherAllowanceBefore = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceBefore = allowance(randomAccount, randomAccount2);

    decreaseAllowance(e, spender, amount);
    assert spender != 0;
    assert allowanceBefore >= to_mathint(amount);

    mathint allowanceAfter = allowance(e.msg.sender, spender);
    mathint anotherAllowanceAfter = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceAfter = allowance(randomAccount, randomAccount2);

    assert allowanceAfter == allowanceBefore - amount;
    assert randomAccount != spender => anotherAllowanceAfter == anotherAllowanceBefore;
    assert randomAccount != e.msg.sender => randomAllowanceBefore == randomAllowanceAfter;
}


rule approveSetsAllowancesAsExpected() {
    env e;
    address spender;
    address randomAccount;
    address randomAccount2;
    uint256 amount;

    mathint anotherAllowanceBefore = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceBefore = allowance(randomAccount, randomAccount2);

    approve(e, spender, amount);
    assert spender != 0;

    mathint allowanceAfter = allowance(e.msg.sender, spender);
    mathint anotherAllowanceAfter = allowance(e.msg.sender, randomAccount);
    mathint randomAllowanceAfter = allowance(randomAccount, randomAccount2);

    assert allowanceAfter == to_mathint(amount);
    assert randomAccount != spender => anotherAllowanceAfter == anotherAllowanceBefore;
    assert randomAccount != e.msg.sender => randomAllowanceBefore == randomAllowanceAfter;
}

 
rule mintIncreasesBalance() {
    env e;
    address account;
    address randomAccount;
    uint256 amount;

    require account != randomAccount;

    mathint balanceBefore = balanceOf(account);
    mathint randomBalanceBefore = balanceOf(randomAccount);
    mathint totalSupplyBefore = totalSupply();

    mint(e, account, amount);
    assert account != 0;

    mathint balanceAfter = balanceOf(account);
    mathint randomBalanceAfter = balanceOf(randomAccount);
    mathint totalSupplyAfter = totalSupply();

    assert balanceAfter == balanceBefore + amount;
    assert randomBalanceBefore == randomBalanceAfter;
    assert totalSupplyBefore + amount == totalSupplyAfter;
}


rule burnDecreasesBalance() {
    env e;
    address account;
    address randomAccount;
    uint256 amount;

    require account != randomAccount;

    mathint balanceBefore = balanceOf(account);
    mathint randomBalanceBefore = balanceOf(randomAccount);
    mathint totalSupplyBefore = totalSupply();

    burn(e, account, amount);
    assert account != 0;
    assert balanceBefore >= to_mathint(amount);

    mathint balanceAfter = balanceOf(account);
    mathint randomBalanceAfter = balanceOf(randomAccount);
    mathint totalSupplyAfter = totalSupply();

    assert balanceAfter == balanceBefore - amount;
    assert randomBalanceBefore == randomBalanceAfter;
    assert totalSupplyBefore  - amount == totalSupplyAfter;
}


// ghost mathint sumOfBalances{
//     init_state axiom sumOfBalances == 0;
// }

// hook Sstore _balances[KEY address addr] uint256 new_balance (uint256 old_balance) STORAGE {
//     sumOfBalances = sumOfBalances + to_mathint(new_balance) - to_mathint(old_balance);
// }

// hook Sload uint256 value _balances[KEY address addr] STORAGE {
//     require to_mathint(value) <= sumOfBalances;
// }

// invariant sumOfBalancesEqualsTotalSupply()
//     sumOfBalances == to_mathint(totalSupply());

