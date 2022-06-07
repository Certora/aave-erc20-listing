certoraRun demo/ICX.sol:IcxToken  \
    --verify IcxToken:spec/erc20lockable.spec $RULE  \
    --solc solc8.0 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "IcxToken:erc20lockable.spec $1"