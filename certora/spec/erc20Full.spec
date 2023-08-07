methods {
    function balanceOf(address) external returns uint256 envfree;
    function totalSupply() external returns uint256 envfree;
}

/*

Property: transferFrom where from is the msg.sender is equivalent to transfer() with the same arguments
*/
rule selfTransferFrom(address to, uint256 amount, address a ) {
    env e;

    storage init = lastStorage;
    transfer(e, to, amount);
    uint256 balanceA = balanceOf(a);
    uint256 ts = totalSupply();
    // storage afterTransfer = lastStorage; 
    transferFrom(e, e.msg.sender, to, amount) at init;
    
    assert balanceOf(a) == balanceA;
    assert totalSupply() == ts;
    // assert afterTransfer == lastStorage; 

} 


rule transferFromIsPossible(address from, address to, uint256 amount) {
    env e;

    uint256 before = balanceOf(to);
    transferFrom(e, from, to, amount);

    satisfy to_mathint(balanceOf(to)) == before + amount;
} 


ghost mathint sumBalances {
    init_state axiom sumBalances == 0;
} 

hook Sstore _balances[KEY address user] uint256 balance
    (uint256 old_balance) STORAGE {
        sumBalances = sumBalances - to_mathint(old_balance) + to_mathint(balance);
    }

invariant sumBalanceIsTotalSupply() 
    sumBalances == to_mathint(totalSupply());

invariant addressZero() 
    balanceOf(0) == 0;