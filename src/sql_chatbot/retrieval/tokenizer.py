import re
import unicodedata

from sql_chatbot.config import STOPWORDS

_CAMEL_BOUNDARY = re.compile(r"([a-z])([A-Z])")
_UPPER_SEQ_BOUNDARY = re.compile(r"([A-Z]+)([A-Z][a-z])")
_LETTER_NUMBER = re.compile(r"([a-zA-Z])(\d)")
_NUMBER_LETTER = re.compile(r"(\d)([a-zA-Z])")
_ID_SEPARATORS = re.compile(r"[.\-_/\\]")
_HAS_IDENTIFIER_STRUCTURE = re.compile(r"[.\-_/\\]|[a-z][A-Z]|[A-Z]{2,}[a-z]|\d[a-zA-Z]|[a-zA-Z]\d")


def _decompose_identifier(ident: str) -> list[str]:
    if not ident:
        return []
    s = _CAMEL_BOUNDARY.sub(r"\1||\2", ident)
    s = _UPPER_SEQ_BOUNDARY.sub(r"\1||\2", s)
    parts = s.split("||")
    result = []
    for part in parts:
        if not part:
            continue
        sub = _LETTER_NUMBER.sub(r"\1||\2", part)
        sub = _NUMBER_LETTER.sub(r"\1||\2", sub)
        for token in sub.split("||"):
            token = token.lower()
            if token:
                result.append(token)
    return result


def _collect_subtokens(token: str) -> list[str]:
    result = []
    if _ID_SEPARATORS.search(token):
        for part in _ID_SEPARATORS.split(token):
            if part:
                result.extend(_collect_subtokens(part))
    else:
        result.extend(_decompose_identifier(token))
    return result


class SQLTokenizer:
    def __init__(self, remove_stopwords: bool = True, keep_full_identifiers: bool = True):
        self.remove_stopwords = remove_stopwords
        self.keep_full_identifiers = keep_full_identifiers

    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        text = unicodedata.normalize("NFKC", text)
        raw_tokens = text.split()
        raw_full: list[str] = []
        decomp: list[str] = []

        for token in raw_tokens:
            if not token or token.isspace():
                continue

            token_lower = token.lower()

            if self.keep_full_identifiers:
                raw_full.append(token_lower)

            if _HAS_IDENTIFIER_STRUCTURE.search(token):
                decomp.extend(_collect_subtokens(token))

        if self.remove_stopwords:
            raw_full = [t for t in raw_full if t not in STOPWORDS or len(t) == 1]

        return raw_full + decomp
