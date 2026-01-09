/**
 * Destinations Carousel
 * Touch-friendly carousel with auto-advance, navigation controls, and responsive behavior
 * @generated-from: task-id:TASK-002
 * @modifies: none
 * @dependencies: []
 */

(function () {
  'use strict';

  /**
   * Carousel state management
   */
  class CarouselState {
    constructor(totalSlides) {
      this.currentIndex = 0;
      this.totalSlides = totalSlides;
      this.isAutoPlaying = true;
      this.isTransitioning = false;
      this.touchStartX = 0;
      this.touchEndX = 0;
      this.autoPlayInterval = null;
    }

    next() {
      this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
      return this.currentIndex;
    }

    previous() {
      this.currentIndex =
        (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
      return this.currentIndex;
    }

    goTo(index) {
      if (index >= 0 && index < this.totalSlides) {
        this.currentIndex = index;
        return this.currentIndex;
      }
      return this.currentIndex;
    }

    setTransitioning(value) {
      this.isTransitioning = value;
    }

    setAutoPlaying(value) {
      this.isAutoPlaying = value;
    }

    recordTouchStart(x) {
      this.touchStartX = x;
    }

    recordTouchEnd(x) {
      this.touchEndX = x;
    }

    getTouchDelta() {
      return this.touchStartX - this.touchEndX;
    }
  }

  /**
   * Carousel controller
   */
  class DestinationsCarousel {
    constructor(containerSelector, options = {}) {
      this.container = document.querySelector(containerSelector);

      if (!this.container) {
        console.error(
          `Carousel container not found: ${containerSelector}`
        );
        return;
      }

      this.options = {
        autoPlayDelay: options.autoPlayDelay || 5000,
        transitionDuration: options.transitionDuration || 500,
        swipeThreshold: options.swipeThreshold || 50,
        pauseOnHover: options.pauseOnHover !== false,
        enableKeyboard: options.enableKeyboard !== false,
        ...options,
      };

      this.slides = this.container.querySelectorAll('[data-carousel-slide]');
      this.prevButton = this.container.querySelector(
        '[data-carousel-prev]'
      );
      this.nextButton = this.container.querySelector(
        '[data-carousel-next]'
      );
      this.indicators = this.container.querySelectorAll(
        '[data-carousel-indicator]'
      );

      if (this.slides.length === 0) {
        console.warn('No carousel slides found');
        return;
      }

      this.state = new CarouselState(this.slides.length);
      this.init();
    }

    init() {
      this.setupEventListeners();
      this.updateCarousel(0);
      this.startAutoPlay();
    }

    setupEventListeners() {
      if (this.prevButton) {
        this.prevButton.addEventListener('click', () => this.previous());
      }

      if (this.nextButton) {
        this.nextButton.addEventListener('click', () => this.next());
      }

      this.indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => this.goToSlide(index));
      });

      this.container.addEventListener('touchstart', (e) =>
        this.handleTouchStart(e)
      );
      this.container.addEventListener('touchend', (e) =>
        this.handleTouchEnd(e)
      );

      if (this.options.pauseOnHover) {
        this.container.addEventListener('mouseenter', () =>
          this.pauseAutoPlay()
        );
        this.container.addEventListener('mouseleave', () =>
          this.resumeAutoPlay()
        );
      }

      if (this.options.enableKeyboard) {
        document.addEventListener('keydown', (e) =>
          this.handleKeyboard(e)
        );
      }

      window.addEventListener('resize', () => this.handleResize());

      window.addEventListener('visibilitychange', () =>
        this.handleVisibilityChange()
      );
    }

    updateCarousel(newIndex, direction = 'next') {
      if (this.state.isTransitioning) {
        return;
      }

      this.state.setTransitioning(true);

      this.slides.forEach((slide, index) => {
        slide.classList.remove('active', 'prev', 'next');
        slide.setAttribute('aria-hidden', 'true');

        if (index === newIndex) {
          slide.classList.add('active');
          slide.setAttribute('aria-hidden', 'false');
        }
      });

      this.updateIndicators(newIndex);
      this.updateButtons();

      setTimeout(() => {
        this.state.setTransitioning(false);
      }, this.options.transitionDuration);
    }

    updateIndicators(activeIndex) {
      this.indicators.forEach((indicator, index) => {
        if (index === activeIndex) {
          indicator.classList.add('active');
          indicator.setAttribute('aria-current', 'true');
        } else {
          indicator.classList.remove('active');
          indicator.setAttribute('aria-current', 'false');
        }
      });
    }

    updateButtons() {
      if (this.prevButton) {
        this.prevButton.setAttribute(
          'aria-label',
          `Go to slide ${this.state.currentIndex}`
        );
      }

      if (this.nextButton) {
        this.nextButton.setAttribute(
          'aria-label',
          `Go to slide ${(this.state.currentIndex + 2) % this.state.totalSlides || this.state.totalSlides}`
        );
      }
    }

    next() {
      const newIndex = this.state.next();
      this.updateCarousel(newIndex, 'next');
      this.resetAutoPlay();
    }

    previous() {
      const newIndex = this.state.previous();
      this.updateCarousel(newIndex, 'prev');
      this.resetAutoPlay();
    }

    goToSlide(index) {
      if (index === this.state.currentIndex) {
        return;
      }

      const direction = index > this.state.currentIndex ? 'next' : 'prev';
      const newIndex = this.state.goTo(index);
      this.updateCarousel(newIndex, direction);
      this.resetAutoPlay();
    }

    handleTouchStart(e) {
      const touch = e.touches[0];
      this.state.recordTouchStart(touch.clientX);
    }

    handleTouchEnd(e) {
      const touch = e.changedTouches[0];
      this.state.recordTouchEnd(touch.clientX);

      const delta = this.state.getTouchDelta();

      if (Math.abs(delta) > this.options.swipeThreshold) {
        if (delta > 0) {
          this.next();
        } else {
          this.previous();
        }
      }
    }

    handleKeyboard(e) {
      if (!this.container.matches(':hover') && document.activeElement !== this.container) {
        return;
      }

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault();
          this.previous();
          break;
        case 'ArrowRight':
          e.preventDefault();
          this.next();
          break;
        case 'Home':
          e.preventDefault();
          this.goToSlide(0);
          break;
        case 'End':
          e.preventDefault();
          this.goToSlide(this.state.totalSlides - 1);
          break;
      }
    }

    handleResize() {
      this.updateCarousel(this.state.currentIndex);
    }

    handleVisibilityChange() {
      if (document.hidden) {
        this.pauseAutoPlay();
      } else {
        this.resumeAutoPlay();
      }
    }

    startAutoPlay() {
      if (!this.state.isAutoPlaying) {
        return;
      }

      this.stopAutoPlay();

      this.state.autoPlayInterval = setInterval(() => {
        this.next();
      }, this.options.autoPlayDelay);
    }

    stopAutoPlay() {
      if (this.state.autoPlayInterval) {
        clearInterval(this.state.autoPlayInterval);
        this.state.autoPlayInterval = null;
      }
    }

    pauseAutoPlay() {
      this.state.setAutoPlaying(false);
      this.stopAutoPlay();
    }

    resumeAutoPlay() {
      this.state.setAutoPlaying(true);
      this.startAutoPlay();
    }

    resetAutoPlay() {
      if (this.state.isAutoPlaying) {
        this.startAutoPlay();
      }
    }

    destroy() {
      this.stopAutoPlay();

      if (this.prevButton) {
        this.prevButton.removeEventListener('click', () => this.previous());
      }

      if (this.nextButton) {
        this.nextButton.removeEventListener('click', () => this.next());
      }

      this.indicators.forEach((indicator) => {
        indicator.removeEventListener('click', () => {});
      });

      this.container.removeEventListener('touchstart', () => {});
      this.container.removeEventListener('touchend', () => {});
      this.container.removeEventListener('mouseenter', () => {});
      this.container.removeEventListener('mouseleave', () => {});

      if (this.options.enableKeyboard) {
        document.removeEventListener('keydown', () => {});
      }

      window.removeEventListener('resize', () => {});
      window.removeEventListener('visibilitychange', () => {});
    }
  }

  function initializeCarousels() {
    const carousels = document.querySelectorAll('[data-carousel]');

    carousels.forEach((carouselElement) => {
      const autoPlayDelay = parseInt(
        carouselElement.dataset.carouselAutoplay,
        10
      );
      const pauseOnHover =
        carouselElement.dataset.carouselPause !== 'false';

      try {
        new DestinationsCarousel(`#${carouselElement.id}`, {
          autoPlayDelay: autoPlayDelay || 5000,
          pauseOnHover,
        });
      } catch (error) {
        console.error(
          `Failed to initialize carousel: ${carouselElement.id}`,
          error
        );
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCarousels);
  } else {
    initializeCarousels();
  }

  window.DestinationsCarousel = DestinationsCarousel;
})();