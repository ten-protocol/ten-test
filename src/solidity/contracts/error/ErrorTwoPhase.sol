// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable;
    function reattemptCallback(uint256 callbackId) external;
}

contract ErrorTwoPhase {
    IPublicCallbacks public callbacks;

    string public key = "foo";

    constructor(address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
    }

    function set(string memory _key) public {
        key = _key;
    }

    // set_key_with_require
    function set_key_with_require(string memory newKey) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_set_key_with_require.selector, newKey);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_set_key_with_require(string memory newKey) external {
        require(bytes(newKey).length != 0, "New key cannot be empty");
        key = newKey;
    }

    // set_key_with_revert
    function set_key_with_revert(string memory newKey) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_set_key_with_revert.selector, newKey);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_set_key_with_revert(string memory newKey) external {
        if (bytes(newKey).length == 0){
            revert("New key cannot be empty");
        }
        key = newKey;
    }

    // force_require
    function force_require() public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_force_require.selector);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_force_require() external {
        require(false, "Forced require");
    }

    // force_revert
    function force_revert() public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_force_revert.selector);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_force_revert() external {
        revert("Forced revert");
    }

    // force_assert
    function force_assert() public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handle_force_assert.selector);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handle_force_assert() external {
        assert(false);
    }
}