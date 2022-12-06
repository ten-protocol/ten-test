// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumer {
    address public owner;
    uint256 number;

    constructor(uint256 num) {
        owner = msg.sender;
        number = num;
    }

    function add_once() public {
        1 + 1;
    }

    function add_twice() public {
        1 + 1 + 1;
    }

    function add_thrice() public {
        1 + 1 + 1 + 1;
    }

    function add_three_times_with_a_long_name() public {
        1 + 1 + 1 + 1;
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}