# Background: GLIBC_TUNABLES and Heap Overflows

## What GLIBC_TUNABLES Does

`GLIBC_TUNABLES` is an environment variable introduced in glibc 2.25. It controls
internal glibc parameters, particularly the memory allocator. You can set it to values
like `glibc.malloc.mxfast=128` to change the threshold for fast-path allocations.
The dynamic loader (`ld.so`) reads and parses this variable before any application code
runs, including before `main()` is called.

## The Buffer Overflow

The vulnerable parsing routine in `ld.so` copies the tunable string into a 256-byte
heap buffer. It does not check the length of the string before copying. If the input
exceeds 256 bytes, the copy writes past the end of the buffer into adjacent heap memory.

Heap overflows can be used to overwrite heap metadata, function pointers stored on the
heap, or the contents of adjacent allocations. In glibc's allocator, corrupting the
`fd` and `bk` pointers of a free chunk can redirect pointer writes during the next
`free()` or `malloc()` call, enabling arbitrary writes to memory.

The specific key `glibc.malloc.mxfast=` is the first key the parser encounters in
`GLIBC_TUNABLES`, which means the overflow happens immediately, in a predictable heap
state, making it reliably exploitable.

## Why SUID Matters

The `GLIBC_TUNABLES` variable is stripped for SUID binaries in patched versions. In
the vulnerable versions, `ld.so` reads and processes the variable even when launching
a SUID binary. This means an unprivileged user can set a malicious `GLIBC_TUNABLES`
value and then execute any SUID binary to trigger the overflow in a privileged context.
