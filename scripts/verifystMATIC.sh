if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/StMATIC.sol:StMATIC  \
    --verify StMATIC:spec/erc20mintable.spec $RULE  \
    --solc solc8.7 \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "StMATIC:erc20mintable.spec $1"