// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumerAdd {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function do_nothing() public {}

    function add_once() public { 1 + 2; }
    function add_twice() public { 1 + 2 + 3; }
    function add_thrice() public { 1 + 2 + 3 + 4; }
    function add_three_times_with_a_long_name() public { 1 + 2 + 3 + 4; }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}