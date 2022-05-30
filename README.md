# ERC20 Assets Verification

This repo includes formal verification specs for testing potential ERC20 assets for Aave listing.

Normally, in such a spec we would define how a system should work, then test a spec against the code and maybe
detect some errors. 

With ERC20 tokens there are not many general rules. Tokens have different properties. Some
have fixed supply, while others are mintable. Some major ERC20 tokens have a blacklist features(USDC, USDT), some
tokens have a potential transfer tax (USDT), some can be paused by an admin.

The specs contain rules to detect supply changes, pause on transfers and transfer tax, among others. Since these can be potential token features and not bugs, the counterexamples that the Certora prover finds when running this spec should be seen, first and foremost ,as information about the tested token, not as a violation or a bug. The idea is that testing the token code against the spec provides knowledge and richer details to the community, so that it can take a better decision re: listing the token.

For example, if we know that the tested token is mintable, it will obviously violate the noMintingTokens rule. Looking at the trace call will help us see that the "violation" (increasing total supply) happens in the mint() function - this is the token working as it should. On the other hand, if we see that the violation takes place in an approve() function, then this maybe a potential bug. The point is to understand each counterexample.

## Specs

- erc20.spec: generic token spec

- erc20mintable.spec: mintable token spec. Assumes that the token is mintable and tests if the mint() function is privileged.

## The rules

| Rule name                                  | Rule Description                                                                                                      | Category           | What breaks it                                                  |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ------------------ | --------------------------------------------------------------- |
| noFeeOnTransferFrom                        | Verifies that there is no tax on transferFrom()                                                                       | erc20.spec         | transfer tax                                                    |
| noFeeOnTransfer                            | Verifies that there is no tax on transfer()                                                                           | erc20.spec         | transfer tax                                                    |
| transferCorrect                            | Verifies correctness of transfer()                                                                                    | erc20.spec         | transfer tax, blacklist, pausability                            |
| transferFromCorrect                        | Verifies correctness of transferFrom()                                                                                | erc20.spec         | transfer tax, blacklist, pausability                            |
| transferFromReverts                        | Verifies correctness of transfer reverts                                                                              | erc20.spec         | pausability                                                     |
| ZeroAddressNoBalance                       | Verifies that zero address has no balance                                                                             | erc20.spec         | tokens that allow transfers to 0                                |
| NoChangeTotalSupply                        | Verifies that total supply doesn't change                                                                             | erc20.spec         | mintable tokens                                                 |
| noBurningTokens                            | Verifies that total supply doesn't go down                                                                            | erc20.spec         | mintable tokens                                                 |
| noMintingTokens                            | Verifies that total supply doesn't go up                                                                              | erc20.spec         | mintable tokens                                                 |
| Changing Allowance                         | Allowance changes correctly                                                                                           | erc20.spec         |                                                                 |
| TransferSumOfFromAndToBalancesStaySame     | Transfer from a to b doesn't change the sum of their balances                                                         | erc20.spec         | transfer tax                                                    |
| TransferFromSumOfFromAndToBalancesStaySame | transferFrom from a to b doesn't change the sum of their balances                                                     | erc20.spec         | transfer tax                                                    |
| TransferDoesntChangeOtherBalance           | Transfer from a to b doesn't change balance of c                                                                      | erc20.spec         | transfer tax sent to owner                                      |
| TransferFromDoesntChangeOtherBalance       | transferFrom from a to b doesn't change balance of c                                                                  | erc20.spec         | transfer tax sent to owner                                      |
| OtherBalanceOnlyGoesUp                     | Operations don't decrease balance of uninvolved addresses                                                             | erc20.spec         | USDC (signed message authorizes transfers), burnFrom() function |
| noRebasing                                 | Balance of an address doesn't change after an operation unless the operation is explicitly supposed to change balance | erc20.spec         | Rebasing token with rebase() function (OHM)                     |
| isMintPrivileged                           | Is only one address allowed to call mint()                                                                            | erc20Mintable.spec | tokens that give multiple addresses the MINTER\_ROLE            |


## Tokens

A few ERC20 tokens are included in the `contracts` directory. Some of them are are potential assets to be listed on Aave, like CVX.
Some are included only to demonstrate a particular rule, like sOHM.

Each token contract has a corresponding script for running the spec against it in the `scripts` directory.
