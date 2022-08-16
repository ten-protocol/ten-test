// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Error {
    address public owner;
    string public key;

    constructor(string _key) {
        owner = msg.sender;
        key = _key;
    }

    function requirefn(string value) public view {
        require(value == key, "Value needs to equal key");
    }

    function revertfn(string value) public view {
        if (value != key) {
            revert("Supplied value does not equal the key");
        }
    }

    function assertfn(string value) public view {
        assert(value == key);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}