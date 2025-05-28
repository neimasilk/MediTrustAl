// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserRegistry {
    struct User {
        string userId;
        string role;
        bool isRegistered;
    }

    mapping(string => User) public users;
    address public owner;

    event UserRegistered(string userId, string role);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    function registerUser(string memory _userId, string memory _role) public {
        require(bytes(users[_userId].userId).length == 0, "User ID already registered");
        require(!users[_userId].isRegistered, "User flag indicates already registered");

        users[_userId] = User({
            userId: _userId,
            role: _role,
            isRegistered: true
        });

        emit UserRegistered(_userId, _role);
    }

    function getUserRole(string memory _userId) public view returns (string memory, bool) {
        return (users[_userId].role, users[_userId].isRegistered);
    }
}