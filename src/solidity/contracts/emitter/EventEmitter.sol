pragma solidity ^0.8.0;

contract EventEmitter {
    struct User {uint256 id; string name; address userAddress;}
    event SimpleEvent(uint256 indexed id, string message, address indexed sender);
    event AddressEvent(uint256 indexed id, address indexed _address);
    event ArrayEvent(uint256 indexed id, uint256[] numbers, string[] messages);
    event StructEvent(uint256 indexed id, User user);
    event MappingEvent(uint256 indexed id, address[] keys, uint256[] values);

    uint256 public eventCounter;

    function emitSimpleEvent(uint256 id, string memory _message) public {
        emit SimpleEvent(id, _message, msg.sender);
    }

    function emitAddressEvent(uint256 id, address _address) public {
        emit AddressEvent(id, _address);
    }

    function emitArrayEvent(uint256 id, uint256[] memory _numbers, string[] memory _messages) public {
        require(_numbers.length == _messages.length, "Arrays must be of equal length");
        emit ArrayEvent(id, _numbers, _messages);
    }

    function emitStructEvent(uint256 id, string memory _name) public {
        User memory user = User(eventCounter, _name, msg.sender);
        emit StructEvent(id, user);
    }

    function emitMappingEvent(uint256 id, address[] memory _addresses, uint256[] memory _balances) public {
        require(_addresses.length == _balances.length, "Arrays must be of equal length");
        emit MappingEvent(id, _addresses, _balances);
    }

    fallback() external { revert("Invalid call"); }
    receive() external payable { revert("No ether accepted"); }
}