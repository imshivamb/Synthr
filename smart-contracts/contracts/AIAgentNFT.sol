pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AIAgentNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;
    uint256 public royaltyPercentage = 1000; // 10% as base royalty

    // Custom errors
    error InvalidRoyaltyPercentage();
    error InvalidTokenId();

    constructor() ERC721("AIAgent", "AIAG") Ownable(msg.sender) {}

    function mintAgent(address to, string memory uri) public onlyOwner returns (uint256) {
        require(to != address(0), "Invalid recipient address");
        require(bytes(uri).length > 0, "URI cannot be empty");
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        return tokenId;
    }

    function setRoyaltyPercentage(uint256 newPercentage) public onlyOwner {
        if (newPercentage > 10000) revert InvalidRoyaltyPercentage();
        royaltyPercentage = newPercentage;
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}