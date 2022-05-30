certoraRun demo/Rune.sol:ETH_RUNE  \
    --verify ETH_RUNE:spec/erc20.spec $RULE  \
    --solc solc8.0 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "ETH_RUNE:erc20.spec $1"