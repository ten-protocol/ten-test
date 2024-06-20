pragma solidity ^0.8.0;

contract EventEmitter {
    event SimpleEvent(uint indexed id, string message, address indexed sender);

    event ArrayEvent(uint indexed id, uint[] numbers, string[] messages);

    struct User {uint id; string name; address userAddress;}
    event StructEvent(uint indexed id, User user);

    event MappingEvent(uint indexed id, address[] keys, uint[] values);

    uint public eventCounter;

    function emitSimpleEvent(uint id, string memory _message) public {
        emit SimpleEvent(id, _message, msg.sender);
    }

    function emitArrayEvent(uint id, uint[] memory _numbers, string[] memory _messages) public {
        require(_numbers.length == _messages.length, "Arrays must be of equal length");
        emit ArrayEvent(id, _numbers, _messages);
    }

    function emitStructEvent(uint id, string memory _name) public {
        User memory user = User(eventCounter, _name, msg.sender);
        emit StructEvent(id, user);
    }

    function emitMappingEvent(uint id, address[] memory _addresses, uint[] memory _balances) public {
        require(_addresses.length == _balances.length, "Arrays must be of equal length");
        emit MappingEvent(id, _addresses, _balances);
    }

    fallback() external { revert("Invalid call"); }
    receive() external payable { revert("No ether accepted"); }
}