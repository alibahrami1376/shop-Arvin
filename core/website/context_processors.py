from website.logo_validation import SITE_LOGO_HEIGHT, SITE_LOGO_WIDTH
from website.models import SiteBrandingSettings, SiteWideSocialSettings


def site_branding(request):
    branding = SiteBrandingSettings.get_solo()
    social = SiteWideSocialSettings.get_solo()
    return {
        "site_branding": branding,
        "site_logo_width": SITE_LOGO_WIDTH,
        "site_logo_height": SITE_LOGO_HEIGHT,
        "site_wide_social_links": social.get_links(),
    }
