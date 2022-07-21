# ERC-20 Examples

In the table below we can see sample runs of the ERC20 spec on a few reasonably popular tokens. All of them (except sOHM)
have been recently proposed as an asset to be listed on Aave.

The idea is to look at the output from the Certora prover and see all the violations shown for a particular token.
As we discussed in the [main README](../README.md), with ERC20 tokens spec violations usually don't indicate bugs but
provide information about the non-trivial features of the token. 

In the examples below, the Certora prover tool does find a very minor bug on the GNO token (overflow that can't be exploited
in reality). For other tokens, the spec provides additional information about their code. It shows when tokens have changing
supply (can be minted/burned), when they're pausable by the admin and when they rebase.

| Token | Chain     | Forum Link                                                                                                                | Spec Run                                                                                                                           | Spec Violations                                                                                                                                     |
| ----- | --------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| CVX   | Ethereum  | [CVX proposal](https://governance.aave.com/t/arc-add-support-for-cvx-convex-finance-token/7319)                           | [CVX run](https://vaas-stg.certora.com/output/67509/e6f2daaea56b20e5b789/?anonymousKey=32c1ac33f0811df931d7b662d8a8f8afd9dcaa73)   | 1\. Token is mintable                                                                                                                               |
| FRAX  | Polygon   | [FRAX proposal](https://governance.aave.com/t/add-frax-as-asset-to-aave-v3-markets/7860)                                  | [FRAX run](https://vaas-stg.certora.com/output/67509/2ee27460cc038171efb5/?anonymousKey=b5858b1b0c879fa3332871e07b88c66ecd77702b)  | 1\. Token is mintable<br>2\. Token allowance change by signature is allowed<br>3\. Token has a burnFrom() feature - allowed spender may burn tokens |
| sAVAX | Avalanche | [sAVAX proposal](https://governance.aave.com/t/arc-add-support-for-savax-benqi-liquid-staking-avax-token-on-aave-v3/7892) | [sAVAX run](https://vaas-stg.certora.com/output/67509/2c9355896a35406f062e/?anonymousKey=62e852e8edadb178c14c75d96cefe4e0922cffa3) | 1\. Token is mintable<br>2\. Token is pausable (breaks transfers)<br>3\. Token contract holds a dynamic balance (breaks "OtherBalanceOnlyGoesUp")   |
| GNO   | Ethereum  | [GNO proposal](https://governance.aave.com/t/arc-add-gno-to-aave-v2/7966)                                                 | [GNO run](https://vaas-stg.certora.com/output/67509/fa7eb844230324eb5a29/?anonymousKey=f8e201b45742eaecc01a7544ec1e6ec64cd267ec)   | 1\. Addition to balance doesn't check for overflow<br>2\. Transfer to address 0 is allowed (breaks "zeroAddressNoBalance" invariant)                |
| sOHM  | Ethereum  | not a potential listing                                                                                                   | [sOHM run](https://vaas-stg.certora.com/output/67509/ab6d95c29de96d81fba9/?anonymousKey=bc1973e4bdb9255bf92d5a0a0e78bbb3cded4925)  | 1\. Token is rebasing<br>2\. Rebasing algo breaks multiple transfer rules. We'd need a custom spec to test the correctness of a rebasing token      |
| KNC   | Ethereum  | [KNC proposal](https://governance.aave.com/t/arc-add-new-knc-to-aave/8236)                                                | [KNC run](https://vaas-stg.certora.com/output/67509/a52c3356ecd40412b672/?anonymousKey=00d85632f4240a4d872453ce6f62afda6bff0995)   | 1\. Token is mintable<br>2\. Token has a burnFrom() feature - allowed spender may burn tokens                                                       |
| MAI   | Polygon   | [MAI proposal](https://governance.aave.com/t/add-mai-on-aave-v3/7630/24)                                                | [MAI run](https://prover.certora.com/output/67509/69e0516d38f1e2a98b1a/?anonymousKey=d1ecafe9ea2b57d2b1444ccc39d02e03d5e4929f)   | 1\. Token is mintable<br>2\. Token has a burn() function - admin may burn tokens of any address                                                     |
| StMATIC   | Polygon   | [StMATIC proposal](https://governance.aave.com/t/proposal-add-support-for-stmatic-lido/7677/19)                                                | [StMATIC run](https://prover.certora.com/output/67509/b3a3ca8ea836a40f42c2/?anonymousKey=5026ff1e21dfc50bf002306668e5caf27258a892)   | 1\. Token is mintable
| sUSD   | Optimism   | [sUSD proposal](https://governance.aave.com/t/arc-enable-susd-as-collateral-on-aave-v3-on-optimism/7912/10)                                                | [sUSD run](https://prover.certora.com/output/67509/a2a08fcb0d3a2e2bc8ec/?anonymousKey=c45d6312f9e8065ce2cf74c72c104e5f5a794618)   | 1\. Total supply can be modified by (Synthetix) system contracts<br>2\. Max allowance is never decreased on spending, non-standard behavior.<br>3\. User balance might decrease as a result of a call to burn() - which is callable by system contracts.<br>4\. Zero address might receive a balance as a result of issue() - callable by system contracts


## Next Tokens

- OP (Optimism)
