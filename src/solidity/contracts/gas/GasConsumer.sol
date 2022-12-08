// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumer {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function do_nothing() public { 1 + 2; }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}