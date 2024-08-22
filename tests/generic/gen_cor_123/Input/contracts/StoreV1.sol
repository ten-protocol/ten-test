// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

contract StoreV1 {
    uint256 number;

    function store(uint256 num) public {
        number = num;
    }

    function retrieve() public view virtual returns (uint256){
        return number;
    }
}