// Buggy C++ code with syntax errors
#include <iostream>
using namespace std;

int main() {
    int x = 5
    cout << "Value: " << x << endl  // Missing semicolon
    
    if (x == 5)  // Missing opening brace
        cout << "x is 5" << endl;
        cout << "Still in if" << endl;  // Wrong indentation
    }  // Extra brace
    
    return 0
}
