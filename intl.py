from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer, IpRecognizer, CreditCardRecognizer
from presidio_anonymizer import AnonymizerEngine
from langdetect import detect
import sqlite3

# Define supported languages and their SpaCy models
SUPPORTED_LANGUAGES = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
    "nl": "nl_core_news_sm"
}

# Fallback for regex-based recognizers
regex_recognizers = []


print('Setting up regex recognizers ...')
for lang in SUPPORTED_LANGUAGES.keys():
    regex_recognizers.extend([
        EmailRecognizer(supported_language=lang),
        PhoneRecognizer(supported_language=lang),
        IpRecognizer(supported_language=lang),
        CreditCardRecognizer(supported_language=lang)
    ])
print('Finished regex recognizers setup!')

def setup_nlp_engine() -> NlpEngine:
    print('Setting up nlp engine ...')
    config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": lang_code, "model_name": SUPPORTED_LANGUAGES[lang_code]} for lang_code in SUPPORTED_LANGUAGES.keys()],
    }

    provider = NlpEngineProvider(nlp_configuration=config)
    print('Nlp engine setup finished!')
    return provider.create_engine()


def setup_analyzer() -> AnalyzerEngine:
    print('Setting up analyzer ...')
    nlp_engine = setup_nlp_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    # Register regex recognizers (language-agnostic)
    for recognizer in regex_recognizers:
        analyzer.registry.add_recognizer(recognizer)

    print('Finished analyzer setup!')
    return analyzer


# === Example Usage ===
# Setup
analyzer = setup_analyzer()
anonymizer = AnonymizerEngine()

# Input text
def redactor(text: str) -> str:
    user_lang = detect(text=text)

    if user_lang not in SUPPORTED_LANGUAGES.keys():
        print('Language not supported. Fallback to EN')
        user_lang = 'en'

    results = analyzer.analyze(text=text, language=user_lang)
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text


with sqlite3.connect('foreign_test.db') as db:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sentences;')

    print('Analysis started ...')

    with open('foreign_result.txt', 'w+', encoding="utf8") as f:
        for data in cursor:
            f.write(f'{redactor(data[1])}\n\n')

    print('Analysis finished ...')