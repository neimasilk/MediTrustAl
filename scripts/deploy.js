const fs = require('fs');
const path = require('path');

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  // Deploy UserRegistry
  console.log("\n--- Deploying UserRegistry ---");
  const UserRegistryFactory = await hre.ethers.getContractFactory("UserRegistry");
  const userRegistryContract = await UserRegistryFactory.deploy();
  await userRegistryContract.waitForDeployment();
  const userRegistryAddress = await userRegistryContract.getAddress();
  console.log("UserRegistry contract deployed to:", userRegistryAddress);
  
  // Save UserRegistry deployment info
  saveDeploymentInfo(userRegistryContract, "UserRegistry");

  // Deploy MedicalRecordRegistry
  console.log("\n--- Deploying MedicalRecordRegistry ---");
  const MedicalRecordRegistryFactory = await hre.ethers.getContractFactory("MedicalRecordRegistry");
  const medicalRecordRegistryContract = await MedicalRecordRegistryFactory.deploy();
  await medicalRecordRegistryContract.waitForDeployment();
  const medicalRecordRegistryAddress = await medicalRecordRegistryContract.getAddress();
  console.log("MedicalRecordRegistry contract deployed to:", medicalRecordRegistryAddress);
  
  // Save MedicalRecordRegistry deployment info
  saveDeploymentInfo(medicalRecordRegistryContract, "MedicalRecordRegistry");

  console.log("\n--- Deployment Summary ---");
  console.log("UserRegistry:", userRegistryAddress);
  console.log("MedicalRecordRegistry:", medicalRecordRegistryAddress);
}

function saveDeploymentInfo(contract, contractName) {
  const contractAddress = contract.target;
  const contractArtifact = hre.artifacts.readArtifactSync(contractName);

  const deploymentInfoDir = path.join(__dirname, "..", "blockchain", "build", "deployments");
  if (!fs.existsSync(deploymentInfoDir)) {
    fs.mkdirSync(deploymentInfoDir, { recursive: true });
  }

  const deploymentInfo = {
    contractName: contractName,
    contractAddress: contractAddress,
    abi: contractArtifact.abi,
    bytecode: contractArtifact.bytecode,
    deployedBytecode: contractArtifact.deployedBytecode,
    deploymentTimestamp: new Date().toISOString(),
    network: hre.network.name
  };

  const deploymentInfoPath = path.join(deploymentInfoDir, `${contractName}.json`);
  fs.writeFileSync(deploymentInfoPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`${contractName} deployment info saved to:`, deploymentInfoPath);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });