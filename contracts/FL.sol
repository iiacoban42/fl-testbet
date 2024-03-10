// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;


contract FL {
    string model;
    uint8 currentActor;
    uint8 currentRound;
    string[] weights;
    string[] aggregatedModel;
    uint8[] accuracies;
    uint8[] losses;
    uint8 numberOfRounds;

    constructor(string memory init_model, uint8 number_of_rounds) {
        numberOfRounds = number_of_rounds;
        currentActor = 0;
        currentRound = 0;
        model = init_model;
        currentActor = 1-currentActor;
    }

    function retrieveModel() public view returns (string memory) {
        return model;
    }

    function storeWeights(string memory _ipfsHash) public {
        require(currentActor == 1, "Weights can only be stored by the client");
        weights[currentRound] = _ipfsHash;
        currentActor = 1-currentActor;
    }

    function retrieveWeights(uint8 round) public view returns (string memory) {
        require(round < currentRound, "Round not yet completed");
        return weights[round];
    }

    function storeAggregatedModel(string memory _ipfsHash, uint8 accuracy, uint8 loss) public {
        require(currentActor == 0, "Aggregated model can only be stored by the server");
        aggregatedModel[currentRound] = _ipfsHash;
        accuracies[currentRound] = accuracy;
        losses[currentRound] = loss;
        currentRound++;
        currentActor = 1-currentActor;
    }

    function retrieveAggregatedModel(uint8 round) public view returns (string memory) {
        require(round < currentRound, "Round not yet completed");
        return aggregatedModel[round];
    }

}