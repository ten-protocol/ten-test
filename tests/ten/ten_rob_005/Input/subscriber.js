const { ethers } = require("ethers");

// Replace with your actual provider URL
const providerUrl = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID";
const provider = new ethers.JsonRpcProvider(providerUrl);

// Replace with your contract address
const contractAddress = "YOUR_CONTRACT_ADDRESS";

// Replace with your contract ABI
const contractABI = [
    // Event ABIs
    "event SimpleEvent(uint indexed id, string message, address sender)",
    "event ArrayEvent(uint indexed id, uint[] numbers, string[] messages)",
    "event StructEvent(uint indexed id, tuple(uint id, string name, address userAddress) user)",
];

const contract = new ethers.Contract(contractAddress, contractABI, provider);

// Function to listen to SimpleEvent with filtering
async function listenToFilteredSimpleEvent(idFilter, senderFilter) {
    const filter = contract.filters.SimpleEvent(idFilter, null, senderFilter);

    contract.on(filter, (id, message, sender) => {
        console.log(`Filtered SimpleEvent - ID: ${id}, Message: ${message}, Sender: ${sender}`);
    });
}

// Function to listen to ArrayEvent with filtering
async function listenToFilteredArrayEvent(idFilter) {
    const filter = contract.filters.ArrayEvent(idFilter);

    contract.on(filter, (id, numbers, messages) => {
        console.log(`Filtered ArrayEvent - ID: ${id}, Numbers: ${numbers}, Messages: ${messages}`);
    });
}

// Function to listen to StructEvent with filtering
async function listenToFilteredStructEvent(idFilter, userAddressFilter) {
    const filter = contract.filters.StructEvent(idFilter, null);

    contract.on(filter, (id, user) => {
        if (user.userAddress === userAddressFilter) {
            console.log(`Filtered StructEvent - ID: ${id}, User: ${JSON.stringify(user)}`);
        }
    });
}

// Example usage
(async () => {
    // Replace these with your desired filter values
    const idFilter = 1; // Set to `null` if no filtering on this parameter
    const senderFilter = "0x1234..."; // Set to `null` if no filtering on this parameter
    const userAddressFilter = "0xABCD..."; // Set to the user address you want to filter on

    // Start listening with filters
    listenToFilteredSimpleEvent(idFilter, senderFilter);
    listenToFilteredArrayEvent(idFilter);
    listenToFilteredStructEvent(idFilter, userAddressFilter);

    console.log("Listening for filtered events...");
})();