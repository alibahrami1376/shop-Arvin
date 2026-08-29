from core.caching import get_contact_settings, get_site_branding, get_site_social_links
from website.logo_validation import SITE_LOGO_HEIGHT, SITE_LOGO_WIDTH


def site_branding(request):
    branding = get_site_branding()
    contact = get_contact_settings()
    return {
        "site_branding": branding,
        "site_logo_width": SITE_LOGO_WIDTH,
        "site_logo_height": SITE_LOGO_HEIGHT,
        "site_wide_social_links": get_site_social_links(),
        "contact_settings": contact,
        "contact_phone_tel": contact.get_phone_tel_href(),
    }
