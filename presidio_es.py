from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
import sqlite3

config = {
    "nlp_engine_name": "spacy",
    "models": [{ "lang_code": "es", "model_name": "es_core_news_sm" }]
}

provider = NlpEngineProvider(nlp_configuration=config)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
email_recognizer = EmailRecognizer(supported_language="es")
phone_recognizer = PhoneRecognizer(supported_language="es")

registry = analyzer.registry
registry.add_recognizer(email_recognizer)
registry.add_recognizer(phone_recognizer)

anonymizer = AnonymizerEngine()

with sqlite3.connect('foreign_test.db') as db:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sentences;')

    print('Analyzing...')

    for data in cursor:
        results = analyzer.analyze(text=data[1], language='es')
        anonymized = anonymizer.anonymize(text=data[1], analyzer_results=results)
        
        with open('spanish_result.txt', "a+", encoding="utf8") as f:
            f.write(f'{anonymized.text}\n\n')

    print('End!')