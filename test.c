#include <stdio.h>

int var4;

namespace outerNamespace {
    int var1 = 10;
    int var2 = 20;

    namespace innerNamespace {
        void function1() {
            int var1 = 30;  // Local variable with the same name as in outerNamespace
            outerNamespace::var1 = 40; // Accessing outerNamespace var1
        }

        int var3 = 40;
    }

    void testFunction() {
        innerNamespace::function1();
        var4 = var2;  // Accessing var2 from outerNamespace
        int var5 = innerNamespace::var3; // Accessing var3 from innerNamespace
    }

    namespace veryInnerNamespace {
        int var6 = 50;

        void function2() {
            int var7 = outerNamespace::var2; // Accessing var2 from outerNamespace
        }
    }
}

namespace adjacentNamespace {
    int var1 = 60;

    void function3() {
        int var9 = outerNamespace::var1; // Accessing var1 from outerNamespace
        outerNamespace::testFunction(); // Accessing function from outerNamespace
    }
}

int main() {
    outerNamespace::testFunction();
    adjacentNamespace::function3();
    return 0;
}