// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";
import "./ContractTransparencyConfig.sol";

contract ZeroEventSigGuessGame is GuessGame, ContractTransparencyConfig  {

    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        bytes32 eventSig = hex"0000000000000000000000000000000000000000000000000000000000000000";
        Field[]  memory relevantTo = new Field[](0);
        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](1);
        eventLogConfigs[0] = EventLogConfig(eventSig, relevantTo);
        return VisibilityConfig(ContractCfg.PRIVATE, eventLogConfigs);
    }
}