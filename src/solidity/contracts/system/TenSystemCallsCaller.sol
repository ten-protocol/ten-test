// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITenSystemCalls {
    function getRandomNumber() external returns (uint256);
    function getTransactionTimestamp() external view returns (uint256);
}

contract TenSystemCallsCaller {
    event RandomNumber(uint256 indexed id, uint256 random_num);
    event TxTimestamp(uint256 indexed id, uint256 timestamp);

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

    function emitRandomNumber(uint256 id, address callee) public {
        uint256 random_num = ITenSystemCalls(callee).getRandomNumber();
        emit RandomNumber(id, random_num);
    }

    function emitTimestamp(uint256 id, address callee) public {
        uint256 timestamp =  ITenSystemCalls(callee).getTransactionTimestamp();
        emit TxTimestamp(id, timestamp);
    }
}