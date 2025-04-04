// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable returns (uint256);
    function reattemptCallback(uint256 callbackId) external;
}

contract StorageTwoPhaseReceiveWithRevert {
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
    }

    function retrieve() public view returns (uint256){
        return number;
    }

    receive() external payable { revert(); }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}