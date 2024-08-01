pragma solidity ^0.8.0;

contract EventEmitterCaller {
    event CallerSimpleEvent(uint indexed id, string message, address indexed sender);
    event CallerAddressEvent(uint indexed id, address indexed _address);

    address private emitterAddress;

    constructor(address _emitterAddress) {
        emitterAddress = _emitterAddress;
    }

    function prepend(string memory _prefix, string memory _base) public pure returns (string memory) {
        return string(abi.encodePacked(_prefix, _base));
    }

    function callEmitSimpleEvent(uint id, string memory _prepend, string memory _message) public {
        (bool success, ) = emitterAddress.call(
            abi.encodeWithSignature("emitSimpleEvent(uint256,string)", id, _message)
        );
        require(success, "Call to callEmitSimpleEvent failed");
        emit CallerSimpleEvent(id, prepend(_prepend, _message), msg.sender);
    }

    function callEmitAddressEvent(uint id, address _address) public {
        (bool success, ) = emitterAddress.call(
            abi.encodeWithSignature("emitAddressEvent(uint256,address)", id, _address)
        );
        require(success, "Call to callEmitAddressEvent failed");
        emit CallerAddressEvent(id, msg.sender);
    }
}