/**
 * Registration Data Storage Module
 * Handles saving and downloading registration data as JSON files
 * Modified to store ALL users in a single file
 */

class RegistrationStorage {
    constructor() {
        this.currentData = null;
        this.storageKey = 'all_registrations'; // Key for localStorage
    }

    /**
     * Save registration data to localStorage and update the master file
     * @param {Object} data - The registration form data
     * @returns {boolean} - Success status
     */
    saveToJSON(data) {
        try {
            // Add metadata
            const dataWithMetadata = {
                ...data,
                id: Date.now(), // Unique ID for each registration
                submittedAt: new Date().toISOString(),
                version: '1.0'
            };
            
            // Store current data
            this.currentData = dataWithMetadata;
            
            // Get all existing registrations
            const allRegistrations = this.getAllRegistrations();
            
            // Add new registration to the array
            allRegistrations.push(dataWithMetadata);
            
            // Save to localStorage
            localStorage.setItem(this.storageKey, JSON.stringify(allRegistrations));
            
            // Download the complete file with all users
            this.downloadAllRegistrations();
            
            console.log('Registration data saved successfully:', dataWithMetadata);
            console.log(`Total registrations: ${allRegistrations.length}`);
            
            return true;
        } catch (error) {
            console.error('Error saving registration data:', error);
            alert('Failed to save registration data. Please try again.');
            return false;
        }
    }

    /**
     * Download ALL registrations as a single JSON file
     * @returns {boolean} - Success status
     */
    downloadAllRegistrations() {
        const allRegistrations = this.getAllRegistrations();
        
        if (allRegistrations.length === 0) {
            alert('No registrations found to download');
            return false;
        }
        
        try {
            // Create a structured object with metadata
            const exportData = {
                metadata: {
                    exportDate: new Date().toISOString(),
                    totalUsers: allRegistrations.length,
                    version: '1.0'
                },
                registrations: allRegistrations
            };
            
            const jsonString = JSON.stringify(exportData, null, 2);
            this.downloadFile(jsonString, `all_registrations_${Date.now()}.json`);
            return true;
        } catch (error) {
            console.error('Error downloading all registrations:', error);
            alert('Failed to download registrations. Please try again.');
            return false;
        }
    }

    /**
     * Download the current user's data only
     * @returns {boolean} - Success status
     */
    downloadCurrentData() {
        if (!this.currentData) {
            alert('No registration data available to download');
            return false;
        }
        
        try {
            const jsonString = JSON.stringify(this.currentData, null, 2);
            this.downloadFile(jsonString, this.generateFileName(this.currentData.name));
            return true;
        } catch (error) {
            console.error('Error downloading data:', error);
            alert('Failed to download data. Please try again.');
            return false;
        }
    }

