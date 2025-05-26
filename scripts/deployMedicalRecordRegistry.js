const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying MedicalRecordRegistry contract with the account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  const MedicalRecordRegistryFactory = await hre.ethers.getContractFactory("MedicalRecordRegistry");
  const medicalRecordRegistryContract = await MedicalRecordRegistryFactory.deploy();

  await medicalRecordRegistryContract.waitForDeployment();
  const contractAddress = await medicalRecordRegistryContract.getAddress();

  console.log("MedicalRecordRegistry contract deployed to:", contractAddress);

  // Save deployment info
  saveDeploymentInfo(medicalRecordRegistryContract, "MedicalRecordRegistry");
}

function saveDeploymentInfo(contract, contractName) {
  const contractAddress = contract.target; // For ethers v6, target is the address
  const contractArtifact = hre.artifacts.readArtifactSync(contractName);

  const deploymentInfoDir = path.join(__dirname, "..", "blockchain", "build", "deployments");
  if (!fs.existsSync(deploymentInfoDir)) {
    fs.mkdirSync(deploymentInfoDir, { recursive: true });
  }

  // Save contract address
  fs.writeFileSync(
    path.join(deploymentInfoDir, `${contractName}-address.json`),
    JSON.stringify({ address: contractAddress }, undefined, 2)
  );

  // Save ABI
  fs.writeFileSync(
    path.join(deploymentInfoDir, `${contractName}-abi.json`),
    JSON.stringify(contractArtifact.abi, undefined, 2)
  );

  console.log(`Deployment info for ${contractName} saved to ${deploymentInfoDir}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error deploying MedicalRecordRegistry contract:", error);
    process.exit(1);
  });
