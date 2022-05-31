pragma solidity >=0.8.0;

// SPDX-License-Identifier: UNLICENSED

import "@openzeppelin/contracts/access/Ownable.sol";


interface IWETH {
    function transferFrom(address src, address dst, uint wad) external returns (bool);
}

contract Pledge is Ownable {
    string public name = "Plegde v1";

    address public weth_address;

    uint public pledge_fee = 0.010 ether;
    uint public min_pledge = 0.001 ether;

    uint public payout_embargo = 30 days;

    mapping(address => bool) public is_approved_beneficiary;
    mapping(address => mapping(address => uint)) public pledged_amount;
    mapping(address => mapping(address => uint)) public last_payout_timestamp;

    constructor(address _weth_address) {
        // e.g. 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
        weth_address = _weth_address;
    }

    receive() external payable {
        // Thank you
    }

    function configure_pledge(uint _pledge_fee, uint _min_pledge) public onlyOwner {
        pledge_fee = _pledge_fee;
        min_pledge = _min_pledge;
    }

    function pledge(address beneficiary, uint amount) public payable {
        require(is_approved_beneficiary[beneficiary]);
        require(amount >= min_pledge);

        require(msg.value >= pledge_fee);

        pledged_amount[msg.sender][beneficiary] = amount;
    }

    function pay(address from, address to, uint amount) public onlyOwner {
        require(is_approved_beneficiary[to]);  // @dev: The beneficiary has to be approved first.
        require(last_payout_timestamp[from][to] + payout_embargo < block.timestamp);  // @dev: Payout is too soon.
        require(amount <= pledged_amount[from][to]);  // @dev: Amount to pay may not exceed the pledged amount.

        IWETH(weth_address).transferFrom(from, to, amount);

        last_payout_timestamp[from][to] = block.timestamp;
    }

    function _withdraw(address payable to, uint amount) public onlyOwner {
        to.transfer(amount);
    }

    function _approve_beneficiary(address beneficiary, bool is_approved) public onlyOwner {
        is_approved_beneficiary[beneficiary] = is_approved;
    }
}
