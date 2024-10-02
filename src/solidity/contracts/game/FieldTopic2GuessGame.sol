// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";
import "./ContractTransparencyConfig.sol";

contract FieldTopic2GuessGame is GuessGame, ContractTransparencyConfig  {

    // set the Guessed event log config to everyone
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        bytes32 eventSig = hex"bc11465ed8ccb85c11046e78bf3d70287e3c77bf1c9542a3e250511bfb3c1b04";
        Field[]  memory relevantTo = new Field[](1);
        relevantTo[0] = Field.TOPIC2;
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](1);
        eventLogConfigs[0] = EventLogConfig(eventSig, relevantTo);
        return VisibilityConfig(ContractCfg.PRIVATE, eventLogConfigs);
    }
}