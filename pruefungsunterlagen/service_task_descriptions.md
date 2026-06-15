

## 1. Service-Task: ST_Wertschöpfung_Adresse_Prüfen

* **Zugehöriger Prozess:** Prozess 2 (Wertschöpfung / Mitarbeitervermittlung)
* **Schnittstellen-Anbieter:** OpenStreetMap (Nominatim API)
* **Fachliches Ziel:** Automatische Validierung des vom Industriekunden eingegebenen Einsatzortes, um Fehldispositionen von Handwerkern zu verhindern.
* **HTTP-Methode:** `GET`
* **Request-URL:** `https://nominatim.openstreetmap.org/search?q=${encodedEinsatzOrt}&format=json&email=it-betrieb@hrdtogo.de`
* **Header:**
    * `User-Agent: HRDtoGo-Camunda-App/1.0`
    * `Accept: application/json`


Vor dem Absenden des Requests muss die Camunda-Variable `einsatzOrt` per JavaScript URL-encoded werden:
```javascript
var encodedEinsatzOrt = encodeURIComponent(execution.getVariable("einsatzOrt"));
execution.setVariable("encodedEinsatzOrt", encodedEinsatzOrt);

```

### Variablen-Mapping

| Richtung | Variablenname (Camunda) | Typ | Beschreibung |
| --- | --- | --- | --- |
| **Input** | `encodedEinsatzOrt` | String | Die URL-konform maskierte Adresse des Einsatzortes. |
| **Output** | `is_address_valid` | Boolean | `true`, wenn die Adresse existiert (Array-Länge > 0), sonst `false`. |
| **Output** | `api_success` | Boolean | `true`, wenn der API-Aufruf erfolgreich war (HTTP 200), sonst `false`. |
| **Output** | `api_error_message` | String | Enthält im Fehlerfall die Details zum HTTP-Fehler oder Timeout. |

---

## 2. Service-Task: ST_Auftrag_Rechnung_Senden

* **Zugehöriger Prozess:** Prozess 3 (Auftrag/Bestellung / Datenverkauf)
* **Schnittstellen-Anbieter:** Mailgun API
* **Fachliches Ziel:** Vollautomatisierter Rechnungsversand per E-Mail direkt nach der erfolgreichen Genehmigung und Erstellung der Rechnung (vor der Datenbereitstellung).
* **HTTP-Methode:** `POST`
* **Request-URL:** `https://api.mailgun.net/v3/sandbox-your-domain.mailgun.org/messages`
* **Header:**
* `Authorization: Basic [BASE64_ENCODED_API_KEY]`
* `Content-Type: application/x-www-form-urlencoded`



### Entwickler-Hinweis zur Formatierung:

Der `rechnungs_betrag` (Double) muss für den E-Mail-Text in einen sauberen String im Format `"XX,XX EUR"` konvertiert werden, um länderspezifische Formatierungsfehler der JavaScript-Engine zu vermeiden.

### Variablen-Mapping

| Richtung      | Variablenname (Camunda) | Typ | Beschreibung |
|---------------| --- | --- | --- |
| **Input**     | `kundenEmail` | String | E-Mail-Adresse des Kunden (z. B. des Ausbilders). |
| **Input**     | `kundenName` | String | Name des Kunden für die persönliche Anrede. |
| **Input**     | `rechnungs_betrag` | Double | Der zu zahlende Gesamtbetrag (interner numerischer Wert). |
| **Input**     | `kundenId` | String | Eindeutige ID des Kunden zur Zuordnung. |
| **Output**    | `mail_status_code` | Integer | HTTP-Status (z. B. 200 = Erfolgreich gesendet). |
| **Output** °° | `api_success` | Boolean | `true`, wenn die Mail übermittelt wurde, bei 4xx/5xx-Fehlern `false`. |
| **Output**    | `api_error_message` | String | Fehlermeldung der Mailgun API im Falle einer Ablehnung. |

---

## 3. Service-Task: ST_Service_Eskalation_Slack

* **Zugehöriger Prozess:** Prozess 4 (Service / Support & Reklamation)
* **Schnittstellen-Anbieter:** Slack (Incoming Webhooks)
* **Fachliches Ziel:** Sofortige Alarmierung der Teamleitung über einen dedizierten Slack-Channel, wenn ein Support-Fall eskaliert wird (Gateway "Eskalation notwendig = Ja").
* **HTTP-Methode:** `POST`
* **Request-URL:** `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`
* **Header:**
* `Content-Type: application/json`



### Variablen-Mapping

| Richtung | Variablenname (Camunda) | Typ | Beschreibung |
| --- | --- | --- | --- |
| **Input** | `kundenId` | String | Die betroffene Kundennummer. |
| **Input** | `betreff` | String | Thema oder Titel der Reklamation / Störung. |
| **Input** | `beschreibung` | String | Detailbeschreibung des Problems durch den Kunden. |
| **Input** | `prioritaet` | String | Dringlichkeitsstufe (Hoch, Mittel, Niedrig). |
| **Output** | `slack_response` | String | Antwort des Slack-Servers (z. B. "ok"). |
| **Output** | `api_success` | Boolean | `true`, wenn der Webhook erfolgreich getriggert wurde, sonst `false`. |
| **Output** | `api_error_message` | String | Enthält im Fehlerfall die Details zum HTTP-Fehler von Slack. |


### Was verändert wurde: 
Fehler 1 (Ablauf): Rechnungsversand zeitlich vor die Datenbereitstellung verschoben wie im BPMN-Modell.

Fehler 2 (API-Richtlinie): E-Mail-Parameter bei OpenStreetMap ergänzt, um Blockaden zu verhindern.

Fehler 3 (Syntax): JavaScript mit encodeURIComponent() eingefügt, damit Sonder- und Leerzeichen in der URL nicht zum Absturz führen.

Fehler 4 (Datentyp): Hinweis zur Konvertierung des Double-Rechnungsbetrags in einen sauberen Text-String  für Mailgun hinzugefügt.

Fehler 5 (Fehlerhandling): Bei allen Tasks die Outputs api_success und api_error_message ergänzt, um Camunda-Abstürze bei API-Ausfällen zu verhindern.

```
