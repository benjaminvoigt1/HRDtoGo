# Technische Spezifikation: REST-Service-Tasks (Sprint 4)

**Verantwortlich für die Definition:** Elif Kurtcuoglu  
**Zielgruppe für die Implementierung:** Benjamin Voigt 

Diese Dokumentation beschreibt die drei externen REST-Schnittstellen, die über JavaScript-Tasks in die Camunda-Workflow-Engine eingebunden werden, um die Mindestanforderungen an die technische Komplexität und den externen Datenaustausch zu erfüllen.

---

## 1. Service-Task: ST_Wertschöpfung_Adresse_Prüfen

* **Zugehöriger Prozess:** Prozess 2 (Wertschöpfung / Mitarbeitervermittlung)
* **Schnittstellen-Anbieter:** OpenStreetMap (Nominatim API)
* **Fachliches Ziel:** Automatische Validierung des vom Industriekunden eingegebenen Einsatzortes, um Fehldispositionen von Handwerkern zu verhindern.
* **HTTP-Methode:** `GET`
* **Request-URL:** `https://nominatim.openstreetmap.org/search?q=${einsatzOrt}&format=json`
* **Header:**
    * `User-Agent: HRDtoGo-Camunda-App/1.0`
    * `Accept: application/json`

### Variablen-Mapping
| Richtung | Variablenname (Camunda) | Typ | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Input** | `einsatzOrt` | String | Die vom Kunden eingegebene Adresse/Stadt. |
| **Output** | `is_address_valid` | Boolean | `true`, wenn die Adresse existiert, sonst `false`. |


## 2. Service-Task: ST_Auftrag_Rechnung_Senden

* **Zugehöriger Prozess:** Prozess 3 (Auftrag/Bestellung / Datenverkauf)
* **Schnittstellen-Anbieter:** Mailgun API
* **Fachliches Ziel:** Vollautomatisierter Rechnungsversand per E-Mail nach erfolgreicher Bereitstellung des Datenpakets (Prozessschritt 12).
* **HTTP-Methode:** `POST`
* **Request-URL:** `https://api.mailgun.net/v3/sandbox-your-domain.mailgun.org/messages`
* **Header:**
  * `Authorization: Basic [BASE64_ENCODED_API_KEY]`
  * `Content-Type: application/x-www-form-urlencoded`

### Variablen-Mapping
| Richtung | Variablenname (Camunda) | Typ | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Input** | `kundenEmail` | String | E-Mail-Adresse des Kunden (z. B. des Ausbilders). |
| **Input** | `kundenName` | String | Name des Kunden für die persönliche Anrede. |
| **Input** | `rechnungs_betrag` | Double | Der zu zahlende Gesamtbetrag. |
| **Input** | `kundenId` | String | Eindeutige ID des Kunden zur Zuordnung. |
| **Output** | `mail_status_code` | Integer | HTTP-Status (z. B. 200 = Erfolgreich gesendet). |

## 3. Service-Task: ST_Service_Eskalation_Slack

* **Zugehöriger Prozess:** Prozess 4 (Service / Support & Reklamation)
* **Schnittstellen-Anbieter:** Slack (Incoming Webhooks)
* **Fachliches Ziel:** Sofortige Alarmierung der Teamleitung über einen dedizierten Slack-Channel, wenn ein Support-Fall eskaliert wird (Gateway "Eskalation notwendig = Ja").
* **HTTP-Methode:** `POST`
* * **Request-URL:** `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`
* **Header:**
  * `Content-Type: application/json`

### Variablen-Mapping
| Richtung | Variablenname (Camunda) | Typ | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Input** | `kundenId` | String | Die betroffene Kundennummer. |
| **Input** | `betreff` | String | Thema oder Titel der Reklamation / Störung. |
| **Input** | `beschreibung` | String | Detailbeschreibung des Problems durch den Kunden. |
| **Input** | `prioritaet` | String | Dringlichkeitsstufe (Hoch, Mittel, Niedrig). |
| **Output** | `slack_response` | String | Antwort des Slack-Servers (z. B. "ok"). |