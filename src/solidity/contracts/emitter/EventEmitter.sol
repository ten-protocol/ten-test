pragma solidity ^0.8.0;

contract EventEmitter {
    event SimpleEvent(uint indexed id, string message, address sender);

    event ArrayEvent(uint indexed id, uint[] numbers, string[] messages);

    struct User {uint id; string name; address userAddress;}
    event StructEvent(uint indexed id, User user);

    event NestedEvent(uint indexed id, uint value, address[] keys, uint[] values);
    
    event MappingEvent(uint indexed id, address[] keys, uint[] values);

    uint public eventCounter;

    function emitSimpleEvent(string memory _message) public {
        eventCounter++;
        emit SimpleEvent(eventCounter, _message, msg.sender);
    }

    function emitArrayEvent(uint[] memory _numbers, string[] memory _messages) public {
        require(_numbers.length == _messages.length, "Arrays must be of equal length");
        eventCounter++;
        emit ArrayEvent(eventCounter, _numbers, _messages);
    }

    function emitStructEvent(string memory _name) public {
        eventCounter++;
        User memory user = User(eventCounter, _name, msg.sender);
        emit StructEvent(eventCounter, user);
    }

    function emitNestedEvent(uint _value, address[] memory _addresses, uint[] memory _values) public {
        require(_addresses.length == _values.length, "Arrays must be of equal length");
        eventCounter++;
        emit NestedEvent(eventCounter, _value, _addresses, _values);
    }

    function emitMappingEvent(address[] memory _addresses, uint[] memory _balances) public {
        require(_addresses.length == _balances.length, "Arrays must be of equal length");
        eventCounter++;
        emit MappingEvent(eventCounter, _addresses, _balances);
    }

    fallback() external {
        revert("Invalid call");
    }

    receive() external payable {
        revert("No ether accepted");
    }
}