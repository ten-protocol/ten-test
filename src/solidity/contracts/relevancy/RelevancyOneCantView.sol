// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Relevancy.sol";
import "./ContractTransparencyConfig.sol";

contract RelevancyOneCantView is Relevancy, ContractTransparencyConfig  {

    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        EventLogConfig[]  memory configs = new EventLogConfig[](1);

        //TwoIndexedAddresses
        configs[0] = EventLogConfig(hex"bd0c34a389065c93b7dd305b36de77856672fb59b283b31e9f43dc0cf48898b0", false, true, false, true, false);
        return VisibilityConfig(false, configs);
    }
}