// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StoreAndRetrieve {
    struct Request {
        uint256 id;
        string data;
    }

    struct Response {
        uint256 id;
        string result;
    }

    struct Query {
        Request request;
        Response response;
    }

    mapping(uint256 => Query) public queries;

    function storeQuery(uint256 _id, string memory _requestData, string memory _responseResult, uint256 multiplier) external {
        queries[_id] = Query(Request(_id, _requestData), Response(_id, _responseResult));
        enlargeResponse(_id, multiplier);
    }

    function retrieveQuery(uint256 _id) public view virtual returns (Query memory) {
        return queries[_id];
    }

    function enlargeResponse(uint256 _id, uint256 multiplier) public {
        string memory originalResponse = queries[_id].response.result;
        string memory enlargedResponse;
        for (uint256 i = 0; i < multiplier; i++) {
            enlargedResponse = string(abi.encodePacked(enlargedResponse, originalResponse));
        }
        queries[_id].response.result = enlargedResponse;
    }
}