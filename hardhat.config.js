require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24", // Specified version
  paths: {
    sources: "./blockchain/contracts", // Correct path to contracts
    tests: "./blockchain/test",       // Correct path to tests
    cache: "./blockchain/cache",      // Correct path for cache
    artifacts: "./blockchain/artifacts" // Correct path for artifacts
  },
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {},
    ganache: {
      url: "http://127.0.0.1:7545", // Standard Ganache URL
      // chainId: 1337 // Default Ganache chainId, often not needed if Ganache is standard
      // accounts: { mnemonic: "YOUR_GANACHE_MNEMONIC_HERE" } // Optional: if you want to use specific accounts
    }
  }
};
