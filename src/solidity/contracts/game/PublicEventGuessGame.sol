// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";

contract PublicEventGuessGame is GuessGame {

    function visibilityRules() public view returns (VisibilityConfig memory){
        configs[0] = EventLogConfig(hex"bc11465ed8ccb85c11046e78bf3d70287e3c77bf1c9542a3e250511bfb3c1b04", true, true, true, true, false);
        return VisibilityConfig(false, configs);
    }
}