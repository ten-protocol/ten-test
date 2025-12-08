// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "./MathUtils.sol";

contract TestMath {
    using MathUtils for uint;

    function testSquareRoot(uint x) public pure returns (uint) {
        return x.sqrt();
    }
}