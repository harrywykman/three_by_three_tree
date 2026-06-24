import random
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

CONTENT_ROOT = Path("content")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")
GRID_SIZE = 9


class NodeNotFoundError(Exception):
    pass


class ContentError(Exception):
    """Raised when content on disk violates the expected structure."""


@dataclass
class Child:
    slug: str
    title: str
    href: str
    is_leaf: bool
    thumbnail: str | None = None
    position: int | None = None


@dataclass
class Node:
    slug: str
    title: str
    href: str
    children: list[Child | None] = field(default_factory=list)
    image: str | None = None
    text: str | None = None


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _find_image(dir_path: Path, slug: str) -> str | None:
    for ext in IMAGE_EXTS:
        candidate = dir_path / f"{slug}{ext}"
        if candidate.exists():
            rel = candidate.relative_to(CONTENT_ROOT)
            return f"/content-assets/{rel.as_posix()}"
    return None


def _href(*slugs: str) -> str:
    return "/" + "/".join(slugs)


def _assign_grid_positions(children: list[Child], *, context: str) -> list[Child | None]:
    slots: list[Child | None] = [None] * GRID_SIZE

    positioned = [c for c in children if c.position is not None]
    unpositioned = [c for c in children if c.position is None]

    for child in positioned:
        idx = child.position - 1
        if not (0 <= idx < GRID_SIZE):
            raise ContentError(
                f"{context}: invalid position {child.position} for '{child.slug}' "
                f"(must be 1-{GRID_SIZE})"
            )
        if slots[idx] is not None:
            raise ContentError(
                f"{context}: position {child.position} claimed by both "
                f"'{slots[idx].slug}' and '{child.slug}'"
            )
        slots[idx] = child

    empty_indices = [i for i, s in enumerate(slots) if s is None]

    if len(unpositioned) > len(empty_indices):
        raise ContentError(
            f"{context}: {len(children)} children but only {GRID_SIZE} grid slots "
            f"({len(positioned)} fixed, {len(empty_indices)} free)"
        )

    random.shuffle(unpositioned)
    random.shuffle(empty_indices)
    for idx, child in zip(empty_indices, unpositioned):
        slots[idx] = child

    return slots


def is_leaf(*slugs: str) -> bool:
    """True if this path resolves to a leaf (a {slug}.yaml file), not a grid directory."""
    parent = CONTENT_ROOT.joinpath(*slugs[:-1])
    return (parent / f"{slugs[-1]}.yaml").exists()


def is_grid(*slugs: str) -> bool:
    """True if this path resolves to a grid (a directory)."""
    return CONTENT_ROOT.joinpath(*slugs).is_dir()


@lru_cache(maxsize=256)
def get_node(*slugs: str) -> Node:
    """Return a grid node (root or any category depth) with up to 9 children slotted in."""
    path = CONTENT_ROOT.joinpath(*slugs)

    if not path.is_dir():
        raise NodeNotFoundError(f"No content directory at '{'/'.join(slugs) or '/'}'")

    meta = _read_yaml(path / "meta.yaml")
    title = meta.get("title", slugs[-1] if slugs else "Home")
    context = "/".join(slugs) or "(root)"

    children: list[Child] = []

    for entry in sorted(path.iterdir()):
        if entry.is_dir():
            child_slug = entry.name
            child_meta = _read_yaml(entry / "meta.yaml")
            children.append(
                Child(
                    slug=child_slug,
                    title=child_meta.get("title", child_slug),
                    href=_href(*slugs, child_slug),
                    is_leaf=False,
                    thumbnail=(
                        _find_image(entry, child_slug)
                        or _find_image(entry, "thumbnail")
                    ),
                    position=child_meta.get("position"),
                )
            )
        elif entry.suffix == ".yaml" and entry.stem != "meta":
            child_slug = entry.stem
            child_meta = _read_yaml(entry)
            children.append(
                Child(
                    slug=child_slug,
                    title=child_meta.get("title", child_slug),
                    href=_href(*slugs, child_slug),
                    is_leaf=True,
                    thumbnail=_find_image(path, child_slug),
                    position=child_meta.get("position"),
                )
            )

    if len(children) > GRID_SIZE:
        raise ContentError(
            f"{context}: found {len(children)} children, max is {GRID_SIZE}"
        )

    slots = _assign_grid_positions(children, context=context)

    return Node(
        slug=slugs[-1] if slugs else "",
        title=title,
        href=_href(*slugs),
        children=slots,
    )


@lru_cache(maxsize=256)
def get_leaf(*slugs: str) -> Node:
    """Return a leaf node: a single image + text, no children. Works at any depth."""
    parent_dir = CONTENT_ROOT.joinpath(*slugs[:-1])
    leaf_slug = slugs[-1]
    meta_path = parent_dir / f"{leaf_slug}.yaml"

    if not meta_path.exists():
        raise NodeNotFoundError(f"No leaf content at '{'/'.join(slugs)}'")

    meta = _read_yaml(meta_path)
    image = _find_image(parent_dir, leaf_slug)

    return Node(
        slug=leaf_slug,
        title=meta.get("title", leaf_slug),
        href=_href(*slugs),
        image=image,
        text=meta.get("text"),
    )