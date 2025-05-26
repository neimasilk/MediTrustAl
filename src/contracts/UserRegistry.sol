// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title UserRegistry
 * @dev Smart contract for managing user registration and roles in MediTrustAl
 */
contract UserRegistry {
    // User roles
    enum Role { PATIENT, DOCTOR, ADMIN }

    // User structure
    struct User {
        string did;          // Decentralized Identifier
        Role role;          // User role
        uint256 timestamp;  // Registration timestamp
        bool isActive;      // User status
    }

    // Mapping from DID to User
    mapping(string => User) private users;
    
    // Array to keep track of all DIDs
    string[] private userDids;

    // Events
    event UserRegistered(string did, Role role, uint256 timestamp);
    event UserDeactivated(string did, uint256 timestamp);
    event UserReactivated(string did, uint256 timestamp);

    // Modifiers
    modifier didNotExists(string memory _did) {
        require(bytes(users[_did].did).length == 0, "User already exists");
        _;
    }

    modifier didExists(string memory _did) {
        require(bytes(users[_did].did).length > 0, "User does not exist");
        _;
    }

    /**
     * @dev Register a new user
     * @param _did Decentralized Identifier of the user
     * @param _role Role of the user (0=PATIENT, 1=DOCTOR, 2=ADMIN)
     */
    function registerUser(string memory _did, Role _role) 
        public 
        didNotExists(_did) 
    {
        User memory newUser = User({
            did: _did,
            role: _role,
            timestamp: block.timestamp,
            isActive: true
        });

        users[_did] = newUser;
        userDids.push(_did);

        emit UserRegistered(_did, _role, block.timestamp);
    }

    /**
     * @dev Get user details
     * @param _did Decentralized Identifier of the user
     * @return User details (did, role, timestamp, isActive)
     */
    function getUser(string memory _did) 
        public 
        view 
        didExists(_did) 
        returns (User memory) 
    {
        return users[_did];
    }

    /**
     * @dev Check if a user exists and is active
     * @param _did Decentralized Identifier of the user
     * @return bool indicating if user exists and is active
     */
    function isActiveUser(string memory _did) 
        public 
        view 
        returns (bool) 
    {
        return users[_did].isActive;
    }

    /**
     * @dev Get user role
     * @param _did Decentralized Identifier of the user
     * @return Role of the user
     */
    function getUserRole(string memory _did) 
        public 
        view 
        didExists(_did) 
        returns (Role) 
    {
        return users[_did].role;
    }

    /**
     * @dev Deactivate a user
     * @param _did Decentralized Identifier of the user
     */
    function deactivateUser(string memory _did) 
        public 
        didExists(_did) 
    {
        require(users[_did].isActive, "User is already inactive");
        users[_did].isActive = false;
        emit UserDeactivated(_did, block.timestamp);
    }

    /**
     * @dev Reactivate a user
     * @param _did Decentralized Identifier of the user
     */
    function reactivateUser(string memory _did) 
        public 
        didExists(_did) 
    {
        require(!users[_did].isActive, "User is already active");
        users[_did].isActive = true;
        emit UserReactivated(_did, block.timestamp);
    }

    /**
     * @dev Get total number of registered users
     * @return uint256 Total number of users
     */
    function getTotalUsers() 
        public 
        view 
        returns (uint256) 
    {
        return userDids.length;
    }
} 