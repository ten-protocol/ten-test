// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract KeyStorageForUpgrades {
    address public owner;
    mapping (string => uint256) public items;

    constructor() {
        owner = msg.sender;
    }

    function setItem(string calldata key, uint256 value) external {
        items[key] = value;
    }

    function getItem(string calldata key) public view returns (uint256) {
        return items[key];
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}