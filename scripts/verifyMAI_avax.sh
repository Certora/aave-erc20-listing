if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/MAI_avax.sol:crosschainMai  \
    --verify crosschainMai:spec/erc20mintable.spec $RULE  \
    --solc solc5.17 \
    --send_only \
    --staging \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "MAI_avax:erc20mintable.spec $1"