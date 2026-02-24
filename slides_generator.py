from google_auth import get_services
from models import PresentationOutline
from image_search import find_image_url

SLIDE_WIDTH_EMU  = 9144000
SLIDE_HEIGHT_EMU = 6858000

THEME_STYLES = {
    "Default (No Theme)": {
        "title_color":      {"red": 0.1,  "green": 0.1,  "blue": 0.5},
        "body_color":       {"red": 0.2,  "green": 0.2,  "blue": 0.2},
        "background_color": None,
    },
    "Minimal": {
        "title_color":      {"red": 0.0,  "green": 0.0,  "blue": 0.0},
        "body_color":       {"red": 0.2,  "green": 0.2,  "blue": 0.2},
        "background_color": {"red": 1.0,  "green": 1.0,  "blue": 1.0},
    },
    "Dark": {
        "title_color":      {"red": 1.0,  "green": 1.0,  "blue": 1.0},
        "body_color":       {"red": 0.9,  "green": 0.9,  "blue": 0.9},
        "background_color": {"red": 0.07, "green": 0.07, "blue": 0.07},
    },
    "Corporate": {
        "title_color":      {"red": 0.0,  "green": 0.25, "blue": 0.6},
        "body_color":       {"red": 0.15, "green": 0.15, "blue": 0.2},
        "background_color": {"red": 0.90, "green": 0.94, "blue": 1.0},
    },
}


def create_presentation(
    outline: PresentationOutline,
    theme: str = "Default (No Theme)",
    image_url: str = "",
    use_images: bool = True,          # ← controls per-slide Pexels images
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
    create_requests = [
        {
            "createSlide": {
                "objectId": "slide_0",
                "slideLayoutReference": {"predefinedLayout": "TITLE"},
            }
        }
    ]
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
    resize_requests     = []
    text_requests       = []
    image_requests      = []

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

    # 5. Title slide text
    title_slide    = presentation["slides"][0]
    title_slide_id = title_slide["objectId"]

    for element in title_slide["pageElements"]:
        if "shape" in element:
            ph_type = element["shape"].get("placeholder", {}).get("type", "")
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

    # Hero image on title slide (user-supplied URL)
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
        page         = presentation["slides"][i]
        title_id     = None
        body_id      = None
        body_element = None

        for element in page["pageElements"]:
            if "shape" in element:
                ph_type = element["shape"].get("placeholder", {}).get("type", "")
                if ph_type == "TITLE":
                    title_id = element["objectId"]
                elif ph_type in ("BODY", "OBJECT"):
                    body_id      = element["objectId"]
                    body_element = element

        # Shrink body text box to LEFT 50% only when image will be added
        if use_images and slide.image_query and body_element:
            curr_w = body_element.get("size", {}).get("width", {}).get("magnitude", 8229600)
            curr_t = body_element.get("transform", {})
            target_w    = int(SLIDE_WIDTH_EMU * 0.50)
            new_scale_x = target_w / curr_w

            resize_requests.append({
                "updatePageElementTransform": {
                    "objectId": body_id,
                    "transform": {
                        "scaleX": new_scale_x,
                        "scaleY": curr_t.get("scaleY", 1.0),
                        "shearX": 0,
                        "shearY": 0,
                        "translateX": curr_t.get("translateX", 457200),
                        "translateY": curr_t.get("translateY", 1270000),
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

        # Bullet text
        if body_id:
            bullet_text = "\n".join(f"• {b}" for b in slide.bullets)
            text_requests += [
                {"insertText": {"objectId": body_id, "text": bullet_text}},
                {
                    "updateTextStyle": {
                        "objectId": body_id,
                        "style": {
                            "fontSize": {"magnitude": 16, "unit": "PT"},
                            "foregroundColor": {
                                "opaqueColor": {"rgbColor": styles["body_color"]}
                            },
                        },
                        "fields": "fontSize,foregroundColor",
                    }
                },
            ]

        # Speaker notes
        if slide.notes:
            notes_page = page.get("slideProperties", {}).get("notesPage", {})
            for ne in notes_page.get("pageElements", []):
                if "shape" in ne:
                    if ne["shape"].get("placeholder", {}).get("type", "") == "BODY":
                        text_requests.append({
                            "insertText": {
                                "objectId": ne["objectId"],
                                "text": slide.notes,
                            }
                        })

        # Per-slide Pexels image — RIGHT half, aligned with body text
        if use_images and slide.image_query:
            img_url = find_image_url(slide.image_query)
            if img_url:
                img_w = 3800000
                img_h = 3200000
                img_x = SLIDE_WIDTH_EMU - img_w - 150000
                img_y = 1300000
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
                                "translateX": img_x,
                                "translateY": img_y,
                                "unit": "EMU",
                            },
                        },
                    }
                })
                print(f"  🖼️  Slide {i}: '{slide.image_query}'")
            else:
                print(f"  ⚠️  No image found for slide {i}: '{slide.image_query}'")

    # 7. Execute in correct order: bg → resize → text → images
    all_requests = background_requests + resize_requests + text_requests + image_requests
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
    link = create_presentation(outline, theme="Corporate", image_url="", use_images=True)
    print(f"\n✅ Presentation created: {link}")
