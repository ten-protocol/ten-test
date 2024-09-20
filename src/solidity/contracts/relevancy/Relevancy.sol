// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Relevancy {
    struct EventLogConfig {
        bytes eventSignature; bool isPublic;
        bool topic1CanView; bool topic2CanView; bool topic3CanView;
        bool visibleToSender;
    }
    struct VisibilityConfig { bool isTransparent; EventLogConfig[] eventLogConfigs; }

    event CallerIndexedAddress(address indexed addr);
    event TwoIndexedAddresses(address indexed addr1, address indexed addr2);
    event NonIndexedAddressAndNumber(address addr1, uint256 value);
    event IndexedAddressAndNumber(address indexed addr, uint256 value);
    event Number(uint256 value);

    address public owner;
    uint256 num = 0;

    constructor() {
        owner = msg.sender;
    }

    function callerIndexedAddress() external {
        num = num + 1;
        emit CallerIndexedAddress(msg.sender);
    }

    function twoIndexedAddresses(address addr1, address addr2) external {
        num = num + 1;
        emit TwoIndexedAddresses(addr1, addr2);
    }

    function nonIndexedAddressAndNumber(address addr1) external {
        num = num + 1;
        emit NonIndexedAddressAndNumber(addr1, num);
    }

    function indexedAddressAndNumber(address addr) external {
        num = num + 1;
        emit IndexedAddressAndNumber(addr, num);
    }

    function number() external {
        num = num + 1;
        emit Number(num);
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}