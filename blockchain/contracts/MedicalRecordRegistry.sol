// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalRecordRegistry {
    struct RecordMetadata {
        string patientDid;
        string recordType;
        uint256 timestamp;
        address submitter; // Added submitter as per existing tests
    }

    mapping(bytes32 => RecordMetadata) private recordMetadataMap;
    mapping(bytes32 => bool) public recordExists; // As per existing tests

    // New state variable for the current subtask
    mapping(string => bytes32[]) private patientRecordHashes;

    // Mapping for access control: recordHash => doctorAddress => accessStatus
    mapping(bytes32 => mapping(address => bool)) internal recordAccessList;

    event RecordAdded(bytes32 indexed recordHash, string indexed patientDid, string recordType, uint256 timestamp, address indexed submitter);
    event AccessGranted(bytes32 indexed recordHash, address indexed ownerAddress, address indexed doctorAddress, uint256 timestamp);
    event AccessRevoked(bytes32 indexed recordHash, address indexed ownerAddress, address indexed doctorAddress, uint256 timestamp);

    error RecordAlreadyExists(bytes32 recordHash);
    error NotRecordOwner(bytes32 recordHash, address caller);

    // Modified addRecord to align with existing tests and integrate new functionality
    function addRecord(bytes32 recordHash, string calldata patientDid, string calldata recordType) external {
        if (recordExists[recordHash]) {
            revert RecordAlreadyExists(recordHash);
        }

        require(bytes(patientDid).length > 0, "Patient DID cannot be empty");
        require(bytes(recordType).length > 0, "Record type cannot be empty");

        recordMetadataMap[recordHash] = RecordMetadata(patientDid, recordType, block.timestamp, msg.sender);
        recordExists[recordHash] = true;

        // Integrate new functionality: store record hash for the patient
        patientRecordHashes[patientDid].push(recordHash);

        emit RecordAdded(recordHash, patientDid, recordType, block.timestamp, msg.sender);
    }

    function grantAccess(bytes32 recordHash, address doctorAddress) external {
        RecordMetadata memory metadata = recordMetadataMap[recordHash];
        // Ensure the record exists by checking if the submitter is not the zero address
        require(metadata.submitter != address(0), "Record does not exist"); 
        if (msg.sender != metadata.submitter) {
            revert NotRecordOwner(recordHash, msg.sender);
        }
        recordAccessList[recordHash][doctorAddress] = true;
        emit AccessGranted(recordHash, msg.sender, doctorAddress, block.timestamp);
    }

    function revokeAccess(bytes32 recordHash, address doctorAddress) external {
        RecordMetadata memory metadata = recordMetadataMap[recordHash];
        // Ensure the record exists by checking if the submitter is not the zero address
        require(metadata.submitter != address(0), "Record does not exist");
        if (msg.sender != metadata.submitter) {
            revert NotRecordOwner(recordHash, msg.sender);
        }
        recordAccessList[recordHash][doctorAddress] = false;
        emit AccessRevoked(recordHash, msg.sender, doctorAddress, block.timestamp);
    }

    function checkAccess(bytes32 recordHash, address accessorAddress) external view returns (bool) {
        return recordAccessList[recordHash][accessorAddress];
    }

    // getRecordMetadata function as per existing tests
    function getRecordMetadata(bytes32 recordHash) external view returns (RecordMetadata memory) {
        // The test expects default/empty values if record doesn't exist, not a revert.
        // This is implicitly handled by returning the default struct if not found.
        return recordMetadataMap[recordHash];
    }

    // New function to get record hashes by patient DID
    function getRecordHashesByPatient(string calldata patientDid) external view returns (bytes32[] memory) {
        return patientRecordHashes[patientDid];
    }
}
