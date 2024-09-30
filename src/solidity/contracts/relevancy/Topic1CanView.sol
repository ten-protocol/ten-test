// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Relevancy.sol";
import "./ContractTransparencyConfig.sol";

contract Topic1CanView is Relevancy, ContractTransparencyConfig  {

    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        EventLogConfig[]  memory configs = new EventLogConfig[](1);
        configs[0] = EventLogConfig(hex"bc11465ed8ccb85c11046e78bf3d70287e3c77bf1c9542a3e250511bfb3c1b04", false, true, false, false, false);
        return VisibilityConfig(false, configs);
    }
}