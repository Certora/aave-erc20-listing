if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/MAI.sol:QiStablecoin  \
    --verify QiStablecoin:spec/erc20mintable.spec $RULE  \
    --solc solc5.9 \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "MAI:erc20.spec $1"