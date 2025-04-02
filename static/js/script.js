document.addEventListener('DOMContentLoaded', function() {
    // DOM eles
    const symptomInput = document.getElementById('symptom-input');
    const addSymptomBtn = document.getElementById('add-symptom');
    const searchSymptomsBtn = document.getElementById('search-symptoms');
    const selectedSymptomsDiv = document.getElementById('selected-symptoms');
    const diagnoseBtn = document.getElementById('diagnose-btn');
    const diagnosisResultsDiv = document.getElementById('diagnosis-results');
    const symptomsListDiv = document.getElementById('symptoms-list');
    const diseasesListDiv = document.getElementById('diseases-list');
    const diseaseDetailsDiv = document.getElementById('disease-details');
    const searchSymptomInput = document.getElementById('search-symptom');
    
    // State
    let selectedSymptoms = [];
    
    // Tab functionality
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            this.classList.add('active');
            document.getElementById(`${this.dataset.tab}-tab`).classList.add('active');
        });
    });
    
    // Symptom selection
    addSymptomBtn.addEventListener('click', addSymptom);
    symptomInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') addSymptom();
    });
    
    function addSymptom() {
        const symptom = symptomInput.value.trim();
        if (symptom && !selectedSymptoms.includes(symptom)) {
            selectedSymptoms.push(symptom);
            updateSelectedSymptoms();
            symptomInput.value = '';
        }
    }
    
    function updateSelectedSymptoms() {
        selectedSymptomsDiv.innerHTML = selectedSymptoms.map(symptom => `
            <div class="selected-item">
                ${symptom}
                <button class="remove-btn" data-symptom="${symptom}">×</button>
            </div>
        `).join('');
        
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                selectedSymptoms = selectedSymptoms.filter(s => s !== this.dataset.symptom);
                updateSelectedSymptoms();
            });
        });
    }
    
    // Diagnosis
    diagnoseBtn.addEventListener('click', performDiagnosis);
    
    async function performDiagnosis() {
        if (selectedSymptoms.length === 0) {
            alert('Please add at least one symptom');
            return;
        }
        
        diagnoseBtn.disabled = true;
        diagnosisResultsDiv.innerHTML = '<p>Analyzing symptoms...</p>';
        
        try {
            const response = await fetch('/api/diagnose', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symptoms: selectedSymptoms })
            });
            
            const data = await response.json();
            
            if (data.diagnoses && data.diagnoses.length > 0) {
                diagnosisResultsDiv.innerHTML = `
                    <h3>Possible Diagnoses:</h3>
                    <ul class="diagnosis-list">
                        ${data.diagnoses.map(d => `
                            <li>
                                <strong>${d.name}</strong> (${d.confidence}% confidence)
                                <p>${d.description}</p>
                            </li>
                        `).join('')}
                    </ul>
                `;
            } else {
                diagnosisResultsDiv.innerHTML = '<p>No matching diseases found based on the provided symptoms.</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            diagnosisResultsDiv.innerHTML = '<p>Sorry, there was an error processing your request.</p>';
        } finally {
            diagnoseBtn.disabled = false;
        }
    }
    
    searchSymptomsBtn.addEventListener('click', loadSymptoms);
    searchSymptomInput.addEventListener('input', loadSymptoms);
    
    async function loadSymptoms() {
        const searchTerm = searchSymptomInput.value.trim();
        const url = searchTerm ? `/api/symptoms?search=${encodeURIComponent(searchTerm)}` : '/api/symptoms';
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            symptomsListDiv.innerHTML = data.symptoms.map(symptom => `
                <div class="list-item">
                    ${symptom}
                    <button class="add-from-list" data-symptom="${symptom}">Add</button>
                </div>
            `).join('');
            
            document.querySelectorAll('.add-from-list').forEach(btn => {
                btn.addEventListener('click', function() {
                    if (!selectedSymptoms.includes(this.dataset.symptom)) {
                        selectedSymptoms.push(this.dataset.symptom);
                        updateSelectedSymptoms();
                    }
                });
            });
        } catch (error) {
            console.error('Error loading symptoms:', error);
        }
    }
    
    async function loadDiseases() {
        try {
            const response = await fetch('/api/diseases');
            const data = await response.json();
            
            diseasesListDiv.innerHTML = data.diseases.map(disease => `
                <div class="list-item disease-item" data-disease="${disease}">
                    ${disease}
                </div>
            `).join('');
            
            document.querySelectorAll('.disease-item').forEach(item => {
                item.addEventListener('click', async function() {
                    const diseaseName = this.dataset.disease;
                    try {
                        const response = await fetch(`/api/disease/${encodeURIComponent(diseaseName)}`);
                        const data = await response.json();
                        
                        diseaseDetailsDiv.innerHTML = `
                            <h3>${data.name}</h3>
                            <p><strong>Description:</strong> ${data.description}</p>
                            
                            <h4>Precautions:</h4>
                            <ul>
                                ${data.precautions.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                            
                            <h4>Symptom Patterns:</h4>
                            <ul>
                                ${data.symptom_patterns.map(pattern => `
                                    <li>${pattern.join(', ')}</li>
                                `).join('')}
                            </ul>
                        `;
                    } catch (error) {
                        console.error('Error loading disease details:', error);
                    }
                });
            });
        } catch (error) {
            console.error('Error loading diseases:', error);
        }
    }
    
    loadSymptoms();
    loadDiseases();
});