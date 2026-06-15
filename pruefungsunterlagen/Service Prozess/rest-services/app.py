"""
HRDtoGo - Mock-REST-Services für den Service-Prozess (Sprint 4/5, Backlog #36)

Stellt lokale REST-Endpunkte bereit, die von den JavaScript-Tasks im BPMN
"HRDtoGo_Service-Prozess_implementiert.bpmn" per HTTP-Aufruf (java.net.http)
angesprochen werden:

  POST /api/knowledge-base               -> RPA-Bot "Lösung protokollieren" (Excel-Export / Wissensdatenbank)
  POST /api/notifications/ticket-closed  -> Fallback für "Ticket schließen", falls keine
                                             Prozessvariable "slackWebhookUrl" gesetzt ist
  POST /api/notifications/missing-info   -> simuliert Benachrichtigung "Fehlende Angaben anfordern"
  POST /api/notifications/response       -> simuliert Benachrichtigung "Antwort an Kunden senden"

Implementiert rein mit der Python-Standardbibliothek (kein pip install nötig).

Start:
    python3 app.py

Läuft standardmäßig auf http://localhost:8089
"""
import csv
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8089
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTIFICATIONS_LOG = os.path.join(BASE_DIR, "notifications.log")
KNOWLEDGE_BASE_CSV = os.path.join(BASE_DIR, "wissensdatenbank.csv")
KB_FIELDS = ["timestamp", "kundenId", "betreff", "loesung"]


def _ensure_kb_file():
    if not os.path.exists(KNOWLEDGE_BASE_CSV) or os.path.getsize(KNOWLEDGE_BASE_CSV) == 0:
        with open(KNOWLEDGE_BASE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=KB_FIELDS)
            writer.writeheader()


def _log_notification(kind, payload):
    entry = {"timestamp": datetime.now().isoformat(), "type": kind, "payload": payload}
    with open(NOTIFICATIONS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _read_notifications():
    if not os.path.exists(NOTIFICATIONS_LOG):
        return []
    with open(NOTIFICATIONS_LOG, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _read_knowledge_base():
    _ensure_kb_file()
    with open(KNOWLEDGE_BASE_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_knowledge_base_entry(data):
    _ensure_kb_file()
    row = {
        "timestamp": datetime.now().isoformat(),
        "kundenId": data.get("kundenId", ""),
        "betreff": data.get("betreff", ""),
        "loesung": data.get("loesung", ""),
    }
    with open(KNOWLEDGE_BASE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=KB_FIELDS)
        writer.writerow(row)
    return row


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def log_message(self, fmt, *args):
        print("[hrdtogo-rest] " + (fmt % args))

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self._send_json(200, {
                "service": "HRDtoGo Mock-REST-Services",
                "endpoints": [
                    "POST /api/notifications/missing-info",
                    "POST /api/notifications/response",
                    "POST /api/notifications/ticket-closed",
                    "POST /api/knowledge-base",
                    "GET  /api/knowledge-base",
                    "GET  /api/notifications",
                ],
            })
        elif self.path == "/api/knowledge-base":
            self._send_json(200, _read_knowledge_base())
        elif self.path == "/api/notifications":
            self._send_json(200, _read_notifications())
        else:
            self._send_json(404, {"status": "error", "message": "not found"})

    def do_POST(self):
        data = self._read_json_body()
        if self.path == "/api/notifications/missing-info":
            entry = _log_notification("missing-info", data)
            print(f"[Notification] Fehlende Angaben angefordert: {data}")
            self._send_json(200, {"status": "ok", "message": "Benachrichtigung 'Fehlende Angaben' versendet", "entry": entry})
        elif self.path == "/api/notifications/response":
            entry = _log_notification("response", data)
            print(f"[Notification] Antwort an Kunden gesendet: {data}")
            self._send_json(200, {"status": "ok", "message": "Antwort an Kunden versendet", "entry": entry})
        elif self.path == "/api/notifications/ticket-closed":
            entry = _log_notification("ticket-closed", data)
            print(f"[Notification] Ticket automatisch geschlossen (Fallback statt Slack-Webhook): {data}")
            self._send_json(200, {"status": "ok", "message": "Ticket-Schließung protokolliert (Slack-Webhook-Fallback)", "entry": entry})
        elif self.path == "/api/knowledge-base":
            row = _write_knowledge_base_entry(data)
            print(f"[Knowledge-Base] Lösung protokolliert: {row}")
            self._send_json(201, {"status": "ok", "message": "Lösung im Excel-Export/Wissensdatenbank protokolliert", "entry": row})
        else:
            self._send_json(404, {"status": "error", "message": "not found"})


if __name__ == "__main__":
    _ensure_kb_file()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"HRDtoGo Mock-REST-Services laufen auf http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
