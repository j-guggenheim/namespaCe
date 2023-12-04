#include <stdio.h>

int var4;

namespace outerNamespace {
    int var1 = 10;
    int var2 = 20;

    namespace innerNamespace {
        void function1() {
            var1 = 30;  // This var1 should belong to outerNamespace
        }
        int var2 = 5;
        int var3 = 40;
    }

    void testFunction() {
        innerNamespace::function1();
        int var4 = var2;  // This var2 should belong to outerNamespace
    }
}

int main() {
    outerNamespace::testFunction();
    return 0;
}