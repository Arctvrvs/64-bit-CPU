# rsb32 Module

`rsb32.sv` implements a simple return stack buffer used by the branch
prediction logic to predict addresses for `RET` instructions. It stores
up to 32 return addresses and provides push and pop operations.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `push_i` | in | 1 | Push the provided return address |
| `push_addr_i` | in | 64 | Address to push |
| `pop_i` | in | 1 | Pop the top entry |
| `top_o` | out | 64 | Address from top of stack |

## Behavior

On a push the address is written to the current stack pointer and the
pointer increments modulo the depth. A pop decrements the pointer and
outputs the address from the new top entry. Wrap-around effectively
creates a circular buffer suitable for storing nested return addresses.
