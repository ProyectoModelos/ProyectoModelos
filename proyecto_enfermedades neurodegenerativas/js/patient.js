// patient.js

const vertices = [
    'PEM', 'DES', 'LEN', 'MOF', 'REM', 'JUI', 'CAM', 'PER',
    'PRO', 'PAR', 'DEL', 'DEP', 'ANS', 'AGI', 'ALI', 'INS',
    'INA', 'INM', 'INF'
];

const symptomsInfo = {
    'PEM': 'Pérdida de memoria leve',
    'DES': 'Desorientación en tiempo y lugar',
    'LEN': 'Lenguaje afectado',
    'MOF': 'Problemas motores finos',
    'REM': 'Dificultad para realizar tareas familiares',
    'JUI': 'Juicio deteriorado',
    'CAM': 'Cambios de humor y comportamiento',
    'PER': 'Pérdida de habilidades sociales',
    'PRO': 'Problemas de coordinación',
    'PAR': 'Paranoia y desconfianza',
    'DEL': 'Delirios',
    'DEP': 'Depresión',
    'ANS': 'Ansiedad',
    'AGI': 'Agitación',
    'ALI': 'Pérdida de apetito',
    'INS': 'Insomnio',
    'INA': 'Incapacidad para comunicarse',
    'INM': 'Inmovilidad',
    'INF': 'Incontinencia'
};

function calculateProgress() {
    const patientName = document.getElementById('patientName').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;

    const selectedSymptoms = document.querySelectorAll('input[name="symptom"]:checked');
    let highestVertexIndex = -1;
    let selectedSymptomsText = [];

    selectedSymptoms.forEach(symptom => {
        const index = vertices.indexOf(symptom.value);
        if (index > highestVertexIndex) {
            highestVertexIndex = index;
        }
        selectedSymptomsText.push(symptomsInfo[symptom.value]);
    });

    const percentage = ((highestVertexIndex + 1) / vertices.length) * 100;

    // Determinar el estado de la enfermedad y recomendaciones basado en el porcentaje
    let diseaseStage = "";
    let recommendations = "";

    if (percentage <= 20) {
        diseaseStage = "Etapa Preclínica o Asintomática";
        recommendations = `
            <ul>
                <li><b>Detección temprana:</b> Evaluación del riesgo: Pregunta sobre antecedentes familiares de Alzheimer u otras demencias, historial de traumas craneales, y factores de riesgo cardiovasculares (hipertensión, diabetes, colesterol alto).</li>
                <li><b>Pruebas cognitivas:</b> Considera el uso de herramientas de cribado cognitivo (como el Mini-Mental State Examination o el Montreal Cognitive Assessment) para establecer una línea de base cognitiva, aunque los pacientes pueden no presentar síntomas todavía.</li>
                <li><b>Educación sobre la enfermedad:</b> Informa al paciente sobre los factores de riesgo modificables y las medidas preventivas, como el ejercicio regular, la dieta mediterránea, la estimulación cognitiva y el control de enfermedades crónicas.</li>
            </ul>`;
    } else if (percentage <= 40) {
        diseaseStage = "Etapa Leve";
        recommendations = `
            <ul>
                <li><b>Evaluación clínica:</b> Entrevista detallada: Investiga sobre problemas recientes de memoria, dificultad para encontrar palabras o desorientación en lugares conocidos. Verifica con un miembro de la familia o cuidador para obtener una visión completa.</li>
                <li><b>Pruebas cognitivas:</b> Administra pruebas más detalladas (como el Test de las 7 palabras, pruebas de fluidez verbal) para evaluar la memoria reciente, la atención, y las funciones ejecutivas.</li>
                <li><b>Intervenciones iniciales:</b> Tratamiento farmacológico: Considera iniciar inhibidores de la colinesterasa si no hay contraindicaciones. Explica al paciente y a la familia que estos medicamentos pueden ralentizar la progresión de los síntomas.</li>
            </ul>`;
    } else if (percentage <= 60) {
        diseaseStage = "Etapa Moderada";
        recommendations = `
            <ul>
                <li><b>Evaluación funcional:</b> Valoración del estado funcional: Evalúa la capacidad del paciente para realizar actividades de la vida diaria (AVD), como la higiene personal, la alimentación, y la gestión financiera. Usa escalas como el Índice de Barthel.</li>
                <li><b>Plan de manejo:</b> Tratamiento farmacológico combinado: Introduce memantina para pacientes con síntomas moderados, en combinación con un inhibidor de la colinesterasa si es necesario.</li>
                <li><b>Apoyo al cuidador:</b> Asesora a los cuidadores sobre la carga emocional y física de la enfermedad, y ofrece recursos locales como grupos de apoyo, programas de respiro, y orientación legal.</li>
            </ul>`;
    } else if (percentage <= 80) {
        diseaseStage = "Etapa Moderadamente Grave";
        recommendations = `
            <ul>
                <li><b>Evaluación de seguridad:</b> Riesgo de caídas y deambulación: Evalúa el riesgo de caídas y comportamientos erráticos, como la deambulación, y sugiere medidas de seguridad en el hogar, como barreras en escaleras y puertas con cerraduras especiales.</li>
                <br><li><b>Desnutrición e hidratación:</b> Revisa la capacidad del paciente para alimentarse e hidratarse adecuadamente, ya que estos problemas son comunes en esta etapa.</li></br>
                <br><li><b>Intervenciones específicas:</b> Manejo de síntomas graves: Si los síntomas conductuales son severos, considera el uso de medicamentos antipsicóticos en dosis bajas, siempre pesando los riesgos y beneficios.</li></br>
            </ul>`;
    } else if (percentage <= 100) {
        diseaseStage = "Etapa Grave o Terminal";
        recommendations = `
            <ul>
                <li><b>Evaluación final:</b> Estado general: Evalúa el estado general del paciente, enfocado en el confort, la presencia de dolor, y otros síntomas como úlceras por presión o infecciones.</li>
                <li><b>Cuidados paliativos:</b> Prioriza la comodidad del paciente, con un enfoque en el manejo del dolor, la higiene, y la nutrición a través de técnicas que no causen incomodidad.</li>
                <li><b>Decisiones al final de la vida:</b> Facilita discusiones sobre las preferencias al final de la vida, incluida la reanimación, la alimentación artificial, y otras intervenciones invasivas.</li>
            </ul>`;
    }

    const resultText = highestVertexIndex >= 0
        ? `El paciente ${patientName} (${gender}, ${age}) está en el ${percentage.toFixed(2)}% de progresión de la enfermedad. (${diseaseStage})`
        : "No se han seleccionado síntomas.";

    let report = `
        <p>${resultText}</p>
        <h3>Síntomas seleccionados:</h3>
        <ul>`;
    selectedSymptomsText.forEach(symptom => {
        report += `<li>${symptom}</li>`;
    });
    report += `
        </ul>
        <h3>Recomendaciones:</h3>
        ${recommendations}`;

    document.getElementById('result').innerHTML = report;
}

function registerPatient() {
    alert('Paciente registrado exitosamente.');
    window.location.href = 'index.html'; // Redirigir al index.html después del registro
}

function showSymptomInfo() {
    let symptomsList = "<h2>Información de Síntomas</h2><ul>";
    for (const [key, value] of Object.entries(symptomsInfo)) {
        symptomsList += `<li>${key}: ${value}</li>`;
    }
    symptomsList += "</ul>";
    alert(symptomsList);
}
