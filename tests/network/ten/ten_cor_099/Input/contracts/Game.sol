// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractTransparencyConfig.sol";

contract Game is ContractTransparencyConfig {
    address private owner;
    uint256 private secretNumber;
    uint256 public totalGuesses;
    mapping(address => uint256) public attempts;

    // events emitted by the game
    event Guessed(address indexed user, uint256 guessedNumber, bool success, uint256 secretNumber);
    event Attempts(address indexed user, uint256 attempts);

    // set the visibility config to make the contract fully open
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](0);
        return VisibilityConfig(ContractCfg.TRANSPARENT, eventLogConfigs);
    }

    constructor() {
        owner = msg.sender;
        _resetSecretNumber();
    }

    function guess(uint256 _number) public {
        require(_number > 0 && _number <= maxGuess(), 'Secret number should be between 1 and 10');
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

    // virtual getter for max guess range — override in derived contracts
    function maxGuess() internal view virtual returns (uint256) {
        return 10;
    }
}