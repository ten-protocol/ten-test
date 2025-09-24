// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";
import "./ContractTransparencyConfig.sol";

contract MaliciousTransparentConfigGuessGame is GuessGame, ContractTransparencyConfig  {

    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        uint256 n = 4294967296;
        uint256 a = 0;
        uint256 b = 1;

        for (uint256 i = 2; i <= n; i++) {
            uint256 next = a + b;
            a = b;
            b = next;
        }

        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](0);
        return VisibilityConfig(ContractCfg.TRANSPARENT, eventLogConfigs);
    }
}