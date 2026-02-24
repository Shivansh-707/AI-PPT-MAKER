import traceback
from google_auth import get_services
from models import PresentationOutline
from image_search import find_image_url
from dotenv import load_dotenv

load_dotenv()

SLIDE_WIDTH_EMU  = 9144000
SLIDE_HEIGHT_EMU = 6858000

THEME_STYLES = {
    "Default (No Theme)": {
        "title_color":           {"red": 0.13, "green": 0.13, "blue": 0.53},
        "body_color":            {"red": 0.15, "green": 0.15, "blue": 0.15},
        "background_color":      None,
        "table_header_color":    {"red": 0.13, "green": 0.13, "blue": 0.53},
        "table_body_text_color": {"red": 0.10, "green": 0.10, "blue": 0.10},
    },
    "Minimal": {
        "title_color":           {"red": 0.05, "green": 0.05, "blue": 0.05},
        "body_color":            {"red": 0.25, "green": 0.25, "blue": 0.25},
        "background_color":      {"red": 0.98, "green": 0.98, "blue": 0.98},
        "table_header_color":    {"red": 0.15, "green": 0.15, "blue": 0.15},
        "table_body_text_color": {"red": 0.10, "green": 0.10, "blue": 0.10},
    },
    "Dark": {
        "title_color":           {"red": 0.45, "green": 0.75, "blue": 1.0},
        "body_color":            {"red": 0.85, "green": 0.85, "blue": 0.90},
        "background_color":      {"red": 0.07, "green": 0.07, "blue": 0.10},
        "table_header_color":    {"red": 0.18, "green": 0.45, "blue": 0.75},
        "table_body_text_color": {"red": 1.0,  "green": 1.0,  "blue": 1.0},   # ← white text
    },
    "Corporate": {
        "title_color":           {"red": 0.0,  "green": 0.25, "blue": 0.60},
        "body_color":            {"red": 0.12, "green": 0.12, "blue": 0.18},
        "background_color":      {"red": 0.93, "green": 0.96, "blue": 1.0},
        "table_header_color":    {"red": 0.0,  "green": 0.25, "blue": 0.60},
        "table_body_text_color": {"red": 0.10, "green": 0.10, "blue": 0.10},
    },
    "Vibrant": {
        "title_color":           {"red": 0.55, "green": 0.0,  "blue": 0.75},
        "body_color":            {"red": 0.10, "green": 0.10, "blue": 0.15},
        "background_color":      {"red": 0.97, "green": 0.95, "blue": 1.0},
        "table_header_color":    {"red": 0.55, "green": 0.0,  "blue": 0.75},
        "table_body_text_color": {"red": 0.10, "green": 0.10, "blue": 0.10},
    },
    "Ocean": {
        "title_color":           {"red": 0.0,  "green": 0.50, "blue": 0.60},
        "body_color":            {"red": 0.05, "green": 0.15, "blue": 0.20},
        "background_color":      {"red": 0.90, "green": 0.97, "blue": 0.98},
        "table_header_color":    {"red": 0.0,  "green": 0.45, "blue": 0.55},
        "table_body_text_color": {"red": 0.05, "green": 0.10, "blue": 0.15},
    },
}


# ── Safe dict accessor ────────────────────────────────────────────────────────
def safe_get(obj, *keys, default=None):
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        else:
            return default
    return obj


# ── Table Builder ─────────────────────────────────────────────────────────────
def build_table_requests(page_object_id, table_data, slide_index, header_color, body_text_color):
    requests = []
    table_id = f"table_{slide_index}"

    headers = [str(h) for h in table_data.headers]
    rows    = []
    for row in table_data.rows:
        if isinstance(row, list):
            rows.append([str(c) for c in row])
        elif isinstance(row, dict):
            rows.append([str(v) for v in row.values()])
        else:
            rows.append([str(row)])

    num_rows = len(rows) + 1
    num_cols = len(headers)

    # 1. Create table
    requests.append({
        "createTable": {
            "objectId": table_id,
            "elementProperties": {
                "pageObjectId": page_object_id,
                "size": {
                    "height": {"magnitude": 3200000, "unit": "EMU"},
                    "width":  {"magnitude": 8200000, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": 457200,
                    "translateY": 1800000,
                    "unit": "EMU",
                },
            },
            "rows":    num_rows,
            "columns": num_cols,
        }
    })

    # 2. Header row — always white text on colored background
    for col_idx, header in enumerate(headers):
        requests.append({
            "insertText": {
                "objectId": table_id,
                "cellLocation": {"rowIndex": 0, "columnIndex": col_idx},
                "text": header,
            }
        })
        requests.append({
            "updateTextStyle": {
                "objectId": table_id,
                "cellLocation": {"rowIndex": 0, "columnIndex": col_idx},
                "style": {
                    "bold": True,
                    "fontSize": {"magnitude": 14, "unit": "PT"},
                    "foregroundColor": {
                        "opaqueColor": {
                            "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                        }
                    },
                },
                "fields": "bold,fontSize,foregroundColor",
            }
        })
        requests.append({
            "updateTableCellProperties": {
                "objectId": table_id,
                "tableRange": {
                    "location": {"rowIndex": 0, "columnIndex": col_idx},
                    "rowSpan": 1, "columnSpan": 1,
                },
                "tableCellProperties": {
                    "tableCellBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": header_color}}
                    }
                },
                "fields": "tableCellBackgroundFill.solidFill.color",
            }
        })

    # 3. Data rows — theme-aware text color
    for row_idx, row in enumerate(rows, start=1):
        for col_idx, cell in enumerate(row):
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {
                        "rowIndex":    row_idx,
                        "columnIndex": col_idx,
                    },
                    "text": cell,
                }
            })
            requests.append({
                "updateTextStyle": {
                    "objectId": table_id,
                    "cellLocation": {
                        "rowIndex":    row_idx,
                        "columnIndex": col_idx,
                    },
                    "style": {
                        "fontSize": {"magnitude": 11, "unit": "PT"},
                        "foregroundColor": {
                            "opaqueColor": {"rgbColor": body_text_color}  # ← theme-aware
                        },
                    },
                    "fields": "fontSize,foregroundColor",
                }
            })

    return requests


