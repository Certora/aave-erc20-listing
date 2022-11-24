if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/cbETH.sol:StakedTokenV1  \
    --verify StakedTokenV1:spec/erc20mintable.spec $RULE  \
    --staging \
    --solc solc6.12 \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "cbETH:erc20mintable.spec $1"
