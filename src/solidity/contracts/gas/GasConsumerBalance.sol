// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumerBalance {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function get_balance() public { address(this).balance; }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}