// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "./DoubleV1.sol";

contract DoubleV2 is DoubleV1 {
    function doItTwice(uint x) public pure returns (uint) {
        return 4*x;
    }
}