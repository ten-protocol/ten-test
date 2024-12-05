// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable returns (uint256);
    function reattemptCallback(uint256 callbackId) external;
}

contract StorageTwoPhaseWithRefund {
    IPublicCallbacks public callbacks;
    mapping(uint256 => address) public idToSender;
    mapping(address => uint256) public senderToRefund;

    address public owner;
    uint256 number;

    constructor(uint256 num, address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
        owner = msg.sender;
        number = num;
    }

    function store(uint256 num) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleStore.selector, num, msg.sender);
        uint256 id = callbacks.register{value: msg.value}(callbackData);
        idToSender[id] = msg.sender;
    }

    function handleStore(uint256 num, address originator) external {
        require(msg.sender == address(callbacks));
        number = num;
    }

    function retrieve() public view returns (uint256){
        return number;
    }

    function refundWithdraw() external {
        msg.sender.call{value: senderToRefund[msg.sender]}("");
    }

    function refundBalance() public view returns (uint256){
        return senderToRefund[msg.sender];
    }

    // called into by IPublicCallbacks
    function handleRefund(uint256 id) public payable {
        senderToRefund[idToSender[id]] += msg.value;
    }

    function destroy() public {
        require(msg.sender == owner, "You are not the owner");
        selfdestruct(payable(address(this)));
    }
}