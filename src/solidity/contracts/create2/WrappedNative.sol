// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WrappedNative {
    string public name = "WrappedEth";
    string public symbol = "WETH";
    uint8  public decimals = 18;

    event Approval(address indexed src, address indexed guy, uint amount);
    event Transfer(address indexed src, address indexed dst, uint amount);
    event Deposit(address indexed dst, uint amount);
    event Withdrawal(address indexed src, uint amount);

    mapping (address => uint) public balanceOf;
    mapping (address => mapping (address => uint)) public allowance;

    // Handle plain ETH transfers (no data)
    receive() external payable {
        deposit();
    }

    // Optional fallback for calls with data (keeps behavior consistent)
    fallback() external payable {
        // you can call deposit() here too if desired, but keep minimal.
    }

    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint amount) public {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
        emit Withdrawal(msg.sender, amount);
    }

    function totalSupply() public view returns (uint) {
        return address(this).balance;
    }

    function approve(address guy, uint amount) public returns (bool) {
        allowance[msg.sender][guy] = amount;
        emit Approval(msg.sender, guy, amount);
        return true;
    }

    function transfer(address dst, uint amount) public returns (bool) {
        return transferFrom(msg.sender, dst, amount);
    }

    function transferFrom(address src, address dst, uint amount) public returns (bool) {
        require(balanceOf[src] >= amount, "Insufficient balance");

        if (src != msg.sender && allowance[src][msg.sender] != type(uint256).max) {
            require(allowance[src][msg.sender] >= amount, "Insufficient allowance");
            allowance[src][msg.sender] -= amount;
        }

        balanceOf[src] -= amount;
        balanceOf[dst] += amount;

        emit Transfer(src, dst, amount);

        return true;
    }
}
