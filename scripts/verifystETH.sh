if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/stETH.sol:Lido  \
    --verify Lido:spec/erc20.spec $RULE  \
    --solc solc4.24 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "stETH:erc20.spec $1"