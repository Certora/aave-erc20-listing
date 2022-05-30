pragma solidity ^0.8.0;


contract Lockable {
    uint public creationTime;
    bool public lock;
    bool public tokenTransfer;
    address public owner;
    mapping( address => bool ) public unlockaddress;
    mapping( address => bool ) public lockaddress;

    event Locked(address lockaddress,bool status);
    event Unlocked(address unlockedaddress, bool status);

    // if Token transfer
    modifier isTokenTransfer {
        // if token transfer is not allow
        if(!tokenTransfer) {
            require(unlockaddress[msg.sender]);
        }
        _;
    }

    // This modifier check whether the contract should be in a locked
    // or unlocked state, then acts and updates accordingly if
    // necessary
    modifier checkLock {
        if (lockaddress[msg.sender]) {
            revert();
        }
        _;
    }

    modifier isOwner {
        require(owner == msg.sender);
        _;
    }

    constructor() {
        creationTime = block.timestamp;
        tokenTransfer = false;
        owner = msg.sender;
    }

    // Lock Address
    function lockAddress(address target, bool status)
    external
    isOwner
    {
        require(owner != target);
        lockaddress[target] = status;
        emit Locked(target, status);
    }

    // UnLock Address
    function unlockAddress(address target, bool status)
    external
    isOwner
    {
        unlockaddress[target] = status;
        emit Unlocked(target, status);
    }
}

// ICON ICX Token
/// @author DongOk Ryu - <pop@theloop.co.kr>
contract IcxToken is  Lockable {
    mapping( address => uint ) _balances;
    mapping( address => mapping( address => uint ) ) _approvals;
    uint _supply;
    address public walletAddress;


    //event TokenMint(address newTokenHolder, uint amountOfTokens);
    event TokenBurned(address burnAddress, uint amountOfTokens);
    event TokenTransfer();
    event Transfer( address indexed from, address indexed to, uint value);
    event Approval( address indexed owner, address indexed spender, uint value);

    modifier onlyFromWallet {
        require(msg.sender != walletAddress); // :)))
        _;
    }

    constructor( uint initial_balance, address wallet) {
        require(wallet != address(0));
        require(initial_balance != 0);
        _balances[msg.sender] = initial_balance;
        _supply = initial_balance;
        walletAddress = wallet;
    }

    function totalSupply()  public returns (uint supply) {
        return _supply;
    }

    function balanceOf( address who ) public  returns (uint value) {
        return _balances[who];
    }

    function allowance(address owner, address spender) public  returns (uint _allowance) {
        return _approvals[owner][spender];
    }

    function transfer( address to, uint value) public
    isTokenTransfer
    checkLock
    returns (bool success) {

        require( _balances[msg.sender] >= value );

        _balances[msg.sender] = _balances[msg.sender]- value;
        _balances[to] = _balances[to] + value;
        emit Transfer( msg.sender, to, value );
        return true;
    }

    function transferFrom( address from, address to, uint value) public
    isTokenTransfer
    checkLock
    returns (bool success) {
        // if you don't have enough balance, throw
        require( _balances[from] >= value );
        // if you don't have approval, throw
        require( _approvals[from][msg.sender] >= value );
        // transfer and return true
        _approvals[from][msg.sender] = _approvals[from][msg.sender] - value;
        _balances[from] = _balances[from]- value;
        _balances[to] = _balances[to] + value;
        emit Transfer( from, to, value );
        return true;
    }

    function approve(address spender, uint value) public
    isTokenTransfer
    checkLock
    returns (bool success) {
        _approvals[msg.sender][spender] = value;
        emit Approval( msg.sender, spender, value );
        return true;
    }

    // burnToken burn tokensAmount for sender balance
    function burnTokens(uint tokensAmount)
    isTokenTransfer
    external
    {
        require( _balances[msg.sender] >= tokensAmount );

        _balances[msg.sender] = _balances[msg.sender] - tokensAmount;
        _supply = _supply - tokensAmount;
        emit TokenBurned(msg.sender, tokensAmount);

    }


    function enableTokenTransfer()
    external
    onlyFromWallet {
        tokenTransfer = true;
        emit TokenTransfer();
    }

    function disableTokenTransfer()
    external
    onlyFromWallet {
        tokenTransfer = false;
        emit TokenTransfer();
    }

}