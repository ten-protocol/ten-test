// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface ContractTransparencyConfig {
    // configuration per event log type
    struct EventLogConfig {
        bytes eventSignature;
        bool isPublic;        // everyone can see and query for this event
        bool topic1CanView;   // if private and true the address from topic1 is an EOA that can view
        bool topic2CanView;   // if private and true the address from topic2 is an EOA that can view
        bool topic3CanView;   // if private and true the address from topic2 is an EOA that can view
        bool visibleToSender; // if true, the tx signer will see this event
    }

    struct VisibilityConfig {
        bool isTransparent;  // if true getStorageAt will be accessible to everyone, and all events will be public
        EventLogConfig[] eventLogConfigs; // if an event is not included, semantics fall back to previous behaviour
    }

    // keep the logic independent of the environment
    function visibilityRules() external pure returns (VisibilityConfig memory);
}

contract TransparentGuessGameOneFile is ContractTransparencyConfig {
    address private owner;
    uint256 private secretNumber;
    uint256 public totalGuesses;
    mapping(address => uint256) public attempts;

    // constants
    uint256 public constant MAX_GUESS = 10;

    // events emitted by the game
    event Guessed(address indexed user, uint256 guessedNumber, bool success, uint256 secretNumber);
    event Attempts(address indexed user, uint256 attempts);

    constructor() {
        owner = msg.sender;
        _resetSecretNumber();
    }

    // set the isTransparent property of the contract to true
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        return VisibilityConfig(true, new EventLogConfig[](0));
    }

    function guess(uint256 _number) public {
        require(_number > 0 && _number <= MAX_GUESS, 'Secret number should be between 1 and 1000');
        totalGuesses += 1;
        attempts[msg.sender] += 1;

        if (_number == secretNumber) {
            emit Guessed(msg.sender, _number, true, secretNumber);
            _resetSecretNumber();
            totalGuesses = 0;
        } else {
            emit Guessed(msg.sender, _number, false, secretNumber);
        }
        emit Attempts(msg.sender, attempts[msg.sender]);
    }

    function _resetSecretNumber() private {
        uint256 randomNumber = uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp)));
        secretNumber = (randomNumber % 10) + 1;
    }
}
