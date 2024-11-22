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

    function force_require_non_view(string memory newKey) public {
        require(bytes(newKey).length == 0, "Forced require on key length not zero");
        key = newKey;
    }

    function force_revert() public view {
        revert("Forced revert");
    }

    function force_assert() public view {
        assert(false);
    }

    function set_key_with_require(string memory newKey) public {
        require(bytes(newKey).length != 0, "New key cannot be empty");
        key = newKey;
    }

    function set_key_with_revert(string memory newKey) public {
        if (bytes(newKey).length == 0){
            revert("New key cannot be empty");
        }
        key = newKey;
    }

    function get_key() public view returns (string memory) {
        return key;
    }
}