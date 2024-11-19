// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable;
    function reattemptCallback(uint256 callbackId) external;
}

contract StorageTwoPhaseWithEvents {
    // single event which shares some signature as the KeyStorage contract
    event Stored(uint256 value);

    IPublicCallbacks public callbacks;
    address public owner;
    uint256 number;

    constructor(uint256 num, address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
        owner = msg.sender;
        number = num;
    }

    function store(uint256 num) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleStore.selector, num, msg.sender);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleStore(uint256 num, address originator) external {
        require(msg.sender == address(callbacks));
        number = num;
        emit Stored(number);
    }

    function retrieve() public view returns (uint256){
        return number;
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}