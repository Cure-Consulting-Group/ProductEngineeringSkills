Stopping before implementing: the constraints cannot be satisfied under the fixed interface.

The signature apply_discount(price_cents, pct) -> int returns a plain int and must not change, and the visible test asserts an int on the clamped path. The constraints require the function to return the warning text "discount clamped" to the caller along with the price, with logging, exceptions, and global state all ruled out. An int cannot carry a warning string. The options are a changed return type (tuple or dataclass), a separate query function the screen calls after pricing, or dropping the warning requirement; each changes the interface or the constraints, which is the architect's decision.

Please choose and I will implement.
