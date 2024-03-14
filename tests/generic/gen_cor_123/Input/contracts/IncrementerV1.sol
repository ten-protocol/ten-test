// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IncrementerV1 {
    uint public number;

    function initialValue(uint _num) external {
        number=_num;
    }

    function increase() external {
        number += 1;
    }

    function retrieve() public view returns (uint){
        return number;
    }
}