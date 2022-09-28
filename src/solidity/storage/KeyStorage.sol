// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Store {
    event ItemSet(string key, string value, address setter);

    address public owner;
    mapping (string => string) public items;

    constructor() {
        owner = msg.sender;
    }

    function setItem(string calldata key, string calldata value) external {
        items[key] = value;
        emit ItemSet(key, value, msg.sender);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}