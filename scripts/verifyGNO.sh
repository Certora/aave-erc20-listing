if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/GNO.sol:GnosisToken  \
    --verify GnosisToken:spec/erc20.spec $RULE  \
    --solc solc4.24 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "GNO:erc20.spec $1"