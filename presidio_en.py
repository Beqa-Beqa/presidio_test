from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import sqlite3

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

with sqlite3.connect('test.db') as db:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sentences;')

    print('Analyzing...')

    for data in cursor:
        results = analyzer.analyze(text=data[1], language='en')
        anonymized = anonymizer.anonymize(text=data[1], analyzer_results=results)
        
        with open('english_result.txt', "a+", encoding="utf8") as f:
            f.write(f'{anonymized.text}\n\n')

    print('End!')