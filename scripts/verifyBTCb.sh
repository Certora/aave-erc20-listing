if [[ "$1" ]]
then
    RULE="--rule $1"
fi


certoraRun contracts/BTCb.sol:BridgeToken  \
    --verify BridgeToken:spec/erc20mintableBTCB.spec $RULE  \
    --solc solc8.11 \
    --send_only \
    --optimistic_loop \
    --settings -enableEqualitySaturation=false,-solver=z3,-smt_usePz3=true,-smt_z3PreprocessorTimeout=2 \
    --solc_args '["--experimental-via-ir"]' \
    --msg "BTC.b:erc20mintable.spec $1"
