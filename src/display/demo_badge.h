#pragma once

// Marks every screen while demo mode is on (net/demo_mode.h): a thin
// coloured ring just inside the bezel and a "DEMO" tag at the top, both on
// lv_layer_top() so they sit over whichever screen is showing. A demo must
// never be mistaken for a live machine -- someone could walk up and expect
// the plotter to move.
//
// Neither takes input: touches pass straight through to the screen below.
namespace DemoBadge
{
    // Call every loop iteration; shows or hides the markers to match the
    // demo flag, and does nothing when it hasn't changed.
    void update();
}
