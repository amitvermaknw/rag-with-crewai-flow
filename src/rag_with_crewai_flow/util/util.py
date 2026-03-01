import re
from nanoid import generate

class Util:
    def generate_slug(title: str, id: str) -> str:
        trimmed_title = ' '.join(title.split()[:60])
        clean_title = trimmed_title.lower()
        clean_title = re.sub(r'[*+~.()\'"!:@]', '', clean_title)
        clean_title = re.sub(r'[^\w\s-]', '', clean_title)
        clean_title = re.sub(r'\s+', '-', clean_title).strip('-')
        
        return f"{clean_title}--{id}"


    def slug_id() -> str:
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        return generate(alphabet, 12)