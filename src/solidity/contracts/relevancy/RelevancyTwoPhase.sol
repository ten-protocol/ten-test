// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable returns (uint256);
    function reattemptCallback(uint256 callbackId) external;
}

contract RelevancyTwoPhase {
    IPublicCallbacks public callbacks;

    event CallerIndexedAddress(address indexed addr);
    event TwoIndexedAddresses(address indexed addr1, address indexed addr2);
    event NonIndexedAddressAndNumber(address addr1, uint256 value);

    address public owner;
    uint256 num = 0;

    constructor(address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
        owner = msg.sender;
    }

    function callerIndexedAddress() public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleCallerIndexedAddress.selector, msg.sender);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleCallerIndexedAddress(address addr1) external {
        num = num + 1;
        emit CallerIndexedAddress(addr1);
    }

    function twoIndexedAddresses(address addr1, address addr2) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleTwoIndexedAddresses.selector, addr1, addr2);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleTwoIndexedAddresses(address addr1, address addr2) external {
        num = num + 1;
        emit TwoIndexedAddresses(addr1, addr2);
    }

    function nonIndexedAddressAndNumber(address addr1) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleNonIndexedAddressAndNumber.selector, addr1);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleNonIndexedAddressAndNumber(address addr1) external {
        num = num + 1;
        emit NonIndexedAddressAndNumber(addr1, num);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}