// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IPublicCallbacks {
    function register(bytes calldata callback) external payable;
    function reattemptCallback(uint256 callbackId) external;
}

contract GuessGameTwoPhase {
    IPublicCallbacks public callbacks;

    address private owner;
    uint256 private secretNumber;
    uint256 public totalGuesses;
    mapping(address => uint256) public attempts;

    // constants
    uint256 public constant MAX_GUESS = 10;

    // events emitted by the game
    event Guessed(address indexed user, uint256 guessedNumber, bool success, uint256 secretNumber);
    event Attempts(address indexed user, uint256 attempts);

    constructor(address _callbacks) {
        callbacks = IPublicCallbacks(_callbacks);
        owner = msg.sender;
        _resetSecretNumber();
    }

    function guess(uint256 _number) public payable {
        bytes memory callbackData = abi.encodeWithSelector(this.handleGuess.selector, _number, msg.sender);
        callbacks.register{value: msg.value}(callbackData);
    }

    function handleGuess(uint256 _number, address originator) external {
        require(msg.sender == address(callbacks));
        require(_number > 0 && _number <= MAX_GUESS, 'Secret number should be between 1 and 1000');
        totalGuesses += 1;
        attempts[originator] += 1;

        if (_number == secretNumber) {
            emit Guessed(originator, _number, true, secretNumber);
            _resetSecretNumber();
            totalGuesses = 0;
        } else {
            emit Guessed(originator, _number, false, secretNumber);
        }
        emit Attempts(originator, attempts[originator]);
    }

    function _resetSecretNumber() private {
        uint256 randomNumber = uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp)));
        secretNumber = (randomNumber % 10) + 1;
    }
}