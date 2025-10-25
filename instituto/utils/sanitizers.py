import bleach

ALLOWED_TAGS = [
    'p','br','strong','em','ul','ol','li','h1','h2','h3','blockquote',
    'pre','code','a','img','figure','figcaption','table','thead','tbody','tr','th','td'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id'],
    'a': ['href', 'title', 'target', 'rel', 'class'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'srcset', 'loading', 'class'],
    'table': ['class'],
    'th': ['scope']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

cleaner = bleach.Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRIBUTES,
    protocols=ALLOWED_PROTOCOLS,
    strip=True,
    strip_comments=True
)


def clean_html(value: str) -> str:
    if not value:
        return ''
    return cleaner.clean(value)
