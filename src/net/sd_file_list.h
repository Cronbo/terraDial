#pragma once

#include <Arduino.h>

// FluidNC's SD-card file list for one folder, fetched over HTTP
// (GET /upload?path=<folder>, the endpoint FluidNC's own WebUI and
// terraForge use) and parsed here.
//
// It used to be requested over the WebSocket with `$SD/ListJSON=/`, which
// streams the JSON back as dozens of small frames. FluidNC v4.0.3 reboots
// partway through that stream -- the listing stopped mid-file, the socket
// and the WebUI dropped together, and the controller came back with its
// boot banner and a config error until power-cycled. The HTTP endpoint
// returns the same JSON as one response and doesn't touch that path.
//
// No cap on the number of entries: they live in PSRAM (the board has 8MB),
// and the Jobs ring only ever creates chips for the handful on screen, so
// the list can be as long as the folder is.

// FAT's long-filename limit.
static const size_t SD_NAME_MAX = 255;
// A folder path, relative to the SD root, without leading or trailing
// slashes ("" is the root). Deeper than FluidNC can run a file from (see
// FluidNCClient::runPathFits), but browsing it is harmless.
static const size_t SD_DIR_MAX = 512;

struct FluidNCFileEntry
{
    char name[SD_NAME_MAX + 1] = {0};
    int32_t size = -1;
    bool isDir = false;
};

class SdFileList
{
public:
    // Marks a listing as requested. Caller (FluidNCClient) fetches it on
    // the network task and hands the result to setResponse()/fail().
    void beginCapture();

    bool isCapturing() const { return capturing_; }

    // The HTTP body of GET /upload?path=<dir>. Parses it and marks the list
    // ready. `dir` is the folder it lists.
    void setResponse(const String &body, const char *dir);

    // The fetch failed: finish with an empty list, so the Jobs screen
    // stops waiting rather than spinning forever.
    void fail(const char *dir);

    bool ready() const { return ready_; }
    void clearReady() { ready_ = false; }
    // True when the last fetch failed outright, as opposed to succeeding
    // with nothing in it -- the Jobs screen says which.
    bool failed() const { return failed_; }
    int count() const { return count_; }
    const FluidNCFileEntry &entry(int i) const { return files_[i]; }
    const char *dir() const { return dir_; }

private:
    bool capturing_ = false;
    bool ready_ = false;
    bool failed_ = false;
    FluidNCFileEntry *files_ = nullptr; // PSRAM, grown as needed
    int capacity_ = 0;
    int count_ = 0;
    char dir_[SD_DIR_MAX] = "";

    void setDir(const char *dir);
    FluidNCFileEntry *append();
    void parseJson(const String &body);
};
