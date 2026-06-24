from pathlib import Path

import fastapi_chameleon

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi_chameleon.engine import render

from content import (
    NodeNotFoundError,
    get_leaf,
    get_node,
    is_grid,
    is_leaf,
)

router = APIRouter()


def _slugs_from_path(path: str) -> tuple[str, ...]:
    return tuple(p for p in path.split("/") if p)


def _build_breadcrumbs(slugs: tuple[str, ...]) -> list[dict] | None:
    if not slugs:
        return None

    crumbs = [{"title": "Home", "href": "/"}]
    for i in range(len(slugs) - 1):  # exclude the current page itself
        ancestor_slugs = slugs[: i + 1]
        node = get_node(*ancestor_slugs) if is_grid(*ancestor_slugs) else get_leaf(*ancestor_slugs)
        crumbs.append({"title": node.title, "href": node.href})

    return crumbs


@router.get("/", response_class=HTMLResponse)
@fastapi_chameleon.template("motecture/grid.pt")
def index(request: Request):
    node = get_node()
    return {
        "node": node,
        "title": node.title,
        "breadcrumbs": None,
    }


@router.get("/{path:path}", response_class=HTMLResponse)
def resolve(request: Request, path: str):
    slugs = _slugs_from_path(path)

    try:
        if is_leaf(*slugs):
            node = get_leaf(*slugs)
            template_name = "motecture/leaf.pt"
        elif is_grid(*slugs):
            node = get_node(*slugs)
            template_name = "motecture/grid.pt"
        else:
            raise NodeNotFoundError(f"No content at '{path}'")
    except NodeNotFoundError:
        raise HTTPException(status_code=404)

    html = render(
        template_name,
        node=node,
        title=node.title,
        breadcrumbs=_build_breadcrumbs(slugs),
    )
    return HTMLResponse(html)






dummy_node = {
        "title": "Home",
        "children": [
            {
                "slug": "forest",
                "title": "",
                "href": "/forest",
                "thumbnail": "https://picsum.photos/seed/forest/400",
            },
            {
                "slug": "ocean",
                "title": "",
                "href": "/ocean",
                "thumbnail": "",
            },
            {
                "slug": "desert",
                "title": "",
                "href": "/desert",
                "thumbnail": "https://picsum.photos/seed/desert/400",
            },
            {
                "slug": "tundra",
                "title": "",
                "href": "/tundra",
                "thumbnail": None,  # test the no-thumbnail fallback case
            },
            {
                "slug": "mountains",
                "title": "",
                "href": "/mountains",
                "thumbnail": "https://picsum.photos/seed/mountains/400",
            },
            {
                "slug": "",
                "title": "",
                "href": "",
                "thumbnail": "",
            },
            {
                "slug": "jungle",
                "title": "",
                "href": "/jungle",
                "thumbnail": "https://picsum.photos/seed/jungle/400",
            },
            {
                "slug": "swamp",
                "title": "",
                "href": "/swamp",
                "thumbnail": "https://picsum.photos/seed/swamp/400",
            },
            {
                "slug": "coast",
                "title": "",
                "href": "/coast",
                "thumbnail": "https://picsum.photos/seed/coast/400",
            },
        ],
    }