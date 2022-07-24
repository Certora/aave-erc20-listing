if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/OP.sol:GovernanceToken  \
    --verify GovernanceToken:spec/erc20mintableOP.spec $RULE  \
    --solc solc8.0 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "Optimism:erc20mintableOP.spec $1"
