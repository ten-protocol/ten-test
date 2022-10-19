// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Store {
    // two fields, string indexed only
    event ItemSet1(string indexed key, uint256 value);

    // single event which shares some signature as the Storage contract
    event Stored(uint256 value);

    address public owner;
    mapping (string => uint256) public items;

    constructor() {
        owner = msg.sender;
    }

    function setItem(string calldata key, uint256 value) external {
        items[key] = value;
        emit ItemSet1(key, value);
        emit Stored(value);
    }

    function storeItem(uint256 value) external {
        items['_'] = value;
        emit Stored(value);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}