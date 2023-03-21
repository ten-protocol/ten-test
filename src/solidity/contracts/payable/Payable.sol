// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReceiveEther {
    event Received(string key, uint value);

    /*
                send Ether
                    |
             msg.data is empty?
              /              \
            yes               no
            /                   \
      receive() exists?        call data receiveFunds
         /       \                  /           \
       yes        no              yes           no
        |          |               |             |
    receive()  fallback()    receiveFunds()   fallback()
    */

    receive() external payable {
        emit Received("receive", msg.value);
    }

    fallback() external payable {
        emit Received("fallback", msg.value);
    }

    function receiveFunds() public payable {
        emit Received("receiveFunds", msg.value);
    }

    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}

contract SendEther {
    event Send(string key, uint value);

    function sendViaTransfer(address payable _to) public payable {
        emit Send("sendViaTransfer", msg.value);
        _to.transfer(msg.value);
    }

    function sendViaSend(address payable _to) public payable {
        emit Send("sendViaSend", msg.value);
        bool sent = _to.send(msg.value);
        require(sent, "Failed to send Ether");
    }

    function sendViaCall(address payable _to) public payable {
        emit Send("sendViaCall", msg.value);
        (bool sent, bytes memory data) = _to.call{value: msg.value}("");
        require(sent, "Failed to send Ether");
    }
}