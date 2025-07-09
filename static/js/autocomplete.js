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
        if (!dropdown) return;
        dropdown.innerHTML = '';
        selectedIndex = -1;
        if (currentMedications.length === 0) {
            hideDropdown();
            return;
        }
        currentMedications.forEach((med, index) => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.innerHTML = `
                <div class="medication-item">
                    <div class="medication-name">${med.display_name}</div>
                    <div class="medication-uses">${med.common_uses || 'No uses specified'}</div>
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
        if (!dropdown) return;
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        selectedIndex = -1;
    }

    // Select medication
    function selectMedication(index) {
        const med = currentMedications[index];
        if (med) {
            // Use brand name if available, otherwise generic name
            searchInput.value = med.brand_name || med.name;
            if (detailsDiv) {
                detailsDiv.innerHTML = `
                    <h5>${med.brand_name || med.name}</h5>
                    ${med.brand_name ? `<p><strong>Generic Name:</strong> ${med.name}</p>` : ''}
                    <p><strong>Dosage:</strong> ${med.dosage || 'N/A'}</p>
                    <p><strong>Frequency:</strong> ${med.frequency || 'N/A'}</p>
                    <p><strong>Notes:</strong> ${med.notes || 'N/A'}</p>
                    <p><strong>Form:</strong> ${med.form || 'N/A'}</p>
                    <p><strong>Common Uses:</strong> ${med.common_uses || 'N/A'}</p>
                `;
            }
            if (dosageInput) dosageInput.value = med.dosage || '';
            if (frequencyInput) frequencyInput.value = med.frequency || '';
            if (notesInput) {
                let notes = med.notes || '';
                if (med.brand_name && med.name !== med.brand_name) {
                    notes = notes ? `Generic name: ${med.name}. ${notes}` : `Generic name: ${med.name}`;
                }
                notesInput.value = notes;
            }
            if (formInput) formInput.value = med.form || '';
            if (commonUsesInput) commonUsesInput.value = med.common_uses || '';
            hideDropdown();
        }
    }

    // Input event
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            searchMedications(searchInput.value);
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            const items = dropdown.getElementsByClassName('dropdown-item');
            if (items.length === 0) return;

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
            if (detailsDiv) detailsDiv.innerHTML = '';
        }
    });

    // Update selected item
    function updateSelection(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove('selected');
            if (i === selectedIndex) {
                items[i].classList.add('selected');
                items[i].scrollIntoView({ block: 'nearest' });
            }
        }
    }

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            hideDropdown();
            if (detailsDiv) detailsDiv.innerHTML = '';
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeMedicationSearch('med-search', 'medication-dropdown-home');
    initializeMedicationSearch('name', 'medication-dropdown');
});
// Debounce function
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Initialize autocomplete for medication search
document.addEventListener('DOMContentLoaded', function() {
    const medicationInput = document.getElementById('name');
    const dropdown = document.getElementById('medication-dropdown');
    const detailsContainer = document.getElementById('medication-details');
    
    if (!medicationInput || !dropdown) return;

    // Create dropdown structure
    dropdown.innerHTML = '<ul class="dropdown-menu" style="display: none;"></ul>';
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');

    // Debounced search function
    const searchMedications = debounce(async function(query) {
        if (query.length < 2) {
            dropdownMenu.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`/api/medication-suggestions?term=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const suggestions = await response.json();
            
            if (suggestions.length > 0) {
                displaySuggestions(suggestions);
            } else {
                dropdownMenu.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching medication suggestions:', error);
            dropdownMenu.style.display = 'none';
        }
    }, 300);

    // Display suggestions
    function displaySuggestions(suggestions) {
        dropdownMenu.innerHTML = '';
        
        suggestions.forEach(med => {
            const li = document.createElement('li');
            li.className = 'dropdown-item';
            li.style.cursor = 'pointer';
            li.style.padding = '8px 12px';
            li.style.borderBottom = '1px solid #eee';
            
            li.innerHTML = `
                <div>
                    <strong>${med.display_name}</strong>
                    ${med.common_uses ? `<br><small class="text-muted">${med.common_uses}</small>` : ''}
                </div>
            `;
            
            li.addEventListener('click', function() {
                selectMedication(med);
            });
            
            li.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
            });
            
            li.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'white';
            });
            
            dropdownMenu.appendChild(li);
        });
        
        dropdownMenu.style.display = 'block';
        dropdownMenu.style.position = 'absolute';
        dropdownMenu.style.top = '100%';
        dropdownMenu.style.left = '0';
        dropdownMenu.style.right = '0';
        dropdownMenu.style.backgroundColor = 'white';
        dropdownMenu.style.border = '1px solid #ddd';
        dropdownMenu.style.borderRadius = '4px';
        dropdownMenu.style.maxHeight = '200px';
        dropdownMenu.style.overflowY = 'auto';
        dropdownMenu.style.zIndex = '1000';
        dropdownMenu.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    }

    // Select medication and auto-fill form
    function selectMedication(med) {
        medicationInput.value = med.display_name;
        
        // Auto-fill other fields
        const dosageField = document.getElementById('dosage');
        const frequencyField = document.getElementById('frequency');
        const notesField = document.getElementById('notes');
        const formField = document.getElementById('form');
        const commonUsesField = document.getElementById('common_uses');
        
        if (dosageField && med.dosage) dosageField.value = med.dosage;
        if (frequencyField && med.frequency) frequencyField.value = med.frequency;
        if (formField && med.form) formField.value = med.form;
        if (commonUsesField && med.common_uses) commonUsesField.value = med.common_uses;
        if (notesField && med.notes) notesField.value = med.notes;
        
        // Show auto-filled details
        if (detailsContainer) {
            detailsContainer.innerHTML = `
                <div class="alert alert-info">
                    <strong>Auto-filled from database:</strong><br>
                    Generic name: ${med.name}<br>
                    ${med.brand_name ? `Brand name: ${med.brand_name}<br>` : ''}
                    ${med.common_uses ? `Common uses: ${med.common_uses}` : ''}
                </div>
            `;
        }
        
        dropdownMenu.style.display = 'none';
    }

    // Event listeners
    medicationInput.addEventListener('input', function() {
        const query = this.value.trim();
        searchMedications(query);
    });

    medicationInput.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= 2) {
            searchMedications(query);
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!medicationInput.contains(event.target) && !dropdown.contains(event.target)) {
            dropdownMenu.style.display = 'none';
        }
    });

    // Handle keyboard navigation
    medicationInput.addEventListener('keydown', function(event) {
        const items = dropdownMenu.querySelectorAll('.dropdown-item');
        const currentActive = dropdownMenu.querySelector('.dropdown-item.active');
        let currentIndex = -1;
        
        if (currentActive) {
            currentIndex = Array.from(items).indexOf(currentActive);
        }
        
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
            setActiveItem(items, nextIndex);
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
            setActiveItem(items, prevIndex);
        } else if (event.key === 'Enter' && currentActive) {
            event.preventDefault();
            currentActive.click();
        } else if (event.key === 'Escape') {
            dropdownMenu.style.display = 'none';
        }
    });

    function setActiveItem(items, index) {
        items.forEach(item => item.classList.remove('active'));
        if (items[index]) {
            items[index].classList.add('active');
            items[index].style.backgroundColor = '#e9ecef';
        }
    }
});
