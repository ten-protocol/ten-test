// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Store {
    event ItemSet1(string key, uint256 value, address indexed setter);
    event ItemSet2(string key, uint256 indexed value, address indexed setter);
    event ItemSet3(string indexed key, uint256 value, address setter);

    address public owner;
    mapping (string => uint256) public items;

    constructor() {
        owner = msg.sender;
    }

    function setItem(string calldata key, uint256 value) external {
        items[key] = value;
        emit ItemSet1(key, value, msg.sender);
        emit ItemSet2(key, value, msg.sender);
        emit ItemSet3(key, value, msg.sender);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}