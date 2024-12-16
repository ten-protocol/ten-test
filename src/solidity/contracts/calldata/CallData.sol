// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract CallData {
    uint256 public lastSum;

    function processLargeData(uint256[] memory data) public {
        uint256 sum = 0;
        for (uint256 i = 0; i < data.length; i++) {
            sum += data[i];
        }
        lastSum = sum;
    }

    function getLastSum() public view returns (uint256) {
        return lastSum;
    }
}

