class Language:
    def __init__(self, lang_code, api_lang, direct_mapping):
        self.lang_code = lang_code
        self.api_lang = api_lang
        self.direct_mapping = direct_mapping

    def __repr__(self):
        return f"Language(lang_code={self.lang_code}, api_lang={self.api_lang}, direct_mapping={self.direct_mapping})"