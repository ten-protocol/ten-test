// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GuessGame.sol";
import "./ContractTransparencyConfig.sol";

contract FieldEveryoneAllEventsGuessGame is GuessGame, ContractTransparencyConfig  {

    // set the Guessed and Attempts event log config to everyone
    function visibilityRules() external pure override returns (VisibilityConfig memory) {
        Field[]  memory everyone = new Field[](1);
        everyone[0] = Field.EVERYONE;

        EventLogConfig[]  memory eventLogConfigs = new EventLogConfig[](2);
        eventLogConfigs[0] = EventLogConfig(hex"bc11465ed8ccb85c11046e78bf3d70287e3c77bf1c9542a3e250511bfb3c1b04", everyone);
        eventLogConfigs[1] = EventLogConfig(hex"3c226a964e404138fcf55a5ae0754352f8b942beb69cece51cf9a5d2063a43af", everyone);

        return VisibilityConfig(ContractCfg.PRIVATE, eventLogConfigs);
    }
}