# Python Field Kit — Essential Syntax for Cybersecurity Analysts

A practical Python reference for reading code, tracing logic, and working with data
during investigation and analysis tasks. No external dependencies required.

---

## Variables & Data Types

```python
x = 42           # int
y = 3.14         # float
s = "hello"      # str
b = True         # bool
lst = [1, 2, 3]  # list
d = {"a": 1}     # dict
```

Check the type of any value:

```python
type(x)          # <class 'int'>
type(s)          # <class 'str'>
```

---

## String Operations

```python
s = "Grid Operator"

s.upper()             # "GRID OPERATOR"
s.lower()             # "grid operator"
s.strip()             # remove leading/trailing whitespace
s.split(" ")          # ["Grid", "Operator"]
" ".join(["a", "b"])  # "a b"
s[0:4]                # "Grid"  — slice
s[::-1]               # reverse string
s.replace("Grid", "X") # "X Operator"
len(s)                # 13
s.startswith("Grid")  # True
s.find("Op")          # 5  — index of substring
```

---

## Character ↔ Integer Conversion

```python
ord("A")    # 65  — character to ASCII code
chr(65)     # "A" — ASCII code to character
hex(65)     # "0x41"
int("0x41", 16)  # 65 — hex string to int
```

Useful for tracing scripts that process character codes:

```python
codes = [72, 101, 108, 108, 111]
result = "".join([chr(c) for c in codes])
# → "Hello"
```

---

## Lists

```python
lst = [10, 20, 30]

lst[0]           # 10  — first element
lst[-1]          # 30  — last element
lst[1:3]         # [20, 30]  — slice
lst.append(40)   # add to end
lst.index(20)    # 1  — position of value
len(lst)         # 3
sorted(lst)      # sorted copy (ascending)
lst.reverse()    # reverse in place
```

List comprehension — compact loop:

```python
doubled = [x * 2 for x in lst]
chars = [chr(c) for c in codes]
```

---

## Loops

```python
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for item in lst:
    print(item)

for i, item in enumerate(lst):  # index + value
    print(i, item)
```

---

## Conditionals

```python
if x > 10:
    print("large")
elif x == 10:
    print("exact")
else:
    print("small")
```

---

## Functions

```python
def process(data):
    return data.strip().lower()

result = process("  ADMIN  ")   # "admin"
```

---

## File I/O

```python
# Read entire file
with open("log.txt", "r") as f:
    content = f.read()

# Read line by line
with open("log.txt", "r") as f:
    for line in f:
        print(line.strip())

# Write to file
with open("output.txt", "w") as f:
    f.write("data\n")
```

---

## Encoding & Decoding

```python
import base64

# Encode
base64.b64encode(b"hello")          # b'aGVsbG8='

# Decode
base64.b64decode(b"aGVsbG8=")       # b'hello'
base64.b64decode(b"aGVsbG8=").decode("utf-8")  # "hello"
```

Hex:

```python
"hello".encode().hex()              # "68656c6c6f"
bytes.fromhex("68656c6c6f")         # b'hello'
bytes.fromhex("68656c6c6f").decode()# "hello"
```

---

## Useful Built-ins

```python
len(x)         # length of string, list, dict
range(0, 10)   # integer sequence 0–9
print(x)       # output to terminal
input(">> ")   # read user input
int(), str(), float(), bool()   # type conversion
dir(x)         # list methods available on object
help(str)      # show documentation
```

---

## Quick Reference — Common Patterns

| Task | One-liner |
|------|-----------|
| Reverse a string | `s[::-1]` |
| Join list to string | `"".join(lst)` |
| Split string to list | `s.split(",")` |
| Chars from int list | `"".join([chr(c) for c in codes])` |
| Read file lines | `open("f").readlines()` |
| Base64 decode | `base64.b64decode(s).decode()` |
| Hex to string | `bytes.fromhex(h).decode()` |
| Get char code | `ord(s[0])` |

---

*Part of the Cyberium Hack the Grid — Python Fundamentals module*
*CyberSentinel-sys · 2026*
