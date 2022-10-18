// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Relevancy {
    event TwoIndexedAddresses(address indexed addr1, address indexed addr2);
    event OneIndexedAddress(address indexed addr1, address addr2);
    event IndexedAddressAndNumber(address indexed addr1, uint256 value);
    event AddressAndNumber(address addr1, uint256 value);
    event Number(uint256 value);

    address public owner;
    uint256 num = 1;

    constructor() {
        owner = msg.sender;
    }

    function twoIndexedAddresses(address addr1, address addr2) external {
        num = num + 1;
        emit TwoIndexedAddresses(addr1, addr2);
    }

    function oneIndexedAddress(address addr1, address addr2) external {
        num = num + 1;
        emit OneIndexedAddress(addr1, addr2);
    }

    function indexedAddressAndNumber(address addr) external {
        num = num + 1;
        emit IndexedAddressAndNumber(addr, num);
    }

    function addressAndNumber(address addr) external {
        num = num + 1;
        emit AddressAndNumber(addr, num);
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