// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITenSystemCalls {
    function getRandomNumber() external returns (uint256);
    function getTransactionTimestamp() external view returns (uint256);
}

contract TenSystemCallsCaller {
    function callRandomNumber(address callee) external returns (uint256) {
        return ITenSystemCalls(callee).getRandomNumber();
    }

    function callTimestamp(address callee) external view returns (uint256) {
        return ITenSystemCalls(callee).getTransactionTimestamp();
    }
}