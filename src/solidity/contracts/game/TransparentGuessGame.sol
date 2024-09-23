// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";

contract TransparentGuessGame is GuessGame {

    function visibilityRules() public view returns (VisibilityConfig memory){
        return VisibilityConfig(true, new EventLogConfig[](0));
    }
}