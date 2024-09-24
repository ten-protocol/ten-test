// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";
import "./ContractTransparencyConfig.sol";

contract TransparentGuessGame is GuessGame, ContractTransparencyConfig  {

    // set the isTransparent property of the contract to true
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        return VisibilityConfig(true, new EventLogConfig[](0));
    }
}