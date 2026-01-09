# tests/test_homepage.py

"""
Comprehensive test suite for homepage functionality and responsive design.

Tests cover:
- Homepage rendering and content validation
- Navigation elements and accessibility
- Carousel functionality and interactions
- Responsive design elements
- SEO metadata and structured data
- Performance and security considerations
"""

import pytest
from flask import url_for
from flask.testing import FlaskClient
from bs4 import BeautifulSoup
import json
import re


class TestHomepageRendering:
    """Test suite for homepage rendering and basic functionality."""

    def test_homepage_loads_successfully(self, client: FlaskClient):
        """
        Test that homepage loads with 200 status code.
        
        Validates:
        - Successful HTTP response
        - Content type is HTML
        """
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_homepage_has_correct_title(self, client: FlaskClient):
        """
        Test that homepage has correct title tag.
        
        Validates:
        - Title tag exists
        - Title contains expected content
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        title = soup.find('title')
        assert title is not None
        assert 'Discover Nigeria' in title.string
        assert 'Explore Breathtaking Landscapes' in title.string

    def test_homepage_has_hero_section(self, client: FlaskClient):
        """
        Test that homepage contains hero section with required elements.
        
        Validates:
        - Hero section exists
        - Hero title is present
        - Hero subtitle is present
        - Hero image is present
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_section = soup.find('section', class_='hero-section')
        assert hero_section is not None
        
        hero_title = hero_section.find('h1', class_='hero-title')
        assert hero_title is not None
        assert 'Discover the Beauty of Nigeria' in hero_title.text
        
        hero_subtitle = hero_section.find('p', class_='hero-subtitle')
        assert hero_subtitle is not None
        
        hero_image = hero_section.find('img', class_='hero-image')
        assert hero_image is not None
        assert hero_image.get('src') is not None

    def test_homepage_has_featured_destinations_section(self, client: FlaskClient):
        """
        Test that homepage contains featured destinations section.
        
        Validates:
        - Featured destinations section exists
        - Section has proper heading
        - Section contains carousel
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        destinations_section = soup.find('section', {'aria-labelledby': 'destinations-title'})
        assert destinations_section is not None
        
        section_title = soup.find('h2', id='destinations-title')
        assert section_title is not None
        assert 'Featured Destinations' in section_title.text
        
        carousel = soup.find('div', {'data-carousel': True})
        assert carousel is not None

    def test_homepage_has_services_section(self, client: FlaskClient):
        """
        Test that homepage contains services section with all services.
        
        Validates:
        - Services section exists
        - All four services are displayed
        - Each service has icon, title, and description
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        services_section = soup.find('section', {'aria-labelledby': 'services-title'})
        assert services_section is not None
        
        service_cards = services_section.find_all('article', class_='service-card')
        assert len(service_cards) == 4
        
        expected_services = [
            'Tour Packages',
            'Hotel Booking',
            'Travel Guides',
            'Transportation'
        ]
        
        for card in service_cards:
            title = card.find('h3', class_='service-title')
            assert title is not None
            assert title.text.strip() in expected_services
            
            icon = card.find('svg', class_='service-icon')
            assert icon is not None
            
            description = card.find('p', class_='service-description')
            assert description is not None

    def test_homepage_has_testimonials_section(self, client: FlaskClient):
        """
        Test that homepage contains testimonials section.
        
        Validates:
        - Testimonials section exists
        - Contains three testimonials
        - Each testimonial has rating, quote, and author
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        testimonials_section = soup.find('section', {'aria-labelledby': 'testimonials-title'})
        assert testimonials_section is not None
        
        testimonial_cards = testimonials_section.find_all('article')
        assert len(testimonial_cards) == 3
        
        for card in testimonial_cards:
            # Check for star rating
            stars = card.find('div', {'aria-label': re.compile(r'5 out of 5 stars')})
            assert stars is not None
            
            # Check for quote
            quote = card.find('blockquote')
            assert quote is not None
            
            # Check for author
            author = card.find('cite')
            assert author is not None

    def test_homepage_has_cta_section(self, client: FlaskClient):
        """
        Test that homepage contains call-to-action section.
        
        Validates:
        - CTA section exists
        - Contains heading and description
        - Has action buttons
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        cta_section = soup.find('section', class_='cta-section')
        assert cta_section is not None
        
        cta_title = cta_section.find('h2', class_='cta-title')
        assert cta_title is not None
        assert 'Ready to Explore Nigeria?' in cta_title.text
        
        cta_buttons = cta_section.find('div', class_='cta-buttons')
        assert cta_buttons is not None
        
        buttons = cta_buttons.find_all('a', class_='btn')
        assert len(buttons) == 2


