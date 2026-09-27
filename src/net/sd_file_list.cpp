#include "sd_file_list.h"
#include <ArduinoJson.h>
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
}

void SdFileList::beginCapture()
{
    ready_ = false;
    capturing_ = true;
    Serial.println("[fluidnc] requesting SD file list (GET /upload?path=/)");
}

void SdFileList::setResponse(const String &body)
{
    capturing_ = false;
    parseJson(body);
}

void SdFileList::fail()
{
    capturing_ = false;
    count_ = 0;
    ready_ = true;
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
        ready_ = true;
        return;
    }

    for (JsonObject f : doc["files"].as<JsonArray>())
    {
        if (count_ >= MAX_FILES) break;

        const char *name = f["name"] | "";

        // Observed on live hardware: this FluidNC build emits "size" as a
        // quoted string (e.g. "size":"100181"), not a JSON number as the
        // upstream source (FileCommands.cpp) would suggest -- accept either
        // shape rather than trust one representation.
        int32_t size = -1;
        JsonVariantConst sizeVal = f["size"];
        if (sizeVal.is<const char *>()) size = atoi(sizeVal.as<const char *>());
        else size = sizeVal | -1;

        if (size < 0) continue;              // directories: skip, flat list only
        if (!hasGcodeExtension(name)) continue;

        FluidNCFileEntry &entry = files_[count_++];
        strncpy(entry.name, name, sizeof(entry.name) - 1);
        entry.name[sizeof(entry.name) - 1] = '\0';
        entry.size = size;
    }

    Serial.printf("[fluidnc] file list parsed: %d g-code file(s)\n", count_);
    ready_ = true;
}
