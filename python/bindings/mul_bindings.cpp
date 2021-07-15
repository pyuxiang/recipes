#include <pybind11/pybind11.h>
#include "mul.cpp"
#include <iostream>
using namespace std;

// int main() {
//     cout << cmult(1, 3) << '\n';
//     return 0;
// }
//

PYBIND11_MODULE(mullib, m) {
    m.doc() = "pybind11 example plugin";
    m.def("add", cmult, "A function multiplying two numbers");
}
