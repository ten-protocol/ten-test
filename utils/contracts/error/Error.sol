// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Error {
    string public key = "foo";

    function set(string memory _key) public {
        key = _key;
    }

    function force_require() public view {
        require(false, "Forced require");
    }

    function force_revert() public view {
        revert("Forced revert");
    }

    function force_assert() public view{
        assert(false);
    }
}