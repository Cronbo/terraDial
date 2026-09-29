#pragma once

#include <stdint.h>
#include "../input/encoder.h"

// Hands-off demo for a trade show stand: while demo mode is on
// (net/demo_mode.h) and nobody has touched the panel for TOUR_IDLE_MS, it
// plays a scripted tour of every screen -- and stops the instant a real
// hand touches the glass or the knob, so visitors can take over. Walk away
// and it starts again.
//
// The tour drives the UI the way a person would: its knob turns and clicks
// go through UiNav exactly like the real knob's, so the dial spins, screens
// open, jobs run and alarms raise just as they would by hand. Nothing about
// the screens themselves knows it's running.
namespace DemoTour
{
    // Any real input -- knob or touch. Restarts the idle clock, and stops a
    // running tour.
    void noteRealInput();

    // Call every loop iteration: starts the tour once the panel has been
    // left alone, and steps through the script while it runs.
    void update();

    bool isRunning();

    // Called by UiNav when the real knob had nothing to report: hands over
    // the tour's next scripted turn or click, if one is due. Leaves the
    // arguments alone otherwise.
    void takeInput(int32_t &delta, ButtonEvent &ev);
}