# ── Main Presentation Builder ─────────────────────────────────────────────────
def create_presentation(
    outline: PresentationOutline,
    theme: str = "Default (No Theme)",
    image_url: str = "",
    use_images: bool = True,
) -> str:
    slides_service, drive_service = get_services()

    # 1. Create blank presentation
    presentation = slides_service.presentations().create(
        body={"title": outline.topic}
    ).execute()
    presentation_id = presentation["presentationId"]
    print(f"Created presentation ID: {presentation_id}")

    # Delete default blank slide
    default_slide_id = presentation["slides"][0]["objectId"]
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [{"deleteObject": {"objectId": default_slide_id}}]},
    ).execute()

    styles = THEME_STYLES.get(theme, THEME_STYLES["Default (No Theme)"])

    # 2. Create all slides
    create_requests = [{
        "createSlide": {
            "objectId": "slide_0",
            "slideLayoutReference": {"predefinedLayout": "TITLE"},
        }
    }]
    for i in range(len(outline.slides)):
        create_requests.append({
            "createSlide": {
                "objectId": f"slide_{i+1}",
                "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
            }
        })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": create_requests}
    ).execute()

    # 3. Fetch updated presentation
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    background_requests = []
    delete_requests     = []
    resize_requests     = []
    text_requests       = []
    image_requests      = []
    table_requests      = []

    # 4. Background color per theme
    if styles.get("background_color"):
        bg = styles["background_color"]
        for slide in presentation["slides"]:
            background_requests.append({
                "updatePageProperties": {
                    "objectId": slide["objectId"],
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": bg}}
                        }
                    },
                    "fields": "pageBackgroundFill.solidFill.color",
                }
            })

    # 5. Title slide
    title_slide    = presentation["slides"][0]
    title_slide_id = title_slide["objectId"]

    for element in title_slide.get("pageElements", []):
        if "shape" in element:
            ph_type = safe_get(element, "shape", "placeholder", "type", default="")
            if ph_type == "CENTERED_TITLE":
                text_requests += [
                    {"insertText": {"objectId": element["objectId"], "text": outline.topic}},
                    {
                        "updateTextStyle": {
                            "objectId": element["objectId"],
                            "style": {
                                "bold": True,
                                "fontSize": {"magnitude": 38, "unit": "PT"},
                                "foregroundColor": {
                                    "opaqueColor": {"rgbColor": styles["title_color"]}
                                },
                            },
                            "fields": "bold,fontSize,foregroundColor",
                        }
                    },
                ]
            elif ph_type == "SUBTITLE":
                text_requests.append({
                    "insertText": {
                        "objectId": element["objectId"],
                        "text": "AI-Generated Presentation",
                    }
                })

    # Hero image on title slide
    if image_url.strip():
        hero_w = 4000000
        hero_h = 2250000
        image_requests.append({
            "createImage": {
                "objectId": "hero_image_title",
                "url": image_url.strip(),
                "elementProperties": {
                    "pageObjectId": title_slide_id,
                    "size": {
                        "height": {"magnitude": hero_h, "unit": "EMU"},
                        "width":  {"magnitude": hero_w, "unit": "EMU"},
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": int((SLIDE_WIDTH_EMU - hero_w) / 2),
                        "translateY": int(SLIDE_HEIGHT_EMU * 0.42),
                        "unit": "EMU",
                    },
                },
            }
        })

    # 6. Content slides
    for i, slide in enumerate(outline.slides, start=1):
        try:
            page         = presentation["slides"][i]
            title_id     = None
            body_id      = None
            body_element = None
            has_table    = slide.table is not None

            for element in page.get("pageElements", []):
                if not isinstance(element, dict):
                    continue
                if "shape" in element:
                    ph_type = safe_get(element, "shape", "placeholder", "type", default="")
                    if ph_type == "TITLE":
                        title_id = element["objectId"]
                    elif ph_type in ("BODY", "OBJECT"):
                        body_id      = element["objectId"]
                        body_element = element

            # Delete body placeholder on table slides → removes "Click to add text"
            if has_table and body_id:
                delete_requests.append({
                    "deleteObject": {"objectId": body_id}
                })
                body_id      = None
                body_element = None

            # Resize body to left 50% on image slides
            if use_images and slide.image_query and not has_table and body_element:
                curr_w = safe_get(body_element, "size", "width", "magnitude", default=8229600)
                curr_t = body_element.get("transform", {}) if isinstance(body_element, dict) else {}
                if not isinstance(curr_w, (int, float)):
                    curr_w = 8229600
                target_w    = int(SLIDE_WIDTH_EMU * 0.50)
                new_scale_x = target_w / curr_w

                resize_requests.append({
                    "updatePageElementTransform": {
                        "objectId": body_id,
                        "transform": {
                            "scaleX":     new_scale_x,
                            "scaleY":     curr_t.get("scaleY", 1.0) if isinstance(curr_t, dict) else 1.0,
                            "shearX":     0,
                            "shearY":     0,
                            "translateX": curr_t.get("translateX", 457200) if isinstance(curr_t, dict) else 457200,
                            "translateY": curr_t.get("translateY", 1270000) if isinstance(curr_t, dict) else 1270000,
                            "unit": "EMU"
                        },
                        "applyMode": "ABSOLUTE"
                    }
                })

            # Title text
            if title_id:
                text_requests += [
                    {"insertText": {"objectId": title_id, "text": slide.title}},
                    {
                        "updateTextStyle": {
                            "objectId": title_id,
                            "style": {
                                "bold": True,
                                "fontSize": {"magnitude": 24, "unit": "PT"},
                                "foregroundColor": {
                                    "opaqueColor": {"rgbColor": styles["title_color"]}
                                },
                            },
                            "fields": "bold,fontSize,foregroundColor",
                        }
                    },
                ]

            # Table slide
            if has_table:
                print(f"  📊 Table added to slide {i}: {slide.title}")
                table_requests += build_table_requests(
                    page["objectId"],
                    slide.table,
                    slide_index=i,
                    header_color=styles["table_header_color"],
                    body_text_color=styles["table_body_text_color"],  # ← theme-aware
                )

            # Normal bullet slide
            else:
                if body_id:
                    bullet_text = "\n".join(f"• {b}" for b in slide.bullets)
                    text_requests += [
                        {"insertText": {"objectId": body_id, "text": bullet_text}},
                        {
                            "updateTextStyle": {
                                "objectId": body_id,
                                "style": {
                                    "fontSize": {"magnitude": 14, "unit": "PT"},
                                    "foregroundColor": {
                                        "opaqueColor": {"rgbColor": styles["body_color"]}
                                    },
                                },
                                "fields": "fontSize,foregroundColor",
                            }
                        },
                    ]

                # Per-slide image
                if use_images and slide.image_query:
                    img_url = find_image_url(slide.image_query)
                    if img_url:
                        img_w = 3800000
                        img_h = 3200000
                        image_requests.append({
                            "createImage": {
                                "objectId": f"slide_image_{i}",
                                "url": img_url,
                                "elementProperties": {
                                    "pageObjectId": page["objectId"],
                                    "size": {
                                        "height": {"magnitude": img_h, "unit": "EMU"},
                                        "width":  {"magnitude": img_w, "unit": "EMU"},
                                    },
                                    "transform": {
                                        "scaleX": 1, "scaleY": 1,
                                        "translateX": SLIDE_WIDTH_EMU - img_w - 150000,
                                        "translateY": 1300000,
                                        "unit": "EMU",
                                    },
                                },
                            }
                        })
                        print(f"  🖼️  Slide {i}: '{slide.image_query}'")
                    else:
                        print(f"  ⚠️  No image for slide {i}: '{slide.image_query}'")

            # Speaker notes
            if slide.notes:
                notes_page = safe_get(page, "slideProperties", "notesPage", default={})
                if isinstance(notes_page, dict):
                    for ne in notes_page.get("pageElements", []):
                        if isinstance(ne, dict) and "shape" in ne:
                            ne_ph = safe_get(ne, "shape", "placeholder", "type", default="")
                            if ne_ph == "BODY":
                                text_requests.append({
                                    "insertText": {
                                        "objectId": ne["objectId"],
                                        "text": slide.notes,
                                    }
                                })

        except Exception as e:
            print(f"  ❌ Error on slide {i}: {e}")
            traceback.print_exc()
            continue

    # 7. Execute in correct order
    all_requests = (
        background_requests +
        delete_requests +
        resize_requests +
        text_requests +
        table_requests +
        image_requests
    )
    if all_requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": all_requests}
        ).execute()

    # 8. Share publicly
    drive_service.permissions().create(
        fileId=presentation_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    link = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    print(f"\n✅ Presentation link: {link}")
    return link


if __name__ == "__main__":
    from research_agent import build_outline
    outline = build_outline("Artificial Intelligence")
    link = create_presentation(outline, theme="Dark", image_url="", use_images=True)
    print(f"\n✅ Presentation created: {link}")
