#include "demo_mode.h"

namespace
{
    volatile bool demoOn = false;
}

namespace Demo
{
    bool isOn() { return demoOn; }
    void set(bool on) { demoOn = on; }
}
