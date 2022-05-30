# Files

`ERC20_OZ` - standard OpenZeppelin ERC20 implementation

`Honeypot.sol` - Honeypot ERC20 token - you can only buy it, but not sell (only whitelisted addresses may transfer)

`Rune.sol` - RUNE token code. transferTo() famously uses tx.origin instead of msg.sender. OtherBalanceOnlyGoesUp() detects the bug.

`ICX.sol` - ICX token code. bug in modifier lets anyone call pause()