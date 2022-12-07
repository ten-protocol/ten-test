// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumer {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function times_once() public { 2 * 2; }
    function times_twice() public { 2 * 2 * 2; }
    function times_thrice() public { 2 * 2 * 2 * 2; }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}