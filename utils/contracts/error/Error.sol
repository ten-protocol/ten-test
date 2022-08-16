// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Error {
    string public key = "foo";

    function set(string memory _key) public {
        key = _key;
    }

    function force_require() public view {
        require(false, "Value needs to equal key");
    }

    function force_revert(string memory value) public view {
        revert("Supplied value does not equal the key");
    }

    function force_assert(string memory value) public view{
        assert(false);
    }
}