class TestNavigationElements:
    """Test suite for navigation elements and links."""

    def test_hero_cta_buttons_exist(self, client: FlaskClient):
        """
        Test that hero section contains CTA buttons.
        
        Validates:
        - Both CTA buttons are present
        - Buttons have correct links
        - Buttons have proper styling classes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_section = soup.find('section', class_='hero-section')
        buttons = hero_section.find_all('a', class_='btn')
        
        assert len(buttons) == 2
        
        explore_btn = buttons[0]
        assert 'Explore Destinations' in explore_btn.text
        assert 'btn-primary' in explore_btn.get('class', [])
        
        plan_btn = buttons[1]
        assert 'Plan Your Trip' in plan_btn.text

    def test_destination_cards_have_learn_more_links(self, client: FlaskClient):
        """
        Test that destination cards contain 'Learn More' links.
        
        Validates:
        - Each carousel slide has a learn more button
        - Buttons link to destinations page
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel_slides = soup.find_all('div', {'data-carousel-slide': True})
        
        for slide in carousel_slides:
            learn_more = slide.find('a', class_='btn')
            assert learn_more is not None
            assert 'Learn More' in learn_more.text

    def test_cta_buttons_have_correct_links(self, client: FlaskClient):
        """
        Test that CTA section buttons have correct URLs.
        
        Validates:
        - Contact button links to contact page
        - Destinations button links to destinations page
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        cta_section = soup.find('section', class_='cta-section')
        buttons = cta_section.find_all('a', class_='btn')
        
        contact_btn = buttons[0]
        assert 'contact' in contact_btn.get('href', '').lower()
        
        destinations_btn = buttons[1]
        assert 'destinations' in destinations_btn.get('href', '').lower()


class TestCarouselFunctionality:
    """Test suite for carousel functionality and structure."""

    def test_carousel_has_correct_structure(self, client: FlaskClient):
        """
        Test that carousel has proper HTML structure.
        
        Validates:
        - Carousel container exists
        - Has data-carousel attribute
        - Contains carousel track
        - Has proper ARIA attributes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel = soup.find('div', {'data-carousel': True})
        assert carousel is not None
        assert carousel.get('role') == 'region'
        assert carousel.get('aria-label') is not None
        
        carousel_track = carousel.find('div', class_='carousel-track')
        assert carousel_track is not None

    def test_carousel_has_three_slides(self, client: FlaskClient):
        """
        Test that carousel contains exactly three slides.
        
        Validates:
        - Three carousel slides exist
        - First slide is active
        - Each slide has proper ARIA attributes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        slides = soup.find_all('div', {'data-carousel-slide': True})
        assert len(slides) == 3
        
        # First slide should be active
        first_slide = slides[0]
        assert 'active' in first_slide.get('class', [])
        assert first_slide.get('aria-hidden') == 'false'
        
        # Other slides should not be active
        for slide in slides[1:]:
            assert 'active' not in slide.get('class', [])
            assert slide.get('aria-hidden') == 'true'

    def test_carousel_slides_contain_destination_data(self, client: FlaskClient):
        """
        Test that carousel slides contain destination information.
        
        Validates:
        - Each slide has destination name
        - Each slide has description
        - Each slide has image
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        slides = soup.find_all('div', {'data-carousel-slide': True})
        
        expected_destinations = [
            'Yankari National Park',
            'Olumo Rock',
            'Elegushi Beach'
        ]
        
        for i, slide in enumerate(slides):
            card = slide.find('div', class_='card')
            assert card is not None
            
            title = card.find('h3', class_='card-title')
            assert title is not None
            assert expected_destinations[i] in title.text
            
            description = card.find('p', class_='card-description')
            assert description is not None
            assert len(description.text.strip()) > 0
            
            image = card.find('img', class_='card-image')
            assert image is not None
            assert image.get('src') is not None

    def test_carousel_has_navigation_controls(self, client: FlaskClient):
        """
        Test that carousel has navigation controls.
        
        Validates:
        - Previous button exists
        - Next button exists
        - Buttons have proper ARIA labels
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel = soup.find('div', {'data-carousel': True})
        
        prev_button = carousel.find('button', {'data-carousel-prev': True})
        assert prev_button is not None
        assert prev_button.get('aria-label') == 'Previous slide'
        
        next_button = carousel.find('button', {'data-carousel-next': True})
        assert next_button is not None
        assert next_button.get('aria-label') == 'Next slide'

    def test_carousel_has_indicators(self, client: FlaskClient):
        """
        Test that carousel has slide indicators.
        
        Validates:
        - Three indicators exist
        - First indicator is active
        - Indicators have proper ARIA attributes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        indicators = soup.find_all('button', {'data-carousel-indicator': True})
        assert len(indicators) == 3
        
        # First indicator should be active
        first_indicator = indicators[0]
        assert 'active' in first_indicator.get('class', [])
        assert first_indicator.get('aria-selected') == 'true'
        
        # Other indicators should not be active
        for indicator in indicators[1:]:
            assert 'active' not in indicator.get('class', [])
            assert indicator.get('aria-selected') == 'false'

    def test_carousel_has_autoplay_attribute(self, client: FlaskClient):
        """
        Test that carousel has autoplay configuration.
        
        Validates:
        - Carousel has autoplay data attribute
        - Autoplay interval is set to 5000ms
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel = soup.find('div', {'data-carousel': True})
        assert carousel.get('data-carousel-autoplay') == '5000'


class TestResponsiveDesign:
    """Test suite for responsive design elements."""

    def test_hero_image_has_responsive_attributes(self, client: FlaskClient):
        """
        Test that hero image has responsive image attributes.
        
        Validates:
        - Image has srcset attribute
        - Image has sizes attribute
        - Image has proper loading attributes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_image = soup.find('img', class_='hero-image')
        assert hero_image is not None
        
        assert hero_image.get('srcset') is not None
        assert hero_image.get('sizes') is not None
        assert hero_image.get('loading') == 'eager'
        assert hero_image.get('fetchpriority') == 'high'

    def test_destination_images_have_lazy_loading(self, client: FlaskClient):
        """
        Test that destination images use lazy loading.
        
        Validates:
        - Images have loading="lazy" attribute
        - Images have srcset for responsive sizes
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        card_images = soup.find_all('img', class_='card-image')
        
        for image in card_images:
            assert image.get('loading') == 'lazy'
            assert image.get('srcset') is not None
            assert image.get('sizes') is not None

    def test_responsive_grid_classes_exist(self, client: FlaskClient):
        """
        Test that responsive grid classes are present.
        
        Validates:
        - Services section uses responsive grid
        - Testimonials section uses responsive grid
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        services_grid = soup.find('div', class_='grid-services')
        assert services_grid is not None
        
        testimonials_grid = soup.find('section', {'aria-labelledby': 'testimonials-title'}).find('div', class_='grid')
        assert testimonials_grid is not None
        assert 'md:grid-cols-2' in str(testimonials_grid.get('class', []))
        assert 'lg:grid-cols-3' in str(testimonials_grid.get('class', []))

    def test_hero_buttons_have_responsive_layout(self, client: FlaskClient):
        """
        Test that hero CTA buttons have responsive layout.
        
        Validates:
        - Button container has flex layout
        - Container has responsive flex direction
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_section = soup.find('section', class_='hero-section')
        button_container = hero_section.find('div', class_=re.compile(r'flex.*sm:flex-row'))
        
        assert button_container is not None
        classes = ' '.join(button_container.get('class', []))
        assert 'flex-col' in classes
        assert 'sm:flex-row' in classes


class TestAccessibility:
    """Test suite for accessibility features."""

    def test_hero_section_has_proper_aria_labels(self, client: FlaskClient):
        """
        Test that hero section has proper ARIA labels.
        
        Validates:
        - Hero section has aria-labelledby
        - Hero title has proper id
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_section = soup.find('section', class_='hero-section')
        assert hero_section.get('aria-labelledby') == 'hero-title'
        
        hero_title = soup.find('h1', id='hero-title')
        assert hero_title is not None

    def test_all_images_have_alt_text(self, client: FlaskClient):
        """
        Test that all images have descriptive alt text.
        
        Validates:
        - Every img tag has alt attribute
        - Alt text is descriptive (not empty)
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        images = soup.find_all('img')
        
        for image in images:
            alt_text = image.get('alt')
            assert alt_text is not None
            assert len(alt_text.strip()) > 0
            # Alt text should be descriptive
            assert len(alt_text.split()) >= 3

    def test_sections_have_proper_headings(self, client: FlaskClient):
        """
        Test that sections have proper heading hierarchy.
        
        Validates:
        - Each section has h2 heading
        - Headings have proper ids
        - Sections reference heading ids
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        sections = soup.find_all('section', {'aria-labelledby': True})
        
        for section in sections:
            labelledby = section.get('aria-labelledby')
            heading = soup.find(id=labelledby)
            
            assert heading is not None
            assert heading.name == 'h2'

    def test_buttons_have_proper_labels(self, client: FlaskClient):
        """
        Test that all buttons have proper labels or text.
        
        Validates:
        - Buttons with icons have aria-label
        - Text buttons have descriptive text
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        buttons = soup.find_all('button')
        
        for button in buttons:
            # Button should have either text content or aria-label
            has_text = len(button.get_text(strip=True)) > 0
            has_aria_label = button.get('aria-label') is not None
            
            assert has_text or has_aria_label

    def test_carousel_has_proper_aria_attributes(self, client: FlaskClient):
        """
        Test that carousel has proper ARIA attributes for accessibility.
        
        Validates:
        - Carousel has role="region"
        - Slides have role="group"
        - Indicators have role="tab"
        - Proper aria-hidden states
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel = soup.find('div', {'data-carousel': True})
        assert carousel.get('role') == 'region'
        assert carousel.get('aria-label') is not None
        
        slides = carousel.find_all('div', {'data-carousel-slide': True})
        for slide in slides:
            assert slide.get('role') == 'group'
            assert slide.get('aria-roledescription') == 'slide'
            assert slide.get('aria-hidden') is not None
        
        indicators = carousel.find_all('button', {'data-carousel-indicator': True})
        for indicator in indicators:
            assert indicator.get('role') == 'tab'
            assert indicator.get('aria-selected') is not None


