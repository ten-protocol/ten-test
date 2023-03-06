//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "./IToken.sol";

contract GuessGame {
    address payable owner;
    uint8 private _target;
    address[] private _attemptAddresses;
    mapping(address => uint8) private _prevMisses;
    uint8 public guessRange;
    IToken public token;

    event Correct(address indexed player, uint8 guess, uint prize, uint allowance);
    event Incorrect(address indexed player, uint8 guess, uint prize, uint allowance);
    event Same(address indexed player, uint8 guess, uint prize, uint allowance);
    event Warmer(address indexed player, uint8 guess, uint prize, uint allowance);
    event Colder(address indexed player, uint8 guess, uint prize, uint allowance);

    constructor(uint8 range, address tokenAddress) {
        owner = payable(msg.sender);
        guessRange = range;
        token = IToken(tokenAddress);
        _setNewTarget();
    }

    function attempt(uint8 guess) public payable {
        require(token.allowance(msg.sender, address(this)) >= 1, "Check the token allowance.");

        _attemptAddresses.push(msg.sender);
        token.transferFrom(msg.sender, address(this), 1);
        if (guess == _target) {
            emit Correct(msg.sender, guess, prizePool(), token.allowance(msg.sender, address(this)));
            token.transfer(msg.sender, prizePool());
            _setNewTarget();
        } else {
            uint8 previous = _prevMisses[msg.sender];
            uint8 miss = guess > _target ? guess - _target : _target - guess;
            _prevMisses[msg.sender] = miss;
            if (previous == 0) {
                emit Incorrect(msg.sender, guess, prizePool(), token.allowance(msg.sender, address(this)));
            } else if (miss < previous) {
                emit Warmer(msg.sender, guess, prizePool(), token.allowance(msg.sender, address(this)));
            } else if (miss > previous) {
                emit Colder(msg.sender, guess, prizePool(), token.allowance(msg.sender, address(this)));
            } else {
                emit Same(msg.sender, guess, prizePool(), token.allowance(msg.sender, address(this)));
            }
        }
    }

    function close() public payable {
        require(msg.sender == owner, "Only owner can call this function.");

        selfdestruct(payable(owner));
    }

    function prizePool() public view returns (uint256) {
        return token.balanceOf(address(this));
    }

    function _setNewTarget() private {
        require(token.balanceOf(address(this)) == 0, "Balance must be zero to set a new target.");

        for (uint16 i = 0; i < _attemptAddresses.length; i++) {
            _prevMisses[_attemptAddresses[i]] = 0;
        }
        delete _attemptAddresses;
        _target = uint8(
            uint256(
                keccak256(abi.encodePacked(block.timestamp, block.difficulty))
            ) % guessRange
        );
    }
}
