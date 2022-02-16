# twine

`twine` is a simple data serialization format that allows you to share data across different systems.

Click [here](https://shivrm.github.io/twine/docs) for documentation

# Why twine?

In many cases such as storing large arrays, singleton values, etc. twine takes less space than other serialization formats like *JSON* and *pickle*.

Here's how many bytes each format takes to encode some data:

|                    | JSON   | pickle   | twine      |
| ------------------ | ------ | -------- | ---------- |
| `None`             | _4_    | _4_      | **1**      |
| `False`            | 5      | _4_      | **1**      |
| `1`                | _1_    | 5        | _2_        |
| `2 ** 128 - 1`     | 39     | _31_     | **17**     |
| `-(2 ** 127)`      | 40     | _30_     | **17**     |
| `1.0`              | _3_    | 21       | _5_        |
| `0.1`              | _3_    | 21       | _5_        |
| `1 + 10e-15`       | _16_   | 21       | **9**      |
| `+Infinity`        | _8_    | 21       | **1**      |
| `[]`               | _2_    | 5        | _3_        |
| `range(100)`       | 390    | _216_    | **203**    |
| `range(2**16 - 1)` | 447635 | _196513_ | **196353** |
| `""`               | _2_    | 15       | _3_        |
| `"Hello, World!"`  | _15_   | 28       | _16_       |
| `"\uffff" * 1000`  | 6002   | _3018_   | **3004**   |

twine consumes less space than both JSON and pickle in most of the test cases. However, when the data is short, twine may require more space than JSON.

# Why not twine?

 - twine is relatively new and not available in most languages
 - twine is a solo-project
 - twine is still in development

# Contributing

twine is still a relatively new project, and does not yet have any contributing
guidelines. If you want to report a bug or suggest a feature, feel free to
[create an issue](https://github.com/shivrm/twine/issues/new).

# License

twine is licensed under the MIT License.