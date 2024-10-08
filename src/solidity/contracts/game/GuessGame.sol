// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GuessGame {
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