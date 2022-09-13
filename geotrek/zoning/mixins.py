from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from geotrek.common.utils import intersecting, uniquify
from .models import RestrictedArea, District, City


class ZoningPropertiesMixin:
    areas_verbose_name = _("Restricted areas")

    @cached_property
    def zoning_property(self):
        return self

    @cached_property
    def areas(self):
        return uniquify(intersecting(RestrictedArea, self.zoning_property, distance=0, defer=('geom',)))

    @cached_property
    def districts(self):
        return uniquify(intersecting(District, self.zoning_property, distance=0, defer=('geom',)))

    @cached_property
    def cities(self):
        return uniquify(intersecting(City, self.zoning_property, distance=0, defer=('geom',)))

    @cached_property
    def published_areas(self):
        if not hasattr(self, 'published'):
            return self.areas
        return [area for area in self.areas if area.published]

    @cached_property
    def published_districts(self):
        if not hasattr(self, 'published'):
            return self.districts
        return [district for district in self.districts if district.published]

    @cached_property
    def published_cities(self):
        if not hasattr(self, 'published'):
            return self.cities
        return [city for city in self.cities if city.published]
