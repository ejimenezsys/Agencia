"""Publica localmente un artículo ya aprobado; no hace push ni despliega."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from database import BlogPost, SessionLocal, init_db
from editorial import PUBLISHED_DIR
from editorial_workflow import validate


def publish(source: Path) -> Path:
    post = json.loads(source.read_text(encoding="utf-8"))
    errors = validate(post, publish=True)
    if errors:
        raise ValueError("No publicable: " + "; ".join(errors))
    post["status"] = "published"
    post.setdefault("published_at", datetime.now(timezone.utc).isoformat())
    post.setdefault("image_url", "/static/logo_prosper_ia_cropped.jpg")

    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    destination = PUBLISHED_DIR / f"{post['slug']}.json"
    destination.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    init_db()
    db = SessionLocal()
    try:
        row = db.query(BlogPost).filter(BlogPost.slug == post["slug"]).first()
        values = {
            "title": post["title"], "category": post["lane"], "summary": post["summary"],
            "content": post["content"], "image_url": post["image_url"],
            "published_at": post["published_at"], "author": post["author"],
        }
        if row is None:
            row = BlogPost(slug=post["slug"], **values)
            db.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)
        db.commit()
    finally:
        db.close()
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica un artículo aprobado en la copia local")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(publish(args.file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
