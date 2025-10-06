// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PayableConstructorRevert {
    uint256 public receivedAmount;
    address public owner;

    // require at least 1 ether to deploy this contract
    constructor() payable {
        uint256 minimum = 1 ether;
        require(msg.value >= minimum, "Not enough ETH sent to constructor");

        owner = msg.sender;
        receivedAmount = msg.value;
    }
}