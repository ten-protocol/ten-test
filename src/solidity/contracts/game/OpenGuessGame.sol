// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ContractTransparencyConfig {
    struct EventLogConfig {
        bytes eventSignature;
        bool isPublic;
        bool topic1CanView;
        bool topic2CanView;
        bool topic3CanView;
        bool visibleToSender;
    }

    struct VisibilityConfig {
        bool isTransparent;
        EventLogConfig[] eventLogConfigs;
    }

    function visibilityRules() external pure returns (VisibilityConfig memory);
}

contract OpenGuessGame is ContractTransparencyConfig {
    address private owner;
    uint256 private secretNumber;
    uint256 public totalGuesses;

    // constants
    uint256 public constant MAX_GUESS = 10;

    event Guessed(address indexed user, uint256 guessedNumber, bool success, uint256 secretNumber);

    constructor() {
        owner = msg.sender;
        _resetSecretNumber();
    }

    function visibilityRules() public override pure returns (VisibilityConfig memory){
        return VisibilityConfig(true, new EventLogConfig[](0));
    }

    function guess(uint256 _number) public {
        require(_number > 0 && _number <= MAX_GUESS, 'Secret number should be between 1 and 1000');
        totalGuesses += 1;

        if (_number == secretNumber) {
            emit Guessed(msg.sender, _number, true, secretNumber);
            _resetSecretNumber();
            totalGuesses = 0;
        } else {
            emit Guessed(msg.sender, _number, false, secretNumber);
        }
    }

    function _resetSecretNumber() private {
        uint256 randomNumber = uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp)));
        secretNumber = (randomNumber % 10) + 1;
    }
}