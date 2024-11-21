// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable;
    function reattemptCallback(uint256 callbackId) external;
}

contract Error {
    IPublicCallbacks public callbacks;

    constructor(address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
    }

    function force_require() public view {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_force_require.selector);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_force_require() external {
        require(false, "Forced require");
    }

    function force_revert() public view {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_force_revert.selector);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_force_revert() public view {
        revert("Forced revert");
    }
}