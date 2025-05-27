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

    describe("getRecordHashesByPatient", function () {
        it("Should return correct record hashes for a patient with multiple records", async function () {
            const patientDid1 = "did:example:patientWithMultipleRecords";
            const recordHash1 = ethers.encodeBytes32String("patient1RecordHash1");
            const recordHash2 = ethers.encodeBytes32String("patient1RecordHash2");
            const recordType1 = "IMMUNIZATION";
            const recordType2 = "ALLERGY";

            await medicalRecordRegistry.connect(addr1).addRecord(recordHash1, patientDid1, recordType1);
            await medicalRecordRegistry.connect(addr1).addRecord(recordHash2, patientDid1, recordType2);

            const hashes = await medicalRecordRegistry.getRecordHashesByPatient(patientDid1);
            expect(hashes).to.have.lengthOf(2);
            expect(hashes).to.include(recordHash1);
            expect(hashes).to.include(recordHash2);
        });

        it("Should return an empty array for a patient with no records", async function () {
            const patientDidNoRecords = "did:example:patientWithNoRecords";
            const hashes = await medicalRecordRegistry.getRecordHashesByPatient(patientDidNoRecords);
            expect(hashes).to.be.an('array').that.is.empty;
        });

        it("Should return correct record hashes for multiple different patients", async function () {
            const patientDidA = "did:example:patientA";
            const recordHashA1 = ethers.encodeBytes32String("patientARecordHash1");
            const recordTypeA1 = "CONSULTATION";
            await medicalRecordRegistry.connect(addr1).addRecord(recordHashA1, patientDidA, recordTypeA1);

            const patientDidB = "did:example:patientB";
            const recordHashB1 = ethers.encodeBytes32String("patientBRecordHash1");
            const recordHashB2 = ethers.encodeBytes32String("patientBRecordHash2");
            const recordTypeB1 = "IMAGING_STUDY";
            const recordTypeB2 = "PATHOLOGY_REPORT";
            await medicalRecordRegistry.connect(addr2).addRecord(recordHashB1, patientDidB, recordTypeB1);
            await medicalRecordRegistry.connect(addr2).addRecord(recordHashB2, patientDidB, recordTypeB2);
            
            // Verify for patient A
            const hashesA = await medicalRecordRegistry.getRecordHashesByPatient(patientDidA);
            expect(hashesA).to.have.lengthOf(1);
            expect(hashesA).to.include(recordHashA1);

            // Verify for patient B
            const hashesB = await medicalRecordRegistry.getRecordHashesByPatient(patientDidB);
            expect(hashesB).to.have.lengthOf(2);
            expect(hashesB).to.include(recordHashB1);
            expect(hashesB).to.include(recordHashB2);

            // Verify for a patient with no records added yet in this test context
            const patientDidC = "did:example:patientC_NoRecordsInThisTest";
            const hashesC = await medicalRecordRegistry.getRecordHashesByPatient(patientDidC);
            expect(hashesC).to.be.an('array').that.is.empty;
        });
    });

    describe("Access Control", function () {
        let recordHash;
        let patientDid;
        let recordType;
        let ownerAddress; // Will be addr1 who adds the record
        let doctorAddress; // Will be addr2

        beforeEach(async function () {
            recordHash = ethers.encodeBytes32String("accessTestRecordHash");
            patientDid = "did:example:accessPatient";
            recordType = "X-RAY";
            ownerAddress = addr1; // addr1 will submit the record
            doctorAddress = addr2; // addr2 will be the doctor

            // Add a record as addr1
            await medicalRecordRegistry.connect(ownerAddress).addRecord(recordHash, patientDid, recordType);
        });

        describe("grantAccess", function () {
            it("Should allow record owner to grant access and emit AccessGranted event", async function () {
                const grantTx = await medicalRecordRegistry.connect(ownerAddress).grantAccess(recordHash, doctorAddress.address);
                const receipt = await grantTx.wait();
                const expectedTimestamp = (await ethers.provider.getBlock(receipt.blockNumber)).timestamp;

                await expect(grantTx)
                    .to.emit(medicalRecordRegistry, "AccessGranted")
                    .withArgs(recordHash, ownerAddress.address, doctorAddress.address, expectedTimestamp);

                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.true;
            });

            it("Should revert if non-owner tries to grant access", async function () {
                await expect(
                    medicalRecordRegistry.connect(doctorAddress).grantAccess(recordHash, ownerAddress.address) // doctorAddress (addr2) is not the owner
                ).to.be.revertedWithCustomError(medicalRecordRegistry, "NotRecordOwner")
                 .withArgs(recordHash, doctorAddress.address);
            });

            it("Should revert if trying to grant access to a non-existent record", async function () {
                const nonExistentRecordHash = ethers.encodeBytes32String("nonExistentForAccess");
                await expect(
                    medicalRecordRegistry.connect(ownerAddress).grantAccess(nonExistentRecordHash, doctorAddress.address)
                ).to.be.revertedWith("Record does not exist"); // Using require message from contract
            });
        });

        describe("revokeAccess", function () {
            beforeEach(async function () {
                // Grant access first before attempting to revoke
                await medicalRecordRegistry.connect(ownerAddress).grantAccess(recordHash, doctorAddress.address);
                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.true; // Verify access was granted
            });

            it("Should allow record owner to revoke access and emit AccessRevoked event", async function () {
                const revokeTx = await medicalRecordRegistry.connect(ownerAddress).revokeAccess(recordHash, doctorAddress.address);
                const receipt = await revokeTx.wait();
                const expectedTimestamp = (await ethers.provider.getBlock(receipt.blockNumber)).timestamp;

                await expect(revokeTx)
                    .to.emit(medicalRecordRegistry, "AccessRevoked")
                    .withArgs(recordHash, ownerAddress.address, doctorAddress.address, expectedTimestamp);

                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.false;
            });

            it("Should revert if non-owner tries to revoke access", async function () {
                // Attempt to revoke by addr2 (doctorAddress), who is not the owner
                await expect(
                    medicalRecordRegistry.connect(doctorAddress).revokeAccess(recordHash, doctorAddress.address)
                ).to.be.revertedWithCustomError(medicalRecordRegistry, "NotRecordOwner")
                 .withArgs(recordHash, doctorAddress.address);
            });

            it("Should revert if trying to revoke access to a non-existent record", async function () {
                const nonExistentRecordHash = ethers.encodeBytes32String("nonExistentForRevoke");
                await expect(
                    medicalRecordRegistry.connect(ownerAddress).revokeAccess(nonExistentRecordHash, doctorAddress.address)
                ).to.be.revertedWith("Record does not exist");
            });

            it("Should not change access status if revoking access that was never granted", async function () {
                const anotherDoctorAddress = addr2; // Using addr2 again, but imagine it's a different doctor for clarity
                // Ensure anotherDoctorAddress does not have access initially for this specific test logic.
                // Note: in the global beforeEach, doctorAddress (addr2) *was* granted access.
                // For this specific test, we want to test revoking from someone who *never* had it for *this* record.
                // However, our current setup grants access to doctorAddress (addr2) in the top-level beforeEach.
                // So, let's use a new address that definitely doesn't have access.
                const newDoctorWithoutAccess = ethers.Wallet.createRandom().address;

                expect(await medicalRecordRegistry.checkAccess(recordHash, newDoctorWithoutAccess)).to.be.false;

                const revokeTx = await medicalRecordRegistry.connect(ownerAddress).revokeAccess(recordHash, newDoctorWithoutAccess);
                const receipt = await revokeTx.wait();
                const expectedTimestamp = (await ethers.provider.getBlock(receipt.blockNumber)).timestamp;

                await expect(revokeTx)
                    .to.emit(medicalRecordRegistry, "AccessRevoked") // Event is still emitted as owner can try to revoke
                    .withArgs(recordHash, ownerAddress.address, newDoctorWithoutAccess, expectedTimestamp);

                expect(await medicalRecordRegistry.checkAccess(recordHash, newDoctorWithoutAccess)).to.be.false; // Still false
            });
        });

        describe("checkAccess", function () {
            it("Should return true if access has been granted", async function () {
                await medicalRecordRegistry.connect(ownerAddress).grantAccess(recordHash, doctorAddress.address);
                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.true;
            });

            it("Should return false if access has not been granted", async function () {
                // Ensure no access for a new address
                const anotherDoctor = ethers.Wallet.createRandom().address;
                expect(await medicalRecordRegistry.checkAccess(recordHash, anotherDoctor)).to.be.false;
            });

            it("Should return false if access was granted then revoked", async function () {
                await medicalRecordRegistry.connect(ownerAddress).grantAccess(recordHash, doctorAddress.address);
                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.true; // Granted

                await medicalRecordRegistry.connect(ownerAddress).revokeAccess(recordHash, doctorAddress.address);
                expect(await medicalRecordRegistry.checkAccess(recordHash, doctorAddress.address)).to.be.false; // Revoked
            });

            it("Should return false for a non-existent record", async function () {
                const nonExistentRecordHash = ethers.encodeBytes32String("nonExistentForCheckAccess");
                expect(await medicalRecordRegistry.checkAccess(nonExistentRecordHash, doctorAddress.address)).to.be.false;
            });
        });
    });
});
