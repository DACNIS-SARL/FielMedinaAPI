from django.dispatch import receiver
from django.db.models.signals import post_save
from cities_light.signals import city_items_pre_import
import logging

logger = logging.getLogger(__name__)

ALLOWED_CITIES = {
    'TN': [ # Tunisia
        'Sousse', 'Sfax', 'Tunis', 'Kairouan', 'Monastir', 'Mahdia'
    ],
    'MA': [ # Morocco
        'Fez', 'Marrakesh', 'Essaouira', 'Tétouan', 'Rabat', 'Meknes'
    ],
    'DZ': [ # Algeria
        'Algiers', 'Ghardaïa'
    ],
    'LY': [ # Libya
        'Tripoli'
    ],
    'EG': [ # Egypt
        'Cairo'
    ],
    'LB': [ # Lebanon
        'Tripoli', 'Sidon'
    ],
    'YE': [ # Yemen
        "Sana'a"
    ],
    'SY': [ # Syria
        'Damascus', 'Aleppo'
    ]
}

@receiver(city_items_pre_import)
def filter_cities(sender, items, **kwargs):
    country_code = items[0] 
    
    name = items[1]
    country = items[8]
    
    if country in ALLOWED_CITIES:
        allowed_list = ALLOWED_CITIES[country]
        asciiname = items[2]
        
        if name in allowed_list or asciiname in allowed_list:
            return # Keep it
        
        if country == 'YE' and "Sana'a" in allowed_list:
             if name in ["Sana'a", "Sanaa", "Sana"]:
                 return

        if country == 'LB' and 'Sidon' in allowed_list:
            if name in ['Sidon', 'Saida']:
                return
                
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()
    else:
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()


# Import models and notification service at the end to avoid circular imports
def register_notification_signals():
    """Register signals for sending push notifications"""
    from guard.models import Location, Event, Hiking, Tip
    from guard.notifications import NotificationService

    @receiver(post_save, sender=Location)
    def location_created(sender, instance, created, **kwargs):
        """Send notification when a new location is created"""
        if created:
            try:
                logger.info(f"Sending notification for new location: {instance.id}")
                NotificationService.send_new_location_notification(instance)
            except Exception as e:
                logger.error(f"Error in location_created signal: {e}", exc_info=True)

    @receiver(post_save, sender=Event)
    def event_created(sender, instance, created, **kwargs):
        """Send notification when a new event is created"""
        if created:
            try:
                logger.info(f"Sending notification for new event: {instance.id}")
                NotificationService.send_new_event_notification(instance)
            except Exception as e:
                logger.error(f"Error in event_created signal: {e}", exc_info=True)

    @receiver(post_save, sender=Hiking)
    def hiking_created(sender, instance, created, **kwargs):
        """Send notification when a new hiking trail is created"""
        if created:
            try:
                logger.info(f"Sending notification for new hiking: {instance.id}")
                NotificationService.send_new_hiking_notification(instance)
            except Exception as e:
                logger.error(f"Error in hiking_created signal: {e}", exc_info=True)

    @receiver(post_save, sender=Tip)
    def tip_created(sender, instance, created, **kwargs):
        """Send notification when a new tip is created"""
        if created:
            try:
                logger.info(f"Sending notification for new tip: {instance.id}")
                NotificationService.send_new_tip_notification(instance)
            except Exception as e:
                logger.error(f"Error in tip_created signal: {e}", exc_info=True)


# Register notification signals
register_notification_signals()

