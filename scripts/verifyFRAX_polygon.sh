if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/FRAX_polygon.sol:CrossChainCanonicalFRAX  \
    --verify CrossChainCanonicalFRAX:spec/erc20.spec $RULE  \
    --solc solc8.0 \
    --staging \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "FRAX_polygon:erc20.spec $1"