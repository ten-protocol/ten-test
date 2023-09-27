// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FibonacciCalculator {
    uint256 public result;

    constructor() {
        result = 0; // Initialize result to 0
    }

    function calculateFibonacci(uint256 n) external {
        result = fib(n);
    }

    function getFibonacciResult() external view returns (uint256) {
        return result;
    }

    function fib(uint256 n) internal pure returns (uint256) {
        if (n <= 1) {
            return n;
        } else {
            uint256 a = 0;
            uint256 b = 1;
            uint256 c;
            for (uint256 i = 2; i <= n; i++) {
                c = a + b;
                a = b;
                b = c;
            }
            return b;
        }
    }
}