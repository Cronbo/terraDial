#pragma once

#include <Arduino.h>

// FluidNC's SD-card gcode file list, fetched over HTTP (GET /upload?path=/,
// the endpoint FluidNC's own WebUI and terraForge use) and parsed here.
//
// It used to be requested over the WebSocket with `$SD/ListJSON=/`, which
// streams the JSON back as dozens of small frames. FluidNC v4.0.3 reboots
// partway through that stream -- the listing stopped mid-file, the socket
// and the WebUI dropped together, and the controller came back with its
// boot banner and a config error until power-cycled. The HTTP endpoint
// returns the same JSON as one response and doesn't touch that path.
struct FluidNCFileEntry
{
    char name[48] = {0};
    int32_t size = -1;
};

class SdFileList
{
public:
    static const int MAX_FILES = 40;

    // Marks a listing as requested. Caller (FluidNCClient) fetches it on
    // the network task and hands the result to setResponse()/fail().
    void beginCapture();

    bool isCapturing() const { return capturing_; }

    // The HTTP body of GET /upload?path=/. Parses it and marks the list
    // ready.
    void setResponse(const String &body);

    // The fetch failed: finish with an empty list, so the Jobs screen
    // stops waiting rather than spinning forever.
    void fail();

    bool ready() const { return ready_; }
    void clearReady() { ready_ = false; }
    int count() const { return count_; }
    const FluidNCFileEntry &entry(int i) const { return files_[i]; }

private:
    bool capturing_ = false;
    bool ready_ = false;
    FluidNCFileEntry files_[MAX_FILES];
    int count_ = 0;

    void parseJson(const String &body);
};
