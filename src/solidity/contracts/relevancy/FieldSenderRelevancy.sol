// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Relevancy.sol";
import "./ContractTransparencyConfig.sol";

contract FieldSenderRelevancy is Relevancy, ContractTransparencyConfig  {

    // set the TwoIndexedAddresses event log config to sender only
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        bytes32 eventSig = hex"bd0c34a389065c93b7dd305b36de77856672fb59b283b31e9f43dc0cf48898b0";
        Field[]  memory relevantTo = new Field[](1);
        relevantTo[0] = Field.SENDER;
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](1);
        eventLogConfigs[0] = EventLogConfig(eventSig, relevantTo);
        return VisibilityConfig(ContractCfg.PRIVATE, eventLogConfigs);
    }
}