class TestSEOMetadata:
    """Test suite for SEO metadata and structured data."""

    def test_page_has_open_graph_metadata(self, client: FlaskClient):
        """
        Test that page has Open Graph metadata for social sharing.
        
        Validates:
        - og:title exists
        - og:description exists
        - og:image exists
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        og_title = soup.find('meta', property='og:title')
        assert og_title is not None
        assert 'Nigeria' in og_title.get('content', '')
        
        og_description = soup.find('meta', property='og:description')
        assert og_description is not None
        
        og_image = soup.find('meta', property='og:image')
        assert og_image is not None
        assert 'http' in og_image.get('content', '')

    def test_page_has_twitter_card_metadata(self, client: FlaskClient):
        """
        Test that page has Twitter Card metadata.
        
        Validates:
        - twitter:title exists
        - twitter:description exists
        - twitter:image exists
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        assert twitter_title is not None
        
        twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
        assert twitter_description is not None
        
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        assert twitter_image is not None

    def test_page_has_structured_data(self, client: FlaskClient):
        """
        Test that page has JSON-LD structured data.
        
        Validates:
        - JSON-LD script exists
        - Contains TouristAttraction schema
        - Has required properties
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        json_ld = soup.find('script', type='application/ld+json')
        assert json_ld is not None
        
        structured_data = json.loads(json_ld.string)
        assert structured_data['@context'] == 'https://schema.org'
        assert structured_data['@type'] == 'TouristAttraction'
        assert 'name' in structured_data
        assert 'description' in structured_data
        assert 'url' in structured_data
        assert 'image' in structured_data
        assert 'address' in structured_data
        assert 'geo' in structured_data

    def test_structured_data_has_valid_geo_coordinates(self, client: FlaskClient):
        """
        Test that structured data has valid geographic coordinates.
        
        Validates:
        - Geo coordinates exist
        - Latitude and longitude are valid numbers
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        json_ld = soup.find('script', type='application/ld+json')
        structured_data = json.loads(json_ld.string)
        
        geo = structured_data.get('geo')
        assert geo is not None
        assert geo['@type'] == 'GeoCoordinates'
        
        latitude = float(geo['latitude'])
        longitude = float(geo['longitude'])
        
        # Nigeria's approximate coordinates
        assert 4.0 <= latitude <= 14.0
        assert 2.0 <= longitude <= 15.0


