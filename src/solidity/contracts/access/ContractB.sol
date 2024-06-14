// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ContractB {
    address public contractA;

    function setContractA(address _contractA) public {
        contractA = _contractA;
    }

    function setContractAValue(uint256 _value) public {
        (bool success, ) = contractA.call(abi.encodeWithSignature("setValue(uint256)", _value));
        require(success, "Call to ContractA failed");
    }
}