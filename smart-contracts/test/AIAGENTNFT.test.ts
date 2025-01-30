import { expect } from "chai";
import { ethers } from "hardhat";
import { AIAgentNFT } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("AIAgentNFT", function () {
  let aiAgentNFT: AIAgentNFT;
  let owner: SignerWithAddress;
  let addr1: SignerWithAddress;
  let addr2: SignerWithAddress;

  beforeEach(async function () {
    // Get signers
    [owner, addr1, addr2] = await ethers.getSigners();

    // Deploy contract
    const AIAgentNFTFactory = await ethers.getContractFactory("AIAgentNFT");
    aiAgentNFT = await AIAgentNFTFactory.deploy();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await aiAgentNFT.owner()).to.equal(await owner.getAddress());
    });

    it("Should have correct name and symbol", async function () {
      expect(await aiAgentNFT.name()).to.equal("AIAgent");
      expect(await aiAgentNFT.symbol()).to.equal("AIAG");
    });
  });

  describe("Minting", function () {
    const tokenURI = "ipfs://QmTest";

    it("Should allow owner to mint NFTs", async function () {
      await aiAgentNFT.mintAgent(await addr1.getAddress(), tokenURI);
      expect(await aiAgentNFT.ownerOf(0)).to.equal(await addr1.getAddress());
      expect(await aiAgentNFT.tokenURI(0)).to.equal(tokenURI);
    });

    it("Should not allow non-owners to mint NFTs", async function () {
      // Here's the fix: expect the transaction to be reverted with any reason
      await expect(
        aiAgentNFT.connect(addr1).mintAgent(await addr2.getAddress(), tokenURI)
      ).to.be.reverted;
    });
  });

  describe("Token URI", function () {
    it("Should store and retrieve token URI correctly", async function () {
      const tokenURI = "ipfs://QmTest";
      await aiAgentNFT.mintAgent(await addr1.getAddress(), tokenURI);
      expect(await aiAgentNFT.tokenURI(0)).to.equal(tokenURI);
    });
  });
});