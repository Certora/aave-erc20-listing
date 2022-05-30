if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/CVX.sol:ConvexToken  \
    --verify ConvexToken:spec/erc20mintable.spec $RULE  \
    --solc solc6.12 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "CVX:erc20mintable.spec $1"