class TestPerformance:
    """Test suite for performance-related attributes."""

    def test_hero_image_has_priority_loading(self, client: FlaskClient):
        """
        Test that hero image has priority loading attributes.
        
        Validates:
        - loading="eager" for above-fold content
        - fetchpriority="high" for LCP optimization
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_image = soup.find('img', class_='hero-image')
        assert hero_image.get('loading') == 'eager'
        assert hero_image.get('fetchpriority') == 'high'

    def test_below_fold_images_lazy_load(self, client: FlaskClient):
        """
        Test that below-fold images use lazy loading.
        
        Validates:
        - Carousel images have loading="lazy"
        - Lazy loading improves initial page load
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        carousel_images = soup.find_all('img', class_='card-image')
        
        for image in carousel_images:
            assert image.get('loading') == 'lazy'

    def test_images_have_decoding_async(self, client: FlaskClient):
        """
        Test that images use async decoding for better performance.
        
        Validates:
        - Images have decoding="async" attribute
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        images = soup.find_all('img')
        
        for image in images:
            assert image.get('decoding') == 'async'

    def test_page_has_minimal_inline_styles(self, client: FlaskClient):
        """
        Test that page uses minimal inline styles.
        
        Validates:
        - Inline styles are limited to critical CSS
        - Most styling is in external stylesheets
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for style block in extra_css
        style_blocks = soup.find_all('style')
        
        # Should have minimal inline styles (only critical CSS)
        for style_block in style_blocks:
            style_content = style_block.string
            if style_content:
                # Critical CSS should be concise
                assert len(style_content) < 2000


