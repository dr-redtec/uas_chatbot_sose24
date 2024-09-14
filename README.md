# Chatbot zur Mülltrennung in Frankfurt am Main

Diese Dokumentation beschreibt die Entwicklung und Implementierung eines Chatbots zur Mülltrennung in Frankfurt am Main unter Verwendung des Retrieval-Augmented Generation (RAG)-Algorithmus. Ziel dieses Projekts war es, einen Chatbot zu entwickeln, der den Nutzern präzise und verlässliche Informationen zur Mülltrennung liefert.

## Zielsetzung

Der Chatbot verwendet den RAG-Algorithmus, um in Echtzeit auf externe Datenquellen zuzugreifen und Nutzern aktuelle Informationen bereitzustellen, wie z. B. die Öffnungszeiten der Frankfurter Entsorgungsbetriebe (FES) über eine API. Das Projekt stellt die Vorteile und Herausforderungen bei der Implementierung des RAG-Systems vor und bietet Lösungsansätze für die überwundenen Schwierigkeiten. 

Zu den Highlights gehören:
- **Echtzeitdatenzugriff**: Abrufen der aktuellen FES-Öffnungszeiten.
- **Modellwahl**: Detaillierte Erklärungen zur Auswahl des richtigen Modells.
- **Live-Demo**: Eine interaktive Demo des Chatbots ist verfügbar.
- **Anwendungsfälle**: Verschiedene Szenarien zeigen die Funktionsweise des Chatbots.

## Verzeichnisstruktur

- **`/data`**: Enthält die Daten, die für das Training und die Inferenz verwendet werden.
- **`/test`**: Testskripte für die verschiedenen Module und Funktionen.
- **`/archiv`**: Archivierte Skripte und alte Versionen.
- **`/ipynb`**: Notebooks, die während der Erstellung verwendet wurden.

## Hauptskripte

1. **context_enrichment_rag.py**: Skript zur Anreicherung des Kontexts für den RAG-Algorithmus.
2. **discord_bot_v1.4.py**: Implementierung des Chatbots, der auf Discord läuft.
3. **embeddings.py**: Skript für die Erstellung und Verwaltung von Text-Einbettungen.
4. **llms.py**: Logik für die Interaktion mit großen Sprachmodellen (LLMs).
5. **query_simple_rag.py**: Einfacher RAG-Query-Prozess.
6. **query_transformation_context_rag.py**: Transformiert die Anfrage im Zusammenhang mit dem Kontext.
7. **query_transformation_simple_rag.py**: Einfacher Transformationsprozess für Anfragen.
8. **deepeval_rag.py**: Evaluierungsskript für RAG (in diesem nur Simple RAG). Benötigt OPENAI KEY!
9. **Webloader und Webscrapper**: Sind erweiterungsmöglichkeiten, um APIs und Webseiten für die Chroma zu laden. Webscrapper ist bereits im Create Chroma enthalten.
10. **create_chroma.py**: Skript zur Erstellung und Verwaltung eines Chroma-Datenbank-Backends, das zur Speicherung und zum Abrufen von Einbettungen dient.

## Funktionsweise des RAG-Algorithmus

Der RAG-Algorithmus kombiniert die Leistungsfähigkeit von großen Sprachmodellen (LLMs) mit der Fähigkeit, auf externe Datenquellen zuzugreifen. Dies bietet zwei wesentliche Vorteile:
1. **Aktuelle Informationen**: Dank des Zugriffs auf APIs und externe Datenquellen können dem Nutzer stets aktuelle und präzise Informationen bereitgestellt werden.
2. **Verbesserte Genauigkeit**: Die Kombination von Textgenerierung und Abruf führt zu besseren Ergebnissen bei spezifischen Anfragen.

## Herausforderungen und Lösungen

Während der Implementierung sind verschiedene Herausforderungen aufgetreten, darunter:
- **Echtzeit-Datenverarbeitung**: Die Integration von Echtzeitdatenquellen wie der FES-API stellte Herausforderungen in der Konsistenz und Verfügbarkeit dar.
- **Modellwahl**: Die Wahl des richtigen Modells, um sowohl eine schnelle Reaktionszeit als auch Genauigkeit zu gewährleisten, war ein zentraler Aspekt des Projekts.

## Ausblick

Zukünftige Verbesserungen könnten die Erweiterung des Chatbots auf andere Städte und Mülltrennungssysteme beinhalten, sowie die Verbesserung der API-Integration für noch genauere und umfangreichere Informationen.

## Installation

1. Klone das Repository:
   ```bash
   https://github.com/dr-redtec/uas_chatbot_sose24.git

2.	Installiere die Abhängigkeiten, beachte dass die Requirements nur für die Ausführung des Bots mit den notwenigen Python Skripte im Hauptverzeichnis sind:
    pip install -r requirements.txt

3.  .env Datei erstellen und die benötigten Token hinterlegen für OPEOPENAI_API_KEYNAI, DISCORD_BOT_TOKEN, ALLOWED_GUILD_ID

4.  Sie müssen OLAMMA installieren auf Ihrem System und Llama3.1 8b und Mistral-NeMo ausführen. Änderen Sie die IP Adressen im llm.py auf ihre Lokale Adresse.

5.	Starte den Chatbot:
    python discord_bot_v1.4.py