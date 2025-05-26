const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MedicalRecordRegistry", function () {
    let MedicalRecordRegistry;
    let medicalRecordRegistry;
    let owner;
    let addr1;
    let addr2;

    beforeEach(async function () {
        // Get the ContractFactory and Signers here.
        MedicalRecordRegistry = await ethers.getContractFactory("MedicalRecordRegistry");
        [owner, addr1, addr2] = await ethers.getSigners();

        // Deploy a new MedicalRecordRegistry contract before each test.
        medicalRecordRegistry = await MedicalRecordRegistry.deploy();
        // No need to call waitForDeployment() here, it's done by default in deploy()
        // For ethers.js v5, contract.deployed() was used. For v6, deploy() returns a promise that resolves when deployed.
        // If you are using an older Hardhat setup or specific ethers version, you might need `await medicalRecordRegistry.deployed();`
    });

    describe("Deployment", function () {
        it("Should set the right owner", async function () {
            // The owner who deploys the contract is not explicitly stored in this contract,
            // but msg.sender in transactions will be the deployer initially.
            // This test is more of a sanity check that deployment worked.
            expect(await medicalRecordRegistry.getAddress()).to.not.equal(ethers.ZeroAddress);
        });
    });

    describe("addRecord", function () {
        it("Should add a new record successfully", async function () {
            const recordHash = ethers.encodeBytes32String("testRecordHash1");
            const patientDid = "did:example:patient123";
            const recordType = "DIAGNOSIS";

            // Call addRecord from addr1's perspective
            const tx = await medicalRecordRegistry.connect(addr1).addRecord(recordHash, patientDid, recordType);
            const receipt = await tx.wait(); // Wait for transaction to be mined

            // Check if RecordAdded event was emitted
            // Hardhat Chai Matchers for events: https://hardhat.org/hardhat-chai-matchers/docs/reference#events
            await expect(tx)
                .to.emit(medicalRecordRegistry, "RecordAdded")
                .withArgs(recordHash, patientDid, recordType, (await ethers.provider.getBlock(receipt.blockNumber)).timestamp, addr1.address);

            // Verify stored metadata using getRecordMetadata
            const metadata = await medicalRecordRegistry.getRecordMetadata(recordHash);
            expect(metadata.patientDid).to.equal(patientDid);
            expect(metadata.recordType).to.equal(recordType);
            expect(metadata.submitter).to.equal(addr1.address);
            expect(metadata.timestamp).to.be.gt(0); // Timestamp should be set

            // Verify existence using recordExists mapping
            expect(await medicalRecordRegistry.recordExists(recordHash)).to.be.true;
        });

        it("Should revert if adding a duplicate recordHash", async function () {
            const recordHash = ethers.encodeBytes32String("testRecordHashDuplicate");
            const patientDid = "did:example:patient456";
            const recordType = "LAB_RESULT";

            // Add the record for the first time
            await medicalRecordRegistry.connect(addr1).addRecord(recordHash, patientDid, recordType);

            // Attempt to add the same recordHash again
            await expect(
                medicalRecordRegistry.connect(addr2).addRecord(recordHash, patientDid, "PRESCRIPTION")
            ).to.be.revertedWithCustomError(medicalRecordRegistry, "RecordAlreadyExists")
             .withArgs(recordHash);
        });

        it("Should store different records with different hashes correctly", async function () {
            const recordHash1 = ethers.encodeBytes32String("multiRecordHash1");
            const patientDid1 = "did:example:multiPatient1";
            const recordType1 = "DIAGNOSIS";
            await medicalRecordRegistry.connect(addr1).addRecord(recordHash1, patientDid1, recordType1);

            const recordHash2 = ethers.encodeBytes32String("multiRecordHash2");
            const patientDid2 = "did:example:multiPatient2";
            const recordType2 = "PRESCRIPTION";
            await medicalRecordRegistry.connect(addr2).addRecord(recordHash2, patientDid2, recordType2);

            const metadata1 = await medicalRecordRegistry.getRecordMetadata(recordHash1);
            expect(metadata1.patientDid).to.equal(patientDid1);
            expect(metadata1.submitter).to.equal(addr1.address);

            const metadata2 = await medicalRecordRegistry.getRecordMetadata(recordHash2);
            expect(metadata2.patientDid).to.equal(patientDid2);
            expect(metadata2.submitter).to.equal(addr2.address);
        });
    });

    describe("getRecordMetadata", function () {
        it("Should return correct metadata for an existing record", async function () {
            const recordHash = ethers.encodeBytes32String("getMetaTestHash");
            const patientDid = "did:example:getMetaPatient";
            const recordType = "TREATMENT_PLAN";
            const tx = await medicalRecordRegistry.connect(addr1).addRecord(recordHash, patientDid, recordType);
            const receipt = await tx.wait();
            const expectedTimestamp = (await ethers.provider.getBlock(receipt.blockNumber)).timestamp;

            const metadata = await medicalRecordRegistry.getRecordMetadata(recordHash);
            expect(metadata.patientDid).to.equal(patientDid);
            expect(metadata.recordType).to.equal(recordType);
            expect(metadata.timestamp).to.equal(expectedTimestamp);
            expect(metadata.submitter).to.equal(addr1.address);
        });

        it("Should return empty/default values for a non-existent record hash", async function () {
            const nonExistentHash = ethers.encodeBytes32String("nonExistentHash");
            const metadata = await medicalRecordRegistry.getRecordMetadata(nonExistentHash);

            expect(metadata.patientDid).to.equal(""); // Default for string
            expect(metadata.recordType).to.equal(""); // Default for string
            expect(metadata.timestamp).to.equal(0);    // Default for uint256
            expect(metadata.submitter).to.equal(ethers.ZeroAddress); // Default for address
        });
    });
});
