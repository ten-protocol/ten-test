// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SelfDestructOnDeploy {

    constructor(address payable recipient) payable {
        selfdestruct(recipient);
    }

    function hello() public pure returns (string memory) {
        return "Hello, world!";
    }
}