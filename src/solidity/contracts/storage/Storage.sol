// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Storage {
    // single event which shares some signature as the KeyStorage contract
    event Stored(uint256 value);

    address public owner;
    uint256 number;

    constructor(uint256 num) {
        owner = msg.sender;
        number = num;
    }

    function store(uint256 num) public {
        number = num;
        emit Stored(number);
    }

    function store_no_emit(uint256 num) public {
        number = num;
    }

    function retrieve() public view returns (uint256){
        return number;
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}