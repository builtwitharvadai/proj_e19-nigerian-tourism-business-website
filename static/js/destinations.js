/**
 * Destinations Page - Client-side functionality
 * Handles filtering, search, and modal interactions for Nigerian tourism destinations
 * 
 * @generated-from: task-id:TASK-003
 * @modifies: destinations page interactions
 * @dependencies: ["DOM", "Unsplash API"]
 */

(function() {
  'use strict';

  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const state = {
    destinations: [],
    filteredDestinations: [],
    currentCategory: 'all',
    searchQuery: '',
    selectedDestination: null,
    isModalOpen: false
  };

  // ============================================================================
  // DOM ELEMENT REFERENCES
  // ============================================================================

  const elements = {
    destinationsGrid: null,
    searchInput: null,
    categoryFilters: null,
    modal: null,
    modalContent: null,
    modalClose: null,
    noResults: null
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  /**
   * Initialize the destinations page functionality
   * Sets up event listeners and loads initial data
   */
  function init() {
    try {
      cacheElements();
      
      if (!validateElements()) {
        console.warn('Destinations page elements not found - skipping initialization');
        return;
      }

      loadDestinations();
      attachEventListeners();
      
      console.info('Destinations page initialized successfully');
    } catch (error) {
      console.error('Failed to initialize destinations page:', error);
      showError('Failed to initialize page. Please refresh.');
    }
  }

  /**
   * Cache DOM element references for performance
   */
  function cacheElements() {
    elements.destinationsGrid = document.getElementById('destinations-grid');
    elements.searchInput = document.getElementById('destination-search');
    elements.categoryFilters = document.querySelectorAll('[data-category]');
    elements.modal = document.getElementById('destination-modal');
    elements.modalContent = document.getElementById('modal-content');
    elements.modalClose = document.getElementById('modal-close');
    elements.noResults = document.getElementById('no-results');
  }

  /**
   * Validate that required DOM elements exist
   * @returns {boolean} True if all required elements are present
   */
  function validateElements() {
    return Boolean(
      elements.destinationsGrid &&
      elements.searchInput &&
      elements.categoryFilters.length > 0
    );
  }

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  /**
   * Load destinations from the DOM
   * Extracts destination data from data attributes
   */
  function loadDestinations() {
    try {
      const destinationCards = document.querySelectorAll('[data-destination-id]');
      
      state.destinations = Array.from(destinationCards).map(card => ({
        id: card.dataset.destinationId,
        name: card.dataset.destinationName || '',
        category: card.dataset.destinationCategory || 'cultural',
        location: card.dataset.destinationLocation || '',
        description: card.dataset.destinationDescription || '',
        image: card.dataset.destinationImage || '',
        details: card.dataset.destinationDetails || '',
        element: card
      }));

      state.filteredDestinations = [...state.destinations];
      
      console.info(`Loaded ${state.destinations.length} destinations`);
    } catch (error) {
      console.error('Failed to load destinations:', error);
      state.destinations = [];
      state.filteredDestinations = [];
    }
  }

  // ============================================================================
  // EVENT LISTENERS
  // ============================================================================

  /**
   * Attach all event listeners
   */
  function attachEventListeners() {
    // Search input with debouncing
    if (elements.searchInput) {
      elements.searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Category filters
    elements.categoryFilters.forEach(filter => {
      filter.addEventListener('click', handleCategoryFilter);
    });

    // Destination cards
    state.destinations.forEach(destination => {
      if (destination.element) {
        destination.element.addEventListener('click', () => {
          handleDestinationClick(destination.id);
        });
        destination.element.style.cursor = 'pointer';
      }
    });

    // Modal close handlers
    if (elements.modalClose) {
      elements.modalClose.addEventListener('click', closeModal);
    }

    if (elements.modal) {
      elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) {
          closeModal();
        }
      });
    }

    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboard);
  }

  // ============================================================================
  // SEARCH FUNCTIONALITY
  // ============================================================================

  /**
   * Handle search input
   * @param {Event} event - Input event
   */
  function handleSearch(event) {
    try {
      const query = event.target.value.trim().toLowerCase();
      state.searchQuery = query;
      
      console.info('Search query:', query);
      
      applyFilters();
    } catch (error) {
      console.error('Search error:', error);
    }
  }

  /**
   * Debounce function to limit execution rate
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   * @returns {Function} Debounced function
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func.apply(this, args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ============================================================================
  // CATEGORY FILTERING
  // ============================================================================

  /**
   * Handle category filter click
   * @param {Event} event - Click event
   */
  function handleCategoryFilter(event) {
    try {
      const category = event.currentTarget.dataset.category;
      
      if (!category) {
        console.warn('Category filter missing data-category attribute');
        return;
      }

      state.currentCategory = category;
      
      // Update active state on filter buttons
      elements.categoryFilters.forEach(filter => {
        filter.classList.remove('active', 'bg-blue-600', 'text-white');
        filter.classList.add('bg-gray-200', 'text-gray-700');
      });
      
      event.currentTarget.classList.remove('bg-gray-200', 'text-gray-700');
      event.currentTarget.classList.add('active', 'bg-blue-600', 'text-white');
      
      console.info('Category filter applied:', category);
      
      applyFilters();
    } catch (error) {
      console.error('Category filter error:', error);
    }
  }

  // ============================================================================
  // FILTER APPLICATION
  // ============================================================================

  /**
   * Apply all active filters (search + category)
   */
  function applyFilters() {
    try {
      state.filteredDestinations = state.destinations.filter(destination => {
        // Category filter
        const categoryMatch = state.currentCategory === 'all' || 
                            destination.category === state.currentCategory;
        
        // Search filter
        const searchMatch = !state.searchQuery || 
                          destination.name.toLowerCase().includes(state.searchQuery) ||
                          destination.location.toLowerCase().includes(state.searchQuery) ||
                          destination.description.toLowerCase().includes(state.searchQuery);
        
        return categoryMatch && searchMatch;
      });

      console.info(`Filtered to ${state.filteredDestinations.length} destinations`);
      
      updateDisplay();
    } catch (error) {
      console.error('Filter application error:', error);
      showError('Failed to apply filters');
    }
  }

  /**
   * Update the display based on filtered destinations
   */
  function updateDisplay() {
    try {
      // Hide all destinations
      state.destinations.forEach(destination => {
        if (destination.element) {
          destination.element.style.display = 'none';
        }
      });

      // Show filtered destinations
      state.filteredDestinations.forEach(destination => {
        if (destination.element) {
          destination.element.style.display = 'block';
        }
      });

      // Show/hide no results message
      if (elements.noResults) {
        if (state.filteredDestinations.length === 0) {
          elements.noResults.style.display = 'block';
          elements.noResults.textContent = state.searchQuery 
            ? `No destinations found matching "${state.searchQuery}"`
            : 'No destinations found in this category';
        } else {
          elements.noResults.style.display = 'none';
        }
      }
    } catch (error) {
      console.error('Display update error:', error);
    }
  }

  // ============================================================================
  // MODAL FUNCTIONALITY
  // ============================================================================

  /**
   * Handle destination card click
   * @param {string} destinationId - ID of the clicked destination
   */
  function handleDestinationClick(destinationId) {
    try {
      const destination = state.destinations.find(d => d.id === destinationId);
      
      if (!destination) {
        console.error('Destination not found:', destinationId);
        return;
      }

      state.selectedDestination = destination;
      openModal(destination);
      
      console.info('Opened destination modal:', destination.name);
    } catch (error) {
      console.error('Failed to open destination modal:', error);
      showError('Failed to load destination details');
    }
  }

  /**
   * Open modal with destination details
   * @param {Object} destination - Destination object
   */
  function openModal(destination) {
    if (!elements.modal || !elements.modalContent) {
      console.warn('Modal elements not available');
      return;
    }

    try {
      // Build modal content
      const modalHTML = `
        <div class="relative">
          <img 
            src="${escapeHtml(destination.image)}" 
            alt="${escapeHtml(destination.name)}"
            class="w-full h-64 object-cover rounded-t-lg"
            onerror="this.src='https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80'"
          />
          <div class="p-6">
            <h2 class="text-3xl font-bold mb-2">${escapeHtml(destination.name)}</h2>
            <p class="text-gray-600 mb-4">
              <svg class="inline w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
              </svg>
              ${escapeHtml(destination.location)}
            </p>
            <div class="mb-4">
              <span class="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                ${escapeHtml(destination.category)}
              </span>
            </div>
            <p class="text-gray-700 mb-4">${escapeHtml(destination.description)}</p>
            ${destination.details ? `
              <div class="border-t pt-4 mt-4">
                <h3 class="text-xl font-semibold mb-2">Details</h3>
                <p class="text-gray-700">${escapeHtml(destination.details)}</p>
              </div>
            ` : ''}
          </div>
        </div>
      `;

      elements.modalContent.innerHTML = modalHTML;
      elements.modal.classList.remove('hidden');
      elements.modal.classList.add('flex');
      state.isModalOpen = true;

      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } catch (error) {
      console.error('Failed to render modal:', error);
      showError('Failed to display destination details');
    }
  }

  /**
   * Close the modal
   */
  function closeModal() {
    if (!elements.modal) return;

    try {
      elements.modal.classList.add('hidden');
      elements.modal.classList.remove('flex');
      state.isModalOpen = false;
      state.selectedDestination = null;

      // Restore body scroll
      document.body.style.overflow = '';

      console.info('Modal closed');
    } catch (error) {
      console.error('Failed to close modal:', error);
    }
  }

  // ============================================================================
  // KEYBOARD NAVIGATION
  // ============================================================================

  /**
   * Handle keyboard events
   * @param {KeyboardEvent} event - Keyboard event
   */
  function handleKeyboard(event) {
    // Close modal on Escape key
    if (event.key === 'Escape' && state.isModalOpen) {
      closeModal();
    }
  }

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  function escapeHtml(text) {
    if (!text) return '';
    
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Show error message to user
   * @param {string} message - Error message
   */
  function showError(message) {
    console.error('User-facing error:', message);
    
    // Create temporary error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
      errorDiv.remove();
    }, 5000);
  }

  // ============================================================================
  // ENTRY POINT
  // ============================================================================

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();