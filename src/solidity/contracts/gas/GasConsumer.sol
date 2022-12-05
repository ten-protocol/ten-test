// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract GasConsumer {
    address public owner;
    uint256 number;

    constructor(uint256 num) {
        owner = msg.sender;
        number = num;
    }

    function set(uint256 value) public {
        number = value;
    }

    function add_once(uint256 value) public view {
        number = number + value;
    }

    function add_twice(uint256 value) public view {
        number = number + value + value;
    }

    function add_n_times(uint256 value) public view {
        for (i = 0; i < 10; i = i +1 {
            number = number + value;
        }
    }

    function multiply_once(uint256 value) public view {
        number = number * value;
    }

    function multiply_twice(uint256 value) public view {
        number = number * value * value;
    }

    function add_n_times(uint256 value) public view {
        for (i = 0; i < 10; i = i +1 {
            number = number * value;
        }
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}