// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// note that including here ensures that the contracts are compiled into the artifacts directory
import "@openzeppelin/contracts/proxy/beacon/UpgradeableBeacon.sol";
import "@openzeppelin/contracts/proxy/beacon/BeaconProxy.sol";

contract DoubleV1 {
    function doIt(uint x) public pure returns (uint) {
        return 2*x;
    }
}