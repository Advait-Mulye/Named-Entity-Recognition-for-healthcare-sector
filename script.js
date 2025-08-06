// Medical NER Frontend JavaScript
class MedicalNERApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSampleTexts();
    }

    bindEvents() {
        // Button events
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeText());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearText());
        document.getElementById('sample-btn').addEventListener('click', () => this.loadSampleText());
        
        // Enter key support for textarea
        document.getElementById('medical-text').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeText();
            }
        });

        // Modal close events
        document.querySelector('.modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('error-modal').addEventListener('click', (e) => {
            if (e.target.id === 'error-modal') {
                this.hideModal();
            }
        });

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }

    loadSampleTexts() {
        this.sampleTexts = [
            "Patient presents with chest pain and shortness of breath. Prescribed aspirin 100mg twice daily and scheduled for an ECG.",
            "The patient has a history of diabetes type 2 and hypertension. Current medications include metformin 500mg twice daily and lisinopril 10mg once daily. Blood pressure is elevated at 150/90 mmHg.",
            "Chief complaint: severe headache and nausea. Physical examination reveals neck stiffness. Ordered CT scan of the head and lumbar puncture. Started on IV morphine 5mg for pain control.",
            "Post-operative patient following appendectomy. Wound healing well with no signs of infection. Vital signs stable. Continue antibiotics ciprofloxacin 500mg twice daily for 7 days.",
            "Patient diagnosed with pneumonia affecting the right lung. Symptoms include fever, productive cough, and fatigue. Prescribed azithromycin 250mg daily and albuterol inhaler as needed.",
            "Routine colonoscopy performed. Polyp found in the colon and removed for biopsy. Patient tolerated the procedure well. Results pending pathology report."
        ];
    }

    loadSampleText() {
        const randomIndex = Math.floor(Math.random() * this.sampleTexts.length);
        const sampleText = this.sampleTexts[randomIndex];
        document.getElementById('medical-text').value = sampleText;
        
        // Add a subtle animation
        const textarea = document.getElementById('medical-text');
        textarea.style.background = '#e0f2fe';
        setTimeout(() => {
            textarea.style.background = '';
        }, 1000);
    }

    clearText() {
        document.getElementById('medical-text').value = '';
        this.hideResults();
        
        // Focus back to textarea
        document.getElementById('medical-text').focus();
    }

    async analyzeText() {
        const text = document.getElementById('medical-text').value.trim();
        
        if (!text) {
            this.showError('Please enter some medical text to analyze.');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Analysis failed');
            }

            this.displayResults(data);
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(data) {
        // Update statistics
        document.getElementById('total-entities').textContent = data.total_entities;
        
        const entityTypes = new Set(data.entities.map(e => e.label));
        document.getElementById('entity-types-count').textContent = entityTypes.size;

        // Display entity summary
        this.displayEntitySummary(data.summary);

        // Display detailed entities
        this.displayEntityList(data.entities);

        // Display annotated text
        this.displayAnnotatedText(data.annotated_text);

        // Show results section
        this.showResults();
    }

    displayEntitySummary(summary) {
        const summaryContainer = document.getElementById('entity-summary');
        summaryContainer.innerHTML = '';

        // Entity type colors and icons
        const entityConfig = {
            'DISEASE': { color: 'disease', icon: 'fas fa-virus' },
            'MEDICATION': { color: 'medication', icon: 'fas fa-pills' },
            'SYMPTOM': { color: 'symptom', icon: 'fas fa-thermometer-half' },
            'BODY_PART': { color: 'body-part', icon: 'fas fa-user' },
            'PROCEDURE': { color: 'procedure', icon: 'fas fa-user-md' },
            'TEST': { color: 'test', icon: 'fas fa-flask' },
            'DOSAGE': { color: 'dosage', icon: 'fas fa-prescription-bottle' }
        };

        Object.entries(summary).forEach(([entityType, entities]) => {
            if (entities.length === 0) return;

            const config = entityConfig[entityType] || { color: 'default', icon: 'fas fa-tag' };
            
            const groupElement = document.createElement('div');
            groupElement.className = `entity-group ${config.color}`;
            
            groupElement.innerHTML = `
                <div class="entity-group-title">
                    <i class="${config.icon}"></i>
                    ${entityType.replace('_', ' ')} (${entities.length})
                </div>
                <div class="entity-items">
                    ${entities.map(entity => `<span class="entity-tag">${entity}</span>`).join('')}
                </div>
            `;
            
            summaryContainer.appendChild(groupElement);
        });
    }

    displayEntityList(entities) {
        const listContainer = document.getElementById('entity-list');
        listContainer.innerHTML = '';

        if (entities.length === 0) {
            listContainer.innerHTML = '<p class="no-entities">No entities detected in the text.</p>';
            return;
        }

        // Entity type colors
        const entityColors = {
            'DISEASE': '#ef4444',
            'MEDICATION': '#3b82f6',
            'SYMPTOM': '#eab308',
            'BODY_PART': '#22c55e',
            'PROCEDURE': '#a855f7',
            'TEST': '#f97316',
            'DOSAGE': '#64748b'
        };

        entities.forEach(entity => {
            const entityElement = document.createElement('div');
            entityElement.className = 'entity-item';
            entityElement.style.borderLeftColor = entityColors[entity.label] || '#64748b';
            
            entityElement.innerHTML = `
                <div>
                    <div class="entity-text">${this.escapeHtml(entity.text)}</div>
                    <small class="entity-position">Position: ${entity.start}-${entity.end}</small>
                </div>
                <div class="entity-label" style="color: ${entityColors[entity.label] || '#64748b'}">
                    ${entity.label}
                </div>
            `;
            
            listContainer.appendChild(entityElement);
        });
    }

    displayAnnotatedText(annotatedText) {
        const container = document.getElementById('annotated-text');
        
        // The annotated text should come from the backend with proper HTML formatting
        // If it's plain text, we'll display it as-is
        container.innerHTML = annotatedText || 'No annotated text available.';
    }

    showResults() {
        const resultsSection = document.getElementById('results-section');
        resultsSection.style.display = 'block';
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }

    hideResults() {
        document.getElementById('results-section').style.display = 'none';
    }

    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
        document.getElementById('analyze-btn').disabled = true;
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
        document.getElementById('analyze-btn').disabled = false;
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').style.display = 'flex';
    }

    hideModal() {
        document.getElementById('error-modal').style.display = 'none';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Utility method to format confidence scores
    formatConfidence(confidence) {
        return confidence ? `${(confidence * 100).toFixed(1)}%` : 'N/A';
    }

    // Method to export results (optional enhancement)
    exportResults(data) {
        const exportData = {
            timestamp: new Date().toISOString(),
            originalText: data.original_text,
            totalEntities: data.total_entities,
            entities: data.entities,
            summary: data.summary
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medical-ner-results-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Method to validate text input
    validateInput(text) {
        if (!text || text.trim().length === 0) {
            return { valid: false, message: 'Please enter some text to analyze.' };
        }
        
        if (text.length < 10) {
            return { valid: false, message: 'Please enter at least 10 characters for meaningful analysis.' };
        }
        
        if (text.length > 10000) {
            return { valid: false, message: 'Text is too long. Please limit to 10,000 characters.' };
        }
        
        return { valid: true };
    }

    // Enhanced analyze method with validation
    async analyzeTextWithValidation() {
        const text = document.getElementById('medical-text').value.trim();
        const validation = this.validateInput(text);
        
        if (!validation.valid) {
            this.showError(validation.message);
            return;
        }

        await this.analyzeText();
    }

    // Method to highlight entity in original text (for future enhancement)
    highlightEntity(entityStart, entityEnd) {
        const textarea = document.getElementById('medical-text');
        textarea.focus();
        textarea.setSelectionRange(entityStart, entityEnd);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MedicalNERApp();
});

// Add some helpful keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+K to clear text
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('clear-btn').click();
    }
    
    // Ctrl+L to load sample
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        document.getElementById('sample-btn').click();
    }
});

// Add visual feedback for buttons
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'translateY(1px)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = '';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = '';
        });
    });
});

// Add auto-resize functionality to textarea
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('medical-text');
    
    function autoResize() {
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(120, textarea.scrollHeight) + 'px';
    }
    
    textarea.addEventListener('input', autoResize);
    textarea.addEventListener('paste', () => setTimeout(autoResize, 0));
});