// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FibonacciStorage {
    uint256[] public fibonacciSeries;

    constructor() {
        fibonacciSeries.push(0); // Initialize the series with the first Fibonacci number, 0
        fibonacciSeries.push(1); // Initialize the series with the second Fibonacci number, 1
    }

    function calculateFibonacci(uint256 n) external {
        require(n >= fibonacciSeries.length, "Fibonacci number already calculated");

        for (uint256 i = fibonacciSeries.length; i <= n; i++) {
            uint256 nextFib = fibonacciSeries[i - 1] + fibonacciSeries[i - 2];
            fibonacciSeries.push(nextFib);
        }
    }

    function getFibonacci(uint256 n) external view returns (uint256) {
        require(n < fibonacciSeries.length, "Fibonacci number not yet calculated");
        return fibonacciSeries[n];
    }

    function getFibonacciSeries() external view returns (uint256[] memory) {
        return fibonacciSeries;
    }

    function calculateFactorial(uint256 n) external pure returns (uint256) {
        uint256 result = 1;
        for (uint256 i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}