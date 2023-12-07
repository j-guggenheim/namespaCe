#include <stdio.h>

int foo()
{
    return 1;
}




namespace te_st{

extern
  __attribute__((__format__ (gnu_printf, 1, 2))) __attribute__ ((__nonnull__ (1)))
  int __attribute__((__cdecl__)) attributeFuncNameLol(const char * __restrict__ , ... ) __attribute__ ((__nothrow__));

enum test{gg, hh, ii} enumFunc(void)
{
    return gg;
}


long unsigned a;

int unsigned b;

static const volatile int x, y, z;
char c = 'a';

float flote;
double dubs;

uint8_t intTypes;

enum tEnum{ g }tEnumInstance;
union tUnionnn{int k; char l;} tUnionnnFunc(int)
{
    return {3};
}

int (*funcPtr)(int, int), (*funcPtr2)();

int (*(*(*(*foo5(void))(void))(void))(void))(int i);

void (* ( *get ( int) ) (int) ) (int, int)
{
    return nullptr;
}

int (test) = (3);

int * a;
int j;

static int z = (int)3, b=2;

static int c = 3 + 5;

typedef int newNameForInt;

int $;

unsigned retUnsigned(int a, float b){
    return (unsigned) a;
}

unsigned long retLongUnsigned(int a, float b)
{
    return b;
}

int (foo)()
{
    return 2;
}

int bar (){return b;} int bar2(void){return c;}

typedef struct tStruct {
    int i;
    int j;

    struct inner {
        int k;
        int l;
    } inst, inst2;
    
    union innerUnion{
        int z;
    };

    enum innerEnum{
        ggg = 566,
    } innerEnumInstance;
    
} tStructdef[5];

typedef struct tstruct tStructDef2;

struct tStruct e[];

typedef int * koo(long);

koo loo;

tStructdef f;

struct newStruct{int k;} retStructure(int), newStructInstance, newStructInstanceReturn(void);

struct retStruct{ int retStructVal; } foooo(void) {
    return {2};}

unsigned int tempVar = 5;
int barR()
{
    int tempVar;

    return tempVar;
}

union test3
{
    struct inner2 {
        struct inner8{
            int help;
        };
        int k;
        int l;
    };
    int k;
    int d;
    char f;
    char lmfad[10];
};

unsigned int integerVal(void), kVal = 9, (*gVal(void))[3];



namespace testInnerNs{
    int Arg;
}

}

struct t2Struct{
    struct innards{
        int k;
        int l;
    };
};

int main(void)
{
    std::cout << te_$st::b;
    std::cout << te_$st::z;
    te_$st::get(1);
    te_$st::tEnum t = te_$st::g;
    struct te_$st::tStruct abcdefg;
}