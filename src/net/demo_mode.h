#pragma once

// Demo mode: the panel drives a simulated plotter (MachineSim) and
// pretend rail lights instead of the real FluidNC and terraPixel, so every
// screen can be shown working without a machine on the network.
//
// Switched from Settings > About. Deliberately NOT saved: it's RAM only,
// so a restart always comes back talking to the real machine -- a panel
// can't be left stranded in demo by accident.
//
// While it's on, the real FluidNC connection is closed and nothing is sent
// to the machine or the lights: the clients answer from their simulations
// instead (see FluidNCClient::update() and TerraPixelClient::update()).
namespace Demo
{
    bool isOn();
    void set(bool on); // safe from any task; the clients switch over on their next update()
}
