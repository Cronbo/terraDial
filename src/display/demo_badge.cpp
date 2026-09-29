#include "demo_badge.h"
#include <lvgl.h>
#include "palette.h"
#include "../net/demo_mode.h"

namespace
{
    lv_obj_t *ring = nullptr;
    lv_obj_t *tag = nullptr;
    bool shown = false;

    void create()
    {
        // Just inside the bezel, where no screen draws anything: every
        // screen keeps its content ~5px or more clear of the glass edge.
        ring = lv_obj_create(lv_layer_top());
        lv_obj_set_size(ring, 240, 240);
        lv_obj_center(ring);
        lv_obj_set_style_radius(ring, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_opa(ring, LV_OPA_TRANSP, 0);
        lv_obj_set_style_border_color(ring, Palette::accentSecondary(), 0);
        lv_obj_set_style_border_width(ring, 3, 0);
        lv_obj_set_style_pad_all(ring, 0, 0);
        // lv_obj_create()'s objects take clicks by default; a full-screen
        // one left clickable would swallow every touch on every screen.
        lv_obj_clear_flag(ring, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_clear_flag(ring, LV_OBJ_FLAG_SCROLLABLE);

        tag = lv_label_create(lv_layer_top());
        lv_label_set_text(tag, "DEMO");
        lv_obj_set_style_text_font(tag, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(tag, Palette::bgApp(), 0);
        lv_obj_set_style_text_letter_space(tag, 1, 0);
        lv_obj_set_style_bg_color(tag, Palette::accentSecondary(), 0);
        lv_obj_set_style_bg_opa(tag, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(tag, 8, 0);
        lv_obj_set_style_pad_hor(tag, 7, 0);
        lv_obj_set_style_pad_ver(tag, 1, 0);
        lv_obj_align(tag, LV_ALIGN_TOP_MID, 0, 3);
        lv_obj_clear_flag(tag, LV_OBJ_FLAG_CLICKABLE);
    }
}

namespace DemoBadge
{
    void update()
    {
        bool on = Demo::isOn();
        if (on == shown) return;
        shown = on;
        if (!ring) create();
        if (on)
        {
            lv_obj_clear_flag(ring, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(tag, LV_OBJ_FLAG_HIDDEN);
            // Above anything created on the top layer since they last showed.
            lv_obj_move_foreground(ring);
            lv_obj_move_foreground(tag);
        }
        else
        {
            lv_obj_add_flag(ring, LV_OBJ_FLAG_HIDDEN);
            lv_obj_add_flag(tag, LV_OBJ_FLAG_HIDDEN);
        }
    }
}
