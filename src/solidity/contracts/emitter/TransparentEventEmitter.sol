// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EventEmitter.sol";
import "./ContractTransparencyConfig.sol";

contract TransparentEventEmitter is EventEmitter, ContractTransparencyConfig {

    // set the visibility config to make the contract fully open
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](0);
        return VisibilityConfig(ContractCfg.TRANSPARENT, eventLogConfigs);
    }
}