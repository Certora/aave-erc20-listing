certoraRun demo/Honeypot.sol:ERC20  \
    --verify ERC20:spec/erc20mintable.spec $RULE  \
    --solc solc8.0 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "Honeypot:erc20.spec $1"