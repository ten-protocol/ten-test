// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract StoreV1 is Initializable, OwnableUpgradeable {
    uint256 number;

    function initialize() public initializer {
        __Ownable_init();
        number = 100;
    }

    function store(uint256 num) public {
        number = num;
    }

    function retrieve() public view virtual returns (uint256){
        return number;
    }
}