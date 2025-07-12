// Debounce function
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Initialize autocomplete for medication search
function initializeMedicationSearch(inputId, dropdownId) {
    const searchInput = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    // Exit early if required elements are missing
    if (!searchInput || !dropdown) {
        console.warn(`Autocomplete initialization skipped: Missing elements for inputId=${inputId}, dropdownId=${dropdownId}`);
        return;
    }

    const detailsDiv = document.getElementById('medication-details');
    const dosageInput = document.getElementById('dosage');
    const frequencyInput = document.getElementById('frequency');
    const notesInput = document.getElementById('notes');
    const formInput = document.getElementById('form');
    const commonUsesInput = document.getElementById('common_uses');
    let currentMedications = [];
    let selectedIndex = -1;

    // Fetch medications
    const searchMedications = debounce(async (query) => {
        if (query.length < 2) {
            hideDropdown();
            if (detailsDiv) detailsDiv.innerHTML = '';
            return;
        }
        try {
            const response = await fetch(`/api/medication-suggestions?term=${encodeURIComponent(query)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) {
                console.error('Error fetching suggestions:', response.status);
                hideDropdown();
                if (detailsDiv) detailsDiv.innerHTML = '';
                return;
            }
            const data = await response.json();
            currentMedications = data;
            showDropdown();
        } catch (error) {
            console.error('Fetch error:', error);
            hideDropdown();
            if (detailsDiv) detailsDiv.innerHTML = '';
        }
    }, 300);

    // Show dropdown
    function showDropdown() {
        dropdown.innerHTML = '';
        selectedIndex = -1;
        if (currentMedications.length === 0) {
            hideDropdown();
            return;
        }

        const header = document.createElement('div');
        header.className = 'dropdown-header';
        header.innerHTML = `<i class="fas fa-search me-2"></i>Found ${currentMedications.length} medication${currentMedications.length !== 1 ? 's' : ''}`;
        dropdown.appendChild(header);

        currentMedications.forEach((med, index) => {
            const item = document.createElement('div');
            item.className = 'dropdown-item medication-suggestion';
            item.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-pills text-primary me-3"></i>
                    <div class="flex-grow-1">
                        <div class="fw-semibold">${med.name}</div>
                        <small class="text-muted">${med.common_uses || 'No condition specified'}</small>
                        ${med.dosage ? `<small class="text-info d-block">Default: ${med.dosage}${med.frequency ? ` ${med.frequency}` : ''}</small>` : ''}
                    </div>
                    <i class="fas fa-arrow-right text-muted"></i>
                </div>
            `;
            item.addEventListener('click', () => {
                selectMedication(index);
            });
            dropdown.appendChild(item);
        });
        dropdown.style.display = 'block';
    }

    // Hide dropdown
    function hideDropdown() {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        selectedIndex = -1;
    }

    // Select medication
    function selectMedication(index) {
        const med = currentMedications[index];
        if (med) {
            searchInput.value = med.name;

            if (detailsDiv) {
                detailsDiv.style.display = 'block';
                const detailsContent = document.getElementById('details-content');
                if (detailsContent) {
                    detailsContent.innerHTML = `
                        <div class="row">
                            <div class="col-md-6">
                                <strong>${med.name}</strong>
                                ${med.form ? `<br><small class="text-muted">Form: ${med.form}</small>` : ''}
                                ${med.common_uses ? `<br><small class="text-muted">Used for: ${med.common_uses}</small>` : ''}
                            </div>
                            <div class="col-md-6">
                                ${med.dosage ? `<small class="text-muted">Suggested dosage: ${med.dosage}</small><br>` : ''}
                                ${med.frequency ? `<small class="text-muted">Suggested frequency: ${med.frequency}</small>` : ''}
                            </div>
                        </div>
                    `;
                }
            }

            if (dosageInput) dosageInput.value = med.dosage || '';
            if (frequencyInput) frequencyInput.value = med.frequency || '';
            if (notesInput) notesInput.value = med.notes || '';
            if (formInput) formInput.value = med.form || '';
            if (commonUsesInput) commonUsesInput.value = med.common_uses || '';

            searchInput.classList.add('is-valid');
            setTimeout(() => {
                searchInput.classList.remove('is-valid');
            }, 2000);

            hideDropdown();
        }
    }

    // Clear medication details
    function clearMedicationDetails() {
        if (detailsDiv) {
            detailsDiv.style.display = 'none';
        }
        searchInput.classList.remove('is-valid');
    }

    // Input event
    searchInput.addEventListener('input', (e) => {
        const value = e.target.value;
        if (value.length < 2) {
            clearMedicationDetails();
        }
        searchMedications(value);
    });

    // Keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
        if (!dropdown) return;
        const items = dropdown.getElementsByClassName('dropdown-item');
        if (!items || items.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelection(items);
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            selectMedication(selectedIndex);
        } else if (e.key === 'Escape') {
            hideDropdown();
            if (detailsDiv) detailsDiv.style.display = 'none';
        }
    });

    // Update selected item
    function updateSelection(items) {
        if (!items || items.length === 0) return;
        for (let i = 0; i < items.length; i++) {
            if (items[i]) {
                items[i].classList.remove('selected');
                if (i === selectedIndex) {
                    items[i].classList.add('selected');
                    items[i].scrollIntoView({ block: 'nearest' });
                }
            }
        }
    }

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (!searchInput || !dropdown || !e.target) return;
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            hideDropdown();
            if (detailsDiv) detailsDiv.style.display = 'none';
        }
    });
}

