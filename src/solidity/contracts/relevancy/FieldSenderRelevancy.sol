// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Relevancy.sol";
import "./ContractTransparencyConfig.sol";

contract FieldSenderRelevancy is Relevancy, ContractTransparencyConfig  {

    // set the TwoIndexedAddresses event log config to include the sender
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        bytes32 eventSig = hex"85217d12aec82988299a2d33c06c6d141fb9af7717cb74856740aad1f0a3b8e9";
        Field[]  memory relevantTo = new Field[](3);
        relevantTo[0] = Field.TOPIC1;
        relevantTo[1] = Field.TOPIC2;
        relevantTo[2] = Field.SENDER;
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](1);
        eventLogConfigs[0] = EventLogConfig(eventSig, relevantTo);
        return VisibilityConfig(ContractCfg.PRIVATE, eventLogConfigs);
    }
}