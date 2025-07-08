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
        dropdown.innerHTML = '';
        selectedIndex = -1;
        if (currentMedications.length === 0) {
            hideDropdown();
            return;
        }
        currentMedications.forEach((med, index) => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.innerHTML = `${med.name} (${med.common_uses || 'No uses specified'})`;
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
                detailsDiv.innerHTML = `
                    <h5>${med.name}</h5>
                    <p><strong>Dosage:</strong> ${med.dosage || 'N/A'}</p>
                    <p><strong>Frequency:</strong> ${med.frequency || 'N/A'}</p>
                    <p><strong>Notes:</strong> ${med.notes || 'N/A'}</p>
                    <p><strong>Form:</strong> ${med.form || 'N/A'}</p>
                    <p><strong>Common Uses:</strong> ${med.common_uses || 'N/A'}</p>
                `;
            }
            if (dosageInput) dosageInput.value = med.dosage || '';
            if (frequencyInput) frequencyInput.value = med.frequency || '';
            if (notesInput) notesInput.value = med.notes || '';
            if (formInput) formInput.value = med.form || '';
            if (commonUsesInput) commonUsesInput.value = med.common_uses || '';
            hideDropdown();
        }
    }

    // Input event
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