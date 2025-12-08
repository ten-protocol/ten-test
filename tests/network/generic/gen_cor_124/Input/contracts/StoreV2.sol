// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;
import "./StoreV1.sol";

contract StoreV2 is StoreV1 {

    function retrieve() public view override returns (uint256){
        return 2*number;
    }

}