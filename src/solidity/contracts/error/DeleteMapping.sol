// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MappingDeletionExample {
    // A simple mapping from address to uint
    mapping(address => uint256) public balances;

    // Function to set a balance
    function setBalance(address user, uint256 amount) public {
        balances[user] = amount;
    }

    // Function to get a balance
    function getBalance(address user) public view returns (uint256) {
        return balances[user];
    }

    // Function to delete a specific user from the mapping
    function deleteBalance(address user) public {
        delete balances[user]; // This resets the value to 0
    }
}