    /**
     * Create and trigger file download
     * @param {string} content - File content
     * @param {string} filename - Name of the file
     */
    downloadFile(content, filename) {
        // Create blob
        const blob = new Blob([content], { type: 'application/json' });
        
        // Create download URL
        const url = URL.createObjectURL(blob);
        
        // Create temporary link element
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        // Append to body, click, and cleanup
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);
    }

    /**
     * Generate a unique filename for the JSON file
     * @param {string} name - User's name
     * @returns {string} - Generated filename
     */
    generateFileName(name) {
        const sanitizedName = name.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '');
        const timestamp = Date.now();
        return `registration_${sanitizedName}_${timestamp}.json`;
    }

    /**
     * Get all registration data as an array
     * @returns {Array} - Array of all stored registrations
     */
    getAllRegistrations() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error retrieving registrations:', error);
            return [];
        }
    }

    /**
     * Get a specific registration by ID
     * @param {number} id - Registration ID
     * @returns {Object|null} - Registration object or null
     */
    getRegistrationById(id) {
        const registrations = this.getAllRegistrations();
        return registrations.find(reg => reg.id === id) || null;
    }

    /**
     * Update an existing registration
     * @param {number} id - Registration ID
     * @param {Object} updatedData - Updated registration data
     * @returns {boolean} - Success status
     */
    updateRegistration(id, updatedData) {
        try {
            const registrations = this.getAllRegistrations();
            const index = registrations.findIndex(reg => reg.id === id);
            
            if (index === -1) {
                alert('Registration not found');
                return false;
            }
            
            // Update the registration
            registrations[index] = {
                ...registrations[index],
                ...updatedData,
                updatedAt: new Date().toISOString()
            };
            
            // Save back to localStorage
            localStorage.setItem(this.storageKey, JSON.stringify(registrations));
            console.log('Registration updated successfully');
            return true;
        } catch (error) {
            console.error('Error updating registration:', error);
            return false;
        }
    }

    /**
     * Delete a specific registration
     * @param {number} id - Registration ID
     * @returns {boolean} - Success status
     */
    deleteRegistration(id) {
        try {
            const registrations = this.getAllRegistrations();
            const filteredRegistrations = registrations.filter(reg => reg.id !== id);
            
            if (registrations.length === filteredRegistrations.length) {
                alert('Registration not found');
                return false;
            }
            
            localStorage.setItem(this.storageKey, JSON.stringify(filteredRegistrations));
            console.log('Registration deleted successfully');
            return true;
        } catch (error) {
            console.error('Error deleting registration:', error);
            return false;
        }
    }

    /**
     * Clear all stored registrations from local storage
     * @returns {boolean} - Success status
     */
    clearAllRegistrations() {
        try {
            if (confirm('Are you sure you want to delete ALL registrations? This cannot be undone.')) {
                localStorage.removeItem(this.storageKey);
                console.log('All registrations cleared');
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error clearing registrations:', error);
            return false;
        }
    }

    /**
     * Get statistics about registrations
     * @returns {Object} - Statistics object
     */
    getStatistics() {
        const registrations = this.getAllRegistrations();
        
        return {
            total: registrations.length,
            byType: {
                individual: registrations.filter(r => r.type === 'Individual').length,
                agency: registrations.filter(r => r.type === 'Agency').length,
                subAgency: registrations.filter(r => r.type === 'Sub Agency').length
            },
            byStatus: {
                active: registrations.filter(r => r.status === 'Active').length,
                inactive: registrations.filter(r => r.status === 'Inactive').length,
                suspended: registrations.filter(r => r.status === 'Suspended').length
            },
            byCities: this.groupByField(registrations, 'city'),
            byStates: this.groupByField(registrations, 'state')
        };
    }

    /**
     * Group registrations by a specific field
     * @param {Array} registrations - Array of registrations
     * @param {string} field - Field name to group by
     * @returns {Object} - Grouped data
     */
    groupByField(registrations, field) {
        const grouped = {};
        registrations.forEach(reg => {
            const value = reg[field];
            if (value) {
                grouped[value] = (grouped[value] || 0) + 1;
            }
        });
        return grouped;
    }

    /**
     * Search registrations
     * @param {string} searchTerm - Search term
     * @returns {Array} - Filtered registrations
     */
    searchRegistrations(searchTerm) {
        const registrations = this.getAllRegistrations();
        const term = searchTerm.toLowerCase();
        
        return registrations.filter(reg => 
            reg.name.toLowerCase().includes(term) ||
            reg.city.toLowerCase().includes(term) ||
            reg.state.toLowerCase().includes(term) ||
            reg.status.toLowerCase().includes(term) ||
            reg.type.toLowerCase().includes(term)
        );
    }

    /**
     * Filter registrations by criteria
     * @param {Object} filters - Filter criteria
     * @returns {Array} - Filtered registrations
     */
    filterRegistrations(filters) {
        const registrations = this.getAllRegistrations();
        
        return registrations.filter(reg => {
            let matches = true;
            
            if (filters.type && reg.type !== filters.type) {
                matches = false;
            }
            if (filters.status && reg.status !== filters.status) {
                matches = false;
            }
            if (filters.city && reg.city !== filters.city) {
                matches = false;
            }
            if (filters.state && reg.state !== filters.state) {
                matches = false;
            }
            
            return matches;
        });
    }

    /**
     * Get registrations from a specific date range
     * @param {string} startDate - Start date (ISO format)
     * @param {string} endDate - End date (ISO format)
     * @returns {Array} - Filtered registrations
     */
    getRegistrationsByDateRange(startDate, endDate) {
        const registrations = this.getAllRegistrations();
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        return registrations.filter(reg => {
            const regDate = new Date(reg.submittedAt);
            return regDate >= start && regDate <= end;
        });
    }

    /**
     * Export registrations to CSV format
     * @returns {string} - CSV string
     */
    exportToCSV() {
        const registrations = this.getAllRegistrations();
        
        if (registrations.length === 0) {
            return '';
        }
        
        // CSV headers
        const headers = [
            'ID', 'Name', 'Email', 'City', 'State', 'Postal Code',
            'Type', 'Status', 'Gender', 'DOB', 'Submitted At'
        ];
        
        // CSV rows
        const rows = registrations.map(reg => [
            reg.id,
            reg.name,
            reg.email || '',
            reg.city,
            reg.state,
            reg.postalCode,
            reg.type,
            reg.status,
            reg.gender,
            reg.dob,
            reg.submittedAt
        ]);
        
        // Combine headers and rows
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        return csvContent;
    }

    /**
     * Download registrations as CSV file
     */
    downloadCSV() {
        const csv = this.exportToCSV();
        
        if (!csv) {
            alert('No registrations to export');
            return;
        }
        
        this.downloadFile(csv, `registrations_${Date.now()}.csv`);
    }

    /**
     * Validate registration data before saving
     * @param {Object} data - Registration data to validate
     * @returns {Object} - Validation result {valid: boolean, errors: array}
     */
    validateData(data) {
        const errors = [];
        
        // Required fields
        const requiredFields = ['name', 'address1', 'city', 'state', 'postalCode', 'dob', 'gender', 'status', 'onboardingDate', 'type'];
        
        requiredFields.forEach(field => {
            if (!data[field] || data[field].toString().trim() === '') {
                errors.push(`${field} is required`);
            }
        });
        
        // Multi-select fields
        if (!data.cityMulti || data.cityMulti.length === 0) {
            errors.push('At least one city must be selected');
        }
        
        if (!data.pinCode || data.pinCode.length === 0) {
            errors.push('At least one pin code must be selected');
        }
        
        if (!data.areaMulti || data.areaMulti.length === 0) {
            errors.push('At least one area must be selected');
        }
        
        if (!data.languages || data.languages.length === 0) {
            errors.push('At least one language must be selected');
        }
        
        // Postal code format
        if (data.postalCode && !/^\d{6}$/.test(data.postalCode)) {
            errors.push('Postal code must be 6 digits');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Format data for display or processing
     * @param {Object} data - Raw registration data
     * @returns {Object} - Formatted data
     */
    formatData(data) {
        return {
            personalInfo: {
                name: data.name,
                dateOfBirth: data.dob,
                gender: data.gender
            },
            contactDetails: {
                addressLine1: data.address1,
                addressLine2: data.address2 || 'N/A',
                city: data.city,
                state: data.state,
                postalCode: data.postalCode
            },
            multiSelectInfo: {
                selectedCities: data.cityMulti,
                pinCodes: data.pinCode,
                areas: data.areaMulti,
                languages: data.languages
            },
            registrationDetails: {
                status: data.status,
                onboardingDate: data.onboardingDate,
                type: data.type
            },
            metadata: {
                submittedAt: data.submittedAt || new Date().toISOString(),
                version: data.version || '1.0'
            }
        };
    }

    /**
     * Import registrations from a JSON file
     * @param {File} file - JSON file to import
     */
    async importFromJSON(file) {
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            // Handle different JSON structures
            let registrationsToImport = [];
            
            if (Array.isArray(data)) {
                registrationsToImport = data;
            } else if (data.registrations && Array.isArray(data.registrations)) {
                registrationsToImport = data.registrations;
            } else {
                throw new Error('Invalid JSON format');
            }
            
            // Get existing registrations
            const existing = this.getAllRegistrations();
            
            // Merge with new registrations (assign new IDs to avoid conflicts)
            const merged = [
                ...existing,
                ...registrationsToImport.map(reg => ({
                    ...reg,
                    id: Date.now() + Math.random(), // Ensure unique ID
                    importedAt: new Date().toISOString()
                }))
            ];
            
            // Save to localStorage
            localStorage.setItem(this.storageKey, JSON.stringify(merged));
            
            alert(`Successfully imported ${registrationsToImport.length} registrations!`);
            return true;
        } catch (error) {
            console.error('Error importing registrations:', error);
            alert('Failed to import registrations. Please check the file format.');
            return false;
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RegistrationStorage;
}
