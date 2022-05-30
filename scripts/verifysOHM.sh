if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/sOHM.sol:sOlympus  \
    --verify sOlympus:spec/erc20.spec $RULE  \
    --solc solc7.5 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "sOHM:erc20rebase.spec $1"