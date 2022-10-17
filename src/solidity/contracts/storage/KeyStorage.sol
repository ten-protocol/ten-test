// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Store {
    // two fields, string indexed only
    event ItemSet1(string indexed key, uint256 value);

    // two fields, uint indexed only
    event ItemSet2(string key, uint256 indexed value);

    // two fields, both string and uint indexed
    event ItemSet3(string indexed key, uint256 indexed value);

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
        emit ItemSet2(key, value);
        emit ItemSet3(key, value);
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