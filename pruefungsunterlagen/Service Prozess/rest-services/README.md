# HRDtoGo – Mock-REST-Services (Service-Prozess)

Diese kleine Anwendung (reine Python-Standardbibliothek, kein pip-Setup
nötig) stellt die lokalen REST-Endpunkte bereit, die in
`HRDtoGo_Service-Prozess_implementiert.bpmn` über JavaScript-Tasks
(scriptTask / ExecutionListener, `java.net.http.HttpClient`) angesprochen
werden (Sprint-4-Backlog #36 – "REST-Anbindungen implementieren, mind. 3
Services").

## Voraussetzung

Python 3.8 oder neuer (keine zusätzlichen Pakete erforderlich).

## Starten

```bash
cd rest-services
python3 app.py
```

Die Services laufen danach unter `http://localhost:8089`.

## Endpunkte

| Methode | Pfad | Verwendet von (BPMN-Task) | Zweck |
|---|---|---|---|
| POST | `/api/knowledge-base` | "Lösung protokollieren" (scriptTask, RPA-Bots) | Schreibt die Lösung in `wissensdatenbank.csv` (entspricht dem Excel-Export) |
| GET | `/api/knowledge-base` | – | Zeigt alle protokollierten Lösungen |
| POST | `/api/notifications/ticket-closed` | "Ticket schließen" (scriptTask) | Fallback, falls keine Prozessvariable `slackWebhookUrl` gesetzt ist |
| POST | `/api/notifications/missing-info` | – | Simuliert Benachrichtigung bei fehlenden Angaben |
| POST | `/api/notifications/response` | – | Simuliert Versand einer fachlichen Antwort an den Kunden |
| GET | `/api/notifications` | – | Zeigt alle versendeten Benachrichtigungen |

Externe Anbindungen (nicht Teil dieses Mock-Servers, siehe Setup-Dokumentation
Kap. 4):

- **GitHub Search Issues API** (`api.github.com/search/issues`, öffentlich,
  kein Token nötig) – wird vom ExecutionListener auf "Anfrage klassifizieren"
  zur Suche nach bekannten Fehlern aufgerufen (Prozessvariable `githubRepo`).
- **Slack Incoming Webhook** – wird vom scriptTask "Ticket schließen"
  genutzt, falls die Prozessvariable `slackWebhookUrl` gesetzt ist.

Alle eingehenden Aufrufe an diesen Mock-Server werden zusätzlich in der
Konsole ausgegeben und in `notifications.log` bzw. `wissensdatenbank.csv`
gespeichert – so lässt sich ein Testlauf des Service-Prozesses in Camunda
direkt nachvollziehen.
