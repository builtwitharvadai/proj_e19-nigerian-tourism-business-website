from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def home():
    """
    Render homepage with featured destinations data.
    
    Returns:
        Rendered homepage template with sample destination data for carousel.
    """
    featured_destinations = [
        {
            'name': 'Yankari National Park',
            'description': 'Home to one of the largest surviving elephant populations in West Africa, Yankari offers incredible wildlife viewing and natural warm springs.',
            'image_url': 'https://images.unsplash.com/photo-1621522378876-887f8f5945b8?w=800&h=600&fit=crop&q=80',
            'location': 'Bauchi State'
        },
        {
            'name': 'Olumo Rock',
            'description': 'A historic natural fortress in Abeokuta offering breathtaking views, ancient caves, and rich Yoruba cultural heritage dating back centuries.',
            'image_url': 'https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?w=800&h=600&fit=crop&q=80',
            'location': 'Ogun State'
        },
        {
            'name': 'Elegushi Beach',
            'description': 'Lagos\'s premier beach destination featuring pristine sands, water sports, beachside dining, and vibrant entertainment for all ages.',
            'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=600&fit=crop&q=80',
            'location': 'Lagos State'
        }
    ]
    
    return render_template('index.html', featured_destinations=featured_destinations)


@main.route('/destinations')
def destinations():
    """Render destinations page."""
    return render_template('destinations.html')


@main.route('/services')
def services():
    """Render services page."""
    return render_template('services.html')


@main.route('/contact')
def contact():
    """Render contact page."""
    return render_template('contact.html')