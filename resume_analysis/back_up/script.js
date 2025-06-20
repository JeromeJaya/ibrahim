document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    analyzeBtn.addEventListener('click', analyzeResume);
});

let analysisResults = {};
let myChart = null;

async function analyzeResume() {
    const fileInput = document.getElementById('resume');
    const file = fileInput.files[0];

    if (!file || file.type !== 'application/pdf') {
        alert('Please upload a valid PDF file.');
        return;
    }

    const reader = new FileReader();
    reader.onload = async function (event) {
        try {
            const typedArray = new Uint8Array(event.target.result);
            const pdf = await pdfjsLib.getDocument(typedArray).promise;
            let resumeText = '';

            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const textContent = await page.getTextContent();
                resumeText += textContent.items.map(item => item.str).join(' ');
            }

            const jobMappings = {
                "python": "Software Developer",
                "javascript": "Frontend Developer",
                "sql": "Data Analyst",
                "excel": "Data Analyst",
                "html": "Web Developer",
                "react": "React Developer",
                "node.js": "Backend Developer",
                "java": "Java Developer",
                "c++": "C++ Developer",
                "aws": "Cloud Engineer"
            };

            let predictedJob = "General Position";
            const skills = [];
            const allKeywords = Object.keys(jobMappings);

            allKeywords.forEach(keyword => {
                if (resumeText.toLowerCase().includes(keyword)) {
                    skills.push(keyword);
                    predictedJob = jobMappings[keyword] || predictedJob;
                }
            });

            analysisResults = {
                jobTitle: predictedJob,
                skills: [...new Set(skills)],
                rawText: resumeText
            };

            displayResults();
        } catch (error) {
            console.error("Error analyzing PDF:", error);
            document.getElementById('predictions-output').innerHTML = 
                <p style="color: red;">Error analyzing resume: ${error.message}</p>;
        }
    };

    reader.readAsArrayBuffer(file);
}

function displayResults() {
    const outputDiv = document.getElementById('predictions-output');
    outputDiv.innerHTML = `
        <h3>Analysis Results</h3>
        <p><strong>Suggested Position:</strong> ${analysisResults.jobTitle}</p>
        <p><strong>Identified Skills:</strong></p>
        <ul>${analysisResults.skills.map(skill => 
            <li>${skill.charAt(0).toUpperCase() + skill.slice(1)}</li>
        ).join('')}</ul>
    `;

    if (analysisResults.skills.length > 0) {
        generateChart(analysisResults.skills);
        document.getElementById('chart-container').style.display = 'block';
    }
}

function generateChart(skills) {
    const ctx = document.getElementById('chart').getContext('2d');

    if (myChart) {
        myChart.destroy();
    }

    const proficiencyData = skills.map(() => Math.floor(Math.random() * 40) + 60);

    myChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: skills,
            datasets: [{
                label: 'Skill Proficiency',
                data: proficiencyData,
                backgroundColor: 'rgba(0, 64, 128, 0.2)',
                borderColor: '#004080',
                pointBackgroundColor: '#004080',
                pointBorderColor: '#fff',
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}