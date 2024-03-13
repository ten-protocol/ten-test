// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

contract DoubleV2 {

    function doIt(uint x) public pure returns (uint) {
        return 2*x;
    }

    function doItTwice(uint x) public pure returns (uint) {
        return 4*x;
    }

}