// Frequency preset times configuration
const FREQUENCY_PRESETS = {
    'once-daily': ['07:00'],
    'twice-daily': ['07:00', '19:00'],
    'three-times-daily': ['07:00', '13:00', '19:00'],
    'four-times-daily': ['07:00', '12:00', '16:00', '20:00'],
    'as-needed': []
};

// Initialize medication frequency functionality
function initializeMedicationFrequency() {
    const frequencyButtons = document.querySelectorAll('.frequency-btn');
    const frequencyInput = document.getElementById('frequency');
    const timePickersContainer = document.getElementById('time-pickers-container');
    const timeInputsContainer = document.getElementById('time-inputs');

    // Frequency button mappings
    const frequencyMap = {
        'once-daily': 'Daily',
        'twice-daily': 'Twice daily',
        'three-times-daily': 'Three times daily',
        'four-times-daily': 'Four times daily',
        'as-needed': 'As needed'
    };

    // Check if required elements exist
    if (!frequencyButtons.length || !frequencyInput || !timePickersContainer || !timeInputsContainer) {
        return;
    }

    function createTimeInput(index, presetTime = '') {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'col-6 col-md-3 mb-3';
        timeDiv.innerHTML = `
            <label for="medication_time_${index}" class="form-label fw-semibold">
                Time ${index} <span class="text-danger">*</span>
            </label>
            <div class="input-group">
                <span class="input-group-text">
                    <i class="fas fa-clock text-muted"></i>
                </span>
                <input type="time" class="form-control medication-time" 
                       name="medication_time_${index}" 
                       id="medication_time_${index}" 
                       value="${presetTime}"
                       required>
            </div>
        `;
        return timeDiv;
    }

    function updateTimeInputs(frequencyType, times) {
        // Clear existing time inputs
        timeInputsContainer.innerHTML = '';

        if (times > 0) {
            timePickersContainer.style.display = 'block';

            // Get preset times for this frequency
            const presetTimes = FREQUENCY_PRESETS[frequencyType] || [];

            // Create time inputs with presets
            for (let i = 1; i <= times; i++) {
                const presetTime = presetTimes[i - 1] || '';
                const timeDiv = createTimeInput(i, presetTime);
                timeInputsContainer.appendChild(timeDiv);
            }

            // Add helpful text about presets
            if (presetTimes.length > 0) {
                const helpText = document.createElement('div');
                helpText.className = 'col-12 mb-2';
                helpText.innerHTML = `
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Preset times are automatically filled but can be edited as needed
                    </small>
                `;
                timeInputsContainer.insertBefore(helpText, timeInputsContainer.firstChild);
            }
        } else {
            // Hide time pickers for PRN (As Needed)
            timePickersContainer.style.display = 'none';
        }
    }

    // Add click handlers to frequency buttons
    frequencyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all buttons
            frequencyButtons.forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            });

            // Add active class to clicked button
            this.classList.remove('btn-outline-primary');
            this.classList.add('btn-primary');

            // Get frequency data
            const frequencyType = this.getAttribute('data-frequency');
            const times = parseInt(this.getAttribute('data-times'));

            // Update hidden frequency input
            if (frequencyMap[frequencyType]) {
                frequencyInput.value = frequencyMap[frequencyType];
            }

            // Update time inputs with presets
            updateTimeInputs(frequencyType, times);
        });
    });

    // Auto-select "Once Daily" by default if no frequency is selected
    const defaultButton = document.querySelector('.frequency-btn[data-frequency="once-daily"]');
    if (defaultButton && !frequencyInput.value) {
        defaultButton.click();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if required elements exist
    if (document.getElementById('med-search') && document.getElementById('medication-dropdown-home')) {
        initializeMedicationSearch('med-search', 'medication-dropdown-home');
    }
    if (document.getElementById('name') && document.getElementById('medication-dropdown')) {
        initializeMedicationSearch('name', 'medication-dropdown');
    }

    // Initialize medication frequency functionality
    initializeMedicationFrequency();
});

function initializeAutoComplete(inputId, dropdownId, url, options = {}) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    if (!input || !dropdown) {
        // Silently skip if elements don't exist - this is normal for different pages
        return;
    }
}