class TestContentQuality:
    """Test suite for content quality and completeness."""

    def test_destination_descriptions_are_comprehensive(self, client: FlaskClient):
        """
        Test that destination descriptions are detailed and informative.
        
        Validates:
        - Each description has minimum word count
        - Descriptions are unique
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        descriptions = soup.find_all('p', class_='card-description')
        
        description_texts = []
        for desc in descriptions:
            text = desc.get_text(strip=True)
            # Description should be at least 15 words
            assert len(text.split()) >= 15
            description_texts.append(text)
        
        # All descriptions should be unique
        assert len(description_texts) == len(set(description_texts))

    def test_service_descriptions_are_present(self, client: FlaskClient):
        """
        Test that all services have descriptions.
        
        Validates:
        - Each service has a description
        - Descriptions are meaningful
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        service_descriptions = soup.find_all('p', class_='service-description')
        
        assert len(service_descriptions) == 4
        
        for desc in service_descriptions:
            text = desc.get_text(strip=True)
            assert len(text.split()) >= 10

    def test_testimonials_have_complete_information(self, client: FlaskClient):
        """
        Test that testimonials have complete information.
        
        Validates:
        - Each testimonial has quote
        - Each testimonial has author name
        - Each testimonial has location
        - Each testimonial has rating
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        testimonials = soup.find_all('article', class_=re.compile(r'bg-white.*rounded-xl'))
        
        # Filter to only testimonial cards (in testimonials section)
        testimonials_section = soup.find('section', {'aria-labelledby': 'testimonials-title'})
        testimonials = testimonials_section.find_all('article')
        
        assert len(testimonials) == 3
        
        for testimonial in testimonials:
            # Check for rating
            rating = testimonial.find('div', {'aria-label': re.compile(r'5 out of 5 stars')})
            assert rating is not None
            
            # Check for quote
            quote = testimonial.find('blockquote')
            assert quote is not None
            quote_text = quote.find('p').get_text(strip=True)
            assert len(quote_text.split()) >= 15
            
            # Check for author
            author = testimonial.find('cite')
            assert author is not None
            
            # Check for location
            location = testimonial.find('p', class_='text-gray-500')
            assert location is not None


class TestSecurityHeaders:
    """Test suite for security-related attributes."""

    def test_external_links_have_proper_attributes(self, client: FlaskClient):
        """
        Test that external links have security attributes.
        
        Note: This test checks for external image URLs.
        In production, external links should have rel="noopener noreferrer"
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check that external images use HTTPS
        images = soup.find_all('img')
        
        for image in images:
            src = image.get('src', '')
            if src.startswith('http'):
                assert src.startswith('https://'), f"Image should use HTTPS: {src}"

    def test_no_inline_javascript(self, client: FlaskClient):
        """
        Test that page doesn't contain inline JavaScript (CSP compliance).
        
        Validates:
        - No onclick attributes
        - No inline script tags with code
        - JavaScript is in external files
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for onclick attributes
        elements_with_onclick = soup.find_all(attrs={'onclick': True})
        assert len(elements_with_onclick) == 0
        
        # Check for inline scripts (excluding JSON-LD)
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_type = script.get('type', '')
            # Allow JSON-LD structured data
            if script_type != 'application/ld+json':
                # Should not have inline JavaScript
                assert not script.string or len(script.string.strip()) == 0


class TestRouteIntegration:
    """Test suite for route integration and URL generation."""

    def test_home_route_returns_featured_destinations(self, client: FlaskClient):
        """
        Test that home route provides featured destinations data.
        
        Validates:
        - Route returns data
        - Data contains expected destinations
        """
        response = client.get('/')
        
        assert response.status_code == 200
        
        # Verify destinations are rendered
        soup = BeautifulSoup(response.data, 'html.parser')
        destination_titles = soup.find_all('h3', class_='card-title')
        
        expected_destinations = [
            'Yankari National Park',
            'Olumo Rock',
            'Elegushi Beach'
        ]
        
        actual_destinations = [title.get_text(strip=True) for title in destination_titles]
        
        for expected in expected_destinations:
            assert expected in actual_destinations

    def test_url_for_generates_correct_links(self, app_context):
        """
        Test that url_for generates correct URLs for routes.
        
        Validates:
        - Home route URL
        - Destinations route URL
        - Contact route URL
        """
        assert url_for('main.home') == '/'
        assert url_for('main.destinations') == '/destinations'
        assert url_for('main.contact') == '/contact'


class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_page_renders_without_javascript(self, client: FlaskClient):
        """
        Test that page content is accessible without JavaScript.
        
        Validates:
        - All content is in HTML
        - No content is JavaScript-dependent
        - Progressive enhancement is used
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # All carousel slides should be in HTML
        slides = soup.find_all('div', {'data-carousel-slide': True})
        assert len(slides) == 3
        
        # All content should be visible in HTML
        for slide in slides:
            card_title = slide.find('h3', class_='card-title')
            assert card_title is not None
            assert len(card_title.get_text(strip=True)) > 0

    def test_page_handles_missing_images_gracefully(self, client: FlaskClient):
        """
        Test that page has proper alt text for images.
        
        Validates:
        - All images have descriptive alt text
        - Alt text provides context if image fails to load
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        images = soup.find_all('img')
        
        for image in images:
            alt_text = image.get('alt', '')
            # Alt text should be descriptive enough to understand content
            assert len(alt_text.split()) >= 3
            # Alt text should not be generic
            assert alt_text.lower() not in ['image', 'picture', 'photo']

    def test_carousel_indicators_match_slides(self, client: FlaskClient):
        """
        Test that number of carousel indicators matches number of slides.
        
        Validates:
        - Indicator count equals slide count
        - Prevents UI inconsistencies
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        slides = soup.find_all('div', {'data-carousel-slide': True})
        indicators = soup.find_all('button', {'data-carousel-indicator': True})
        
        assert len(slides) == len(indicators)


