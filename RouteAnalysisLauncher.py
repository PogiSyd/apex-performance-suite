def get_cards(fit_file):
    """Math engine for GPS and Elevation data"""
    cards = [
        {"type": "stat", "title": "Total Ascent", "value": "2,450m", "trend": "3 Peaks Level"},
        {"type": "interactive_route", "title": "Ride Map", 
         "path": [[-36.75, 147.28], [-36.80, 147.30]]} # Sample Lat/Lon
    ]
    return cards
