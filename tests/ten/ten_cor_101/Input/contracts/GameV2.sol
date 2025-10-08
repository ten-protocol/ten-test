// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractTransparencyConfig.sol";
import "./GameV1.sol";

contract GameV2 is GameV1, ContractTransparencyConfig {

    // set the visibility config to make the contract fully open
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](0);
        return VisibilityConfig(ContractCfg.TRANSPARENT, eventLogConfigs);
    }

    // virtual getter for max guess range — override in derived contracts
    function maxGuess() internal pure override returns (uint256) {
        return 20;
    }
}