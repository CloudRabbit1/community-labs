# Background

## AES block structure

AES processes data in 16-byte blocks. When you encrypt 48 bytes, AES sees three separate 16-byte inputs and produces three separate 16-byte outputs. Each output depends only on its input block and the key.

## ECB mode

In Electronic Codebook (ECB) mode, every block is encrypted independently:

```
Plaintext:   [ Block 0        ][ Block 1        ][ Block 2        ]
                     |                 |                 |
              AES(key, B0)     AES(key, B1)     AES(key, B2)
                     |                 |                 |
Ciphertext:  [ CT Block 0     ][ CT Block 1     ][ CT Block 2     ]
```

The same plaintext block always produces the same ciphertext block when the key is fixed. That is the property the attack exploits.

## PKCS7 padding

AES requires the input to be a multiple of 16 bytes. PKCS7 padding adds `n` bytes of value `n` to reach the next multiple:

- 15 bytes of plaintext: add 1 byte of value `0x01`
- 14 bytes of plaintext: add 2 bytes of value `0x02`
- 16 bytes of plaintext: add 16 bytes of value `0x10` (a full padding block)

## The oracle model

The oracle accepts your input `I` and returns `encrypt(I + secret)`. You cannot observe the secret directly. But ECB's block independence means:

If you send 15 bytes, the first block is `I[0:15] + secret[0]`. You know 15 of the 16 bytes. To find the unknown one, try all 256 possibilities: send exactly 16 bytes `I[0:15] + guess` and compare the first output block. When the blocks match, you found `secret[0]`.

Repeat for `secret[1]` by sending 14 bytes: first block is now `I[0:14] + secret[0] + secret[1]`. You already know `secret[0]`, so try all 256 values of `secret[1]`.

Continue until all bytes of the secret are recovered.

## Why CBC mode prevents this

In Cipher Block Chaining (CBC) mode, each plaintext block is XORed with the previous ciphertext block before encryption:

```
CT[i] = AES(key, PT[i] XOR CT[i-1])
```

The same plaintext block produces different ciphertext depending on what came before it. The comparison trick does not work. CBC mode does not share ECB's vulnerability to this attack.
