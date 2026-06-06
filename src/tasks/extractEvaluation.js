const axios = require('axios');

async function extractEvaluationData(task) {
    const processVariables = task.variables.getAll();
    const payload = {
        assignmentId: processVariables.assignmentId,
        client: processVariables.clientName,
        employee: {
            firstName: processVariables.empFirstName,
            lastName: processVariables.empLastName,
            id: processVariables.empId
        },
        skillsEvaluated: processVariables.ratingsArray,
        comment: processVariables.feedbackComment
    };

    try {
        const response = await axios.post('https://api.hrdtogo.de/v1/operations/evaluations/extract', payload);

        return {
            status: "extracted",
            rawDataId: response.data.id
        };
    } catch (error) {
        throw new Error(`Extraktion fehlgeschlagen: ${error.message}`);
    }
}