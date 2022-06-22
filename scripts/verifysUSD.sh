if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/sUSD_target_harness.sol:MultiCollateralSynth \
    --verify MultiCollateralSynth:spec/erc20.spec $RULE  \
    --solc solc5.16 \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "sUSD_target_harness:erc20.spec $1"