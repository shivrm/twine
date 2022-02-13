# Twine Docs

## What is Twine
Twine is a simple data serialization format that allows you to share data
across different systems.

Twine was developed with the purpose of being extensible and easy to implement.

## Usage
Twine is currently available in the following languages:
 - [Python](python.md)

## Structure
Data in twine files is stored in *data structures*. Data sturctures have different
types, such as `int`, `float`, and `str`.

Each data structure also has a *subtype*. This contains additional information like
the precision of a `float`, or the length of an `int` in bytes.

For a full reference of types and subtypes, please refer to the types [reference](types.md)

The handler of a type can also require some arguments. For example a `list` may require an argument specifying it's length

Here's how a `list` containing 13 elements might be encoded:

```
1--- 2--- 3------------------ 4---
          a--- b--- c--------
0101 0000 0010 0001 0000 1101 ....
```

Where:
1. `0101` indicates that it is a list
2. `0000` is the subtype for the list
3. `0010 0001 0000 1101` is the length argument for the list:
     - a. `0010` indicates that the argument is an int
     - b. `0001` is the subtype, and indicates an 8-bit unsigned integer
     - c. `0000 1101` contains the data of the int, and indicates the number 13
4. `....` the succeeding bytes contain the data of the list

