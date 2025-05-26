// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "hardhat/console.sol"; // Optional: For debugging

contract MedicalRecordRegistry {
    struct RecordMetadata {
        string patientDid; // DID of the patient
        string recordType; // Type of medical record (e.g., DIAGNOSIS, LAB_RESULT)
        uint256 timestamp; // Timestamp of when the record was added to the blockchain
        address submitter; // Address of the entity that submitted the record hash
    }

    mapping(bytes32 => RecordMetadata) public recordHashes;
    mapping(bytes32 => bool) public recordExists; // To check for existence efficiently

    event RecordAdded(
        bytes32 indexed recordHash,
        string indexed patientDid,
        string recordType,
        uint256 timestamp,
        address submitter
    );

    error RecordAlreadyExists(bytes32 recordHash);

    /**
     * @dev Adds a new medical record hash along with its metadata.
     * @param _recordHash The SHA-256 hash of the encrypted medical record data.
     * @param _patientDid The Decentralized Identifier (DID) of the patient.
     * @param _recordType The type of the medical record (e.g., "DIAGNOSIS", "LAB_RESULT").
     */
    function addRecord(
        bytes32 _recordHash,
        string memory _patientDid,
        string memory _recordType
    ) public {
        if (recordExists[_recordHash]) {
            revert RecordAlreadyExists(_recordHash);
        }

        recordHashes[_recordHash] = RecordMetadata(
            _patientDid,
            _recordType,
            block.timestamp,
            msg.sender
        );
        recordExists[_recordHash] = true;

        emit RecordAdded(
            _recordHash,
            _patientDid,
            _recordType,
            block.timestamp,
            msg.sender
        );
    }

    /**
     * @dev Retrieves the metadata for a given medical record hash.
     * @param _recordHash The SHA-256 hash of the medical record.
     * @return patientDid The DID of the patient.
     * @return recordType The type of the medical record.
     * @return timestamp The timestamp when the record was added.
     * @return submitter The address of the submitter.
     */
    function getRecordMetadata(bytes32 _recordHash)
        public
        view
        returns (
            string memory patientDid,
            string memory recordType,
            uint256 timestamp,
            address submitter
        )
    {
        RecordMetadata storage metadataRecord = recordHashes[_recordHash];
        // No explicit check for existence here, will return default values if not found.
        // Consider adding a check if returning default values is not desired.
        return (
            metadataRecord.patientDid,
            metadataRecord.recordType,
            metadataRecord.timestamp,
            metadataRecord.submitter
        );
    }
}
