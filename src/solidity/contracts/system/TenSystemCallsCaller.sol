// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITenSystemCalls {
    function getRandomNumber() external returns (uint256);
    function getTransactionTimestamp() external view returns (uint256);
}

contract TenSystemCallsCaller {

    function callRandomNumbers(address callee, uint256 n) external returns (uint256[] memory) {
        uint256[] memory results = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            results[i] = ITenSystemCalls(callee).getRandomNumber();
        }
        return results;
    }

    function callRandomNumber(address callee) external returns (uint256) {
        return ITenSystemCalls(callee).getRandomNumber();
    }

    function callTimestamp(address callee) external view returns (uint256) {
        return ITenSystemCalls(callee).getTransactionTimestamp();
    }
}