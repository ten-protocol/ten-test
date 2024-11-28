// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable;
    function reattemptCallback(uint256 callbackId) external;
}

contract CallDataTwoPhase {
    IPublicCallbacks public callbacks;
    uint256 public lastSum;

    constructor(address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
    }

    function processLargeData(uint256[] memory data) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleProcessLargeData.selector, data);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleProcessLargeData(uint256[] memory data) public {
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

