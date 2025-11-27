// Multi-error C++ code for testing
#include <iostream>
using namespace std;

int calculateSum(int a, int b) {
    int result = a + b;
    return result;
}

int main() {
    int x = 10;
    int y = 20;
    
    int sum = calculateSum(x, y);
    cout << "Sum: " << sum << endl;
    
    return 0;
}
