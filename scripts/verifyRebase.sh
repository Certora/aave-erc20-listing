certoraRun contracts/stETH.sol:Lido  \
    --verify Lido:spec/erc20rebase.spec  \
    --solc solc4.24 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "Lido:erc20rebase.spec $1"