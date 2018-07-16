# POC Phase 0: Simple calculator
Simple calculator with different relationships between its functions

The invocation matrix between functions is in invokers and invoked. The numbers in it are the number of times that function is invoked.

Calculator v1: Simple calculator. The invocation matrix is like

|               | add           | sub    | main   |
| ------------- |:-------------:| ------:|-------:|
| add           | 0             | 0      | 1      |
| sub           | 0             | 0      | 1      |
| main          | 0             | 0      | 0      |

Calculator v2: Added mult

|               | add           | sub   | mult | main   |
| ------------- |:-------------:| -----:|-----:|-------:|
| add           | 0             | 0     | 0    | 4      |
| sub           | 0             | 0     | 0    | 3      |
| mult          | 0             | 0     | 0    | 2      |
| main          | 0             | 0     | 0    | 0      |

Calculator v3: Mult invokes sum

|               | add           | sub   | mult | main   |
| ------------- |:-------------:| -----:|-----:|-------:|
| add           | 0             | 0     | N    | 1      |
| sub           | 0             | 0     | 0    | 1      |
| mult          | 0             | 0     | 0    | 1      |
| main          | 0             | 0     | 0    | 0      |


Calculator v4: Recursive factorial, invokes mult

|               | add           | sub   | mult | fact   | main   |
| ------------- |:-------------:| -----:|-----:|-------:|-------:|
| add           | 0             | 0     | N    | 0      | 1      |
| sub           | 0             | 0     | 0    | 0      | 1      |
| mult          | 0             | 0     | 0    | N      | 1      |
| fact          | 0             | 0     | 0    | N      | 1      |
| main          | 0             | 0     | 0    | 0      | 0      |