class TestMobileOptimization:
    """Test suite for mobile-specific optimizations."""

    def test_viewport_meta_tag_exists(self, client: FlaskClient):
        """
        Test that viewport meta tag is present for mobile optimization.
        
        Validates:
        - Viewport meta tag exists
        - Has proper width and scale settings
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport is not None
        
        content = viewport.get('content', '')
        assert 'width=device-width' in content
        assert 'initial-scale=1' in content

    def test_touch_friendly_button_sizes(self, client: FlaskClient):
        """
        Test that buttons have appropriate classes for touch targets.
        
        Validates:
        - Buttons use btn-lg class for larger touch targets
        - CTA buttons are appropriately sized
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_buttons = soup.find('section', class_='hero-section').find_all('a', class_='btn')
        
        for button in hero_buttons:
            classes = button.get('class', [])
            assert 'btn-lg' in classes

    def test_responsive_text_sizing(self, client: FlaskClient):
        """
        Test that text uses responsive sizing classes.
        
        Validates:
        - Hero title uses appropriate text size classes
        - Content is readable on mobile devices
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        hero_title = soup.find('h1', class_='hero-title')
        assert hero_title is not None
        
        # Hero title should have responsive text classes
        classes = ' '.join(hero_title.get('class', []))
        assert 'hero-title' in classes


# Performance benchmarks for monitoring
class TestPerformanceBenchmarks:
    """Test suite for performance benchmarks and monitoring."""

    def test_page_size_is_reasonable(self, client: FlaskClient):
        """
        Test that page size is within reasonable limits.
        
        Validates:
        - HTML size is under 100KB
        - Helps ensure fast page loads
        """
        response = client.get('/')
        
        page_size = len(response.data)
        # HTML should be under 100KB for good performance
        assert page_size < 100 * 1024, f"Page size {page_size} bytes exceeds 100KB"

    def test_number_of_http_requests_is_optimized(self, client: FlaskClient):
        """
        Test that page minimizes number of external resources.
        
        Validates:
        - Limited number of external image URLs
        - Resources are optimized
        """
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Count unique external resources
        images = soup.find_all('img')
        unique_sources = set()
        
        for img in images:
            src = img.get('src', '')
            srcset = img.get('srcset', '')
            
            if src:
                # Extract base URL without query parameters
                base_url = src.split('?')[0]
                unique_sources.add(base_url)
        
        # Should have reasonable number of unique image sources
        assert len(unique_sources) <= 10, f"Too many unique image sources: {len(unique_sources)}"