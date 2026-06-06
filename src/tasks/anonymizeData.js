const axios = require('axios');

async function anonymizeEvaluationData(task) {
    const rawData = task.variables.get('rawData');

    const anonymizedData = {
        timestamp: new Date().toISOString().substring(0, 7), // "2026-06
        region: mapToRegion(rawData.client),
        skills: rawData.skillsEvaluated,
        textAnalysis: cleanText(rawData.comment)
    };

    try {
        await axios.post('https://api.hrdtogo.de/v1/data-sales/pool/anonymize', anonymizedData);

        return {
            anonymized: true,
            storedAt: new Date().toISOString()
        };
    } catch (error) {
        throw new Error(`Anonymisierung fehlgeschlagen: ${error.message}`);
    }
}

function cleanText(text) {
    return text.replace(/(Herr|Frau)\s[A-Z][a-z]+/g, "Der Mitarbeiter/Die Mitarbeiterin");
}

function mapToRegion(clientString) {
    if (clientString.includes("Regensburg") || clientString.includes("München")) return "Süddeutschland";
    return "Deutschland (Überregional)";
}