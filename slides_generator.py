from google_auth import get_services
from models import PresentationOutline


def create_presentation(outline: PresentationOutline) -> str:
    slides_service, drive_service = get_services()

    # Create blank presentation
    presentation = slides_service.presentations().create(
        body={"title": outline.topic}
    ).execute()

    presentation_id = presentation["presentationId"]
    print(f"Created presentation ID: {presentation_id}")

    # ✅ FIX: Google auto-creates one blank slide — delete it first
    default_slide_id = presentation["slides"][0]["objectId"]
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [{"deleteObject": {"objectId": default_slide_id}}]}
    ).execute()

    requests = []

    # Title slide
    requests.append({
        "createSlide": {
            "objectId": "slide_0",
            "slideLayoutReference": {"predefinedLayout": "TITLE"}
        }
    })

    # Content slides
    for i, slide in enumerate(outline.slides, start=1):
        requests.append({
            "createSlide": {
                "objectId": f"slide_{i}",
                "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}
            }
        })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()

    # Fetch updated presentation to get element IDs
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    text_requests = []

    # --- Title slide ---
    title_slide = presentation["slides"][0]
    for element in title_slide["pageElements"]:
        if "shape" in element:
            placeholder_type = element["shape"].get("placeholder", {}).get("type", "")
            if placeholder_type == "CENTERED_TITLE":
                text_requests.append({
                    "insertText": {"objectId": element["objectId"], "text": outline.topic}
                })
                text_requests.append({
                    "updateTextStyle": {
                        "objectId": element["objectId"],
                        "style": {
                            "bold": True,
                            "fontSize": {"magnitude": 36, "unit": "PT"},
                            "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 0.1, "green": 0.1, "blue": 0.5}}}
                        },
                        "fields": "bold,fontSize,foregroundColor"
                    }
                })
            elif placeholder_type == "SUBTITLE":
                text_requests.append({
                    "insertText": {"objectId": element["objectId"], "text": "AI-Generated Presentation"}
                })

    # --- Content slides ---
    for i, slide in enumerate(outline.slides, start=1):
        page = presentation["slides"][i]
        title_id = None
        body_id = None

        for element in page["pageElements"]:
            if "shape" in element:
                placeholder_type = element["shape"].get("placeholder", {}).get("type", "")
                if placeholder_type == "TITLE":
                    title_id = element["objectId"]
                elif placeholder_type in ("BODY", "OBJECT"):
                    body_id = element["objectId"]

        # Insert + format title
        if title_id:
            text_requests.append({
                "insertText": {"objectId": title_id, "text": slide.title}
            })
            text_requests.append({
                "updateTextStyle": {
                    "objectId": title_id,
                    "style": {
                        "bold": True,
                        "fontSize": {"magnitude": 24, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 0.1, "green": 0.1, "blue": 0.5}}}
                    },
                    "fields": "bold,fontSize,foregroundColor"
                }
            })

        # Insert + format bullets
        if body_id:
            bullet_text = "\n".join([f"• {bullet}" for bullet in slide.bullets])
            text_requests.append({
                "insertText": {"objectId": body_id, "text": bullet_text}
            })
            text_requests.append({
                "updateTextStyle": {
                    "objectId": body_id,
                    "style": {
                        "fontSize": {"magnitude": 16, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 0.2, "green": 0.2, "blue": 0.2}}}
                    },
                    "fields": "fontSize,foregroundColor"
                }
            })

        # Insert speaker notes
        if slide.notes:
            notes_page = page.get("slideProperties", {}).get("notesPage", {})
            for notes_element in notes_page.get("pageElements", []):
                if "shape" in notes_element:
                    notes_placeholder = notes_element["shape"].get("placeholder", {}).get("type", "")
                    if notes_placeholder == "BODY":
                        text_requests.append({
                            "insertText": {
                                "objectId": notes_element["objectId"],
                                "text": slide.notes
                            }
                        })

    if text_requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": text_requests}
        ).execute()

    # Share publicly
    drive_service.permissions().create(
        fileId=presentation_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    link = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    return link


if __name__ == "__main__":
    from research_agent import build_outline
    outline = build_outline("Artificial Intelligence")
    link = create_presentation(outline)
    print(f"\n✅ Presentation created: {link}")
