#include "sd_file_list.h"
#include <ArduinoJson.h>
#include <esp_heap_caps.h>
#include <string.h>
#include <stdlib.h>

namespace
{
    bool hasGcodeExtension(const char *name)
    {
        size_t len = strlen(name);
        auto endsWithCi = [&](const char *suffix) {
            size_t slen = strlen(suffix);
            return len >= slen && strcasecmp(name + len - slen, suffix) == 0;
        };
        return endsWithCi(".gcode") || endsWithCi(".nc") || endsWithCi(".g");
    }

    // Folders nobody means to open: Windows' per-volume index (which
    // FluidNC lists like any other folder), and dot-folders such as macOS's
    // .Trashes and .Spotlight-V100.
    bool isHiddenFolder(const char *name)
    {
        return name[0] == '.' || strcmp(name, "System Volume Information") == 0;
    }
}

void SdFileList::beginCapture()
{
    ready_ = false;
    capturing_ = true;
}

void SdFileList::setDir(const char *dir)
{
    strncpy(dir_, dir ? dir : "", sizeof(dir_) - 1);
    dir_[sizeof(dir_) - 1] = '\0';
}

void SdFileList::setResponse(const String &body, const char *dir)
{
    capturing_ = false;
    failed_ = false;
    setDir(dir);
    parseJson(body);
}

void SdFileList::fail(const char *dir)
{
    capturing_ = false;
    failed_ = true;
    setDir(dir);
    count_ = 0;
    ready_ = true;
}

FluidNCFileEntry *SdFileList::append()
{
    if (count_ == capacity_)
    {
        int next = capacity_ ? capacity_ * 2 : 32;
        size_t bytes = next * sizeof(FluidNCFileEntry);
        // PSRAM first: at ~264 bytes an entry, a big folder would otherwise
        // come out of the internal RAM that Wi-Fi and TLS share.
        void *grown = heap_caps_realloc(files_, bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (!grown) grown = realloc(files_, bytes);
        if (!grown) return nullptr;
        files_ = (FluidNCFileEntry *)grown;
        capacity_ = next;
    }
    FluidNCFileEntry *e = &files_[count_++];
    *e = FluidNCFileEntry();
    return e;
}

void SdFileList::parseJson(const String &body)
{
    count_ = 0;

    // Only name and size are used -- filtering keeps the document small
    // however much else (dates, short names, storage stats) FluidNC sends.
    JsonDocument filter;
    filter["files"][0]["name"] = true;
    filter["files"][0]["size"] = true;

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, body, DeserializationOption::Filter(filter));
    if (err)
    {
        Serial.printf("[fluidnc] file list JSON parse failed: %s (%u bytes)\n", err.c_str(), (unsigned)body.length());
        failed_ = true;
        ready_ = true;
        return;
    }

    int files = 0, dirs = 0;
    for (JsonObject f : doc["files"].as<JsonArray>())
    {
        const char *name = f["name"] | "";
        if (!name[0]) continue;

        // FluidNC emits "size" as a quoted string (e.g. "size":"100181"),
        // not a JSON number as its source (FileCommands.cpp) would suggest
        // -- accept either shape rather than trust one representation. A
        // folder is "-1".
        int32_t size = -1;
        JsonVariantConst sizeVal = f["size"];
        if (sizeVal.is<const char *>()) size = atoi(sizeVal.as<const char *>());
        else size = sizeVal | -1;

        bool isDir = size < 0;
        if (isDir ? isHiddenFolder(name) : !hasGcodeExtension(name)) continue;

        if (strlen(name) > SD_NAME_MAX)
        {
            // Can't happen on FAT, but never store a name cut short -- it
            // would point at a file that doesn't exist.
            Serial.printf("[fluidnc] skipping over-long name: %.40s...\n", name);
            continue;
        }

        FluidNCFileEntry *entry = append();
        if (!entry)
        {
            Serial.printf("[fluidnc] out of memory after %d entries, list truncated\n", count_);
            break;
        }
        strcpy(entry->name, name);
        entry->size = isDir ? -1 : size;
        entry->isDir = isDir;
        if (isDir) dirs++;
        else files++;
    }

    Serial.printf("[fluidnc] /%s: %d g-code file(s), %d folder(s)\n", dir_, files, dirs);
    ready_ = true;
}
