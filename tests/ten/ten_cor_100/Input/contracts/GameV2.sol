// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractTransparencyConfig.sol";
import "./GameV1.sol";

contract GameV2 is GameV1 {

    // virtual getter for max guess range — override in derived contracts
    function maxGuess() internal pure override returns (uint256) {
        return 20;
    }
}