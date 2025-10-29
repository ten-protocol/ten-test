pragma solidity ^0.8.0;

contract WrappedNative {
    string public name = "WrappedEth";
    string public symbol = "WETH";
    uint8  public decimals = 18;

    event  Approval(address indexed src, address indexed guy, uint amount);
    event  Transfer(address indexed src, address indexed dst, uint amount);
    event  Deposit(address indexed dst, uint amount);
    event  Withdrawal(address indexed src, uint amount);

    mapping (address => uint) public  balanceOf;
    mapping (address => mapping (address => uint)) public  allowance;

    function() public payable {
        deposit();
    }

    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
        Deposit(msg.sender, msg.value);
    }

    function withdraw(uint amount) public {
        require(balanceOf[msg.sender] >= amount);
        balanceOf[msg.sender] -= amount;
        msg.sender.transfer(amount);
        Withdrawal(msg.sender, amount);
    }

    function totalSupply() public view returns (uint) {
        return this.balance;
    }

    function approve(address guy, uint amount) public returns (bool) {
        allowance[msg.sender][guy] = amount;
        Approval(msg.sender, guy, amount);
        return true;
    }

    function transfer(address dst, uint amount) public returns (bool) {
        return transferFrom(msg.sender, dst, amount);
    }

    function transferFrom(address src, address dst, uint amount) public returns (bool) {
        require(balanceOf[src] >= amount);

        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
            require(allowance[src][msg.sender] >= amount);
            allowance[src][msg.sender] -= amount;
        }

        balanceOf[src] -= amount;
        balanceOf[dst] += amount;

        Transfer(src, dst, amount);

        return true;
    }
}