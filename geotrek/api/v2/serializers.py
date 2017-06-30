# coding: utf8

from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


class Base3DSerializer(object):
    """
    Mixin use to replace geom with geom_3d field
    """
    geometry = geo_serializers.GeometryField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom3d_transformed


class BaseGeoJSONSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Mixin use to serialize in geojson
    """
    class Meta:
        geo_field = 'geometry'
        auto_bbox = True


class FileTypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = common_models.FileType
        fields = ('type')


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    file_type = FileTypeSerializer(read_only=True)

    class Meta:
        model = common_models.Attachment
        fields = ('file_type', 'attachment_file', 'creator', 'author', 'title', 'legend', 'starred',
                  'date_insert', 'date_update')


class TouristicContentCategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'pictogram', 'type1_label', 'type2_label', 'order')


class TouristicContentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:touristiccontent-detail')
    category = TouristicContentCategorySerializer()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        location = obj.geom.transform(settings.API_SRID, clone=True)
        return {
            'latitude': location.y,
            'longitude': location.x
        }

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'url', 'description_teaser', 'description', 'category', 'approved', 'location')


class TouristicContentGeoSerializer(TouristicContentSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TouristicContentSerializer.Meta):
        geo_field = 'geom'


class TouristicContentDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    category = TouristicContentCategorySerializer()
    pictures = serializers.SerializerMethodField()

    def get_pictures(self, obj):
        return obj.serializable_pictures

    class Meta:
        model = tourism_models.TouristicContent
        fields = (
            'id', 'description_teaser', 'description', 'themes',
            'category', 'contact', 'email', 'website', 'practical_info',
            'source', 'portal', 'eid', 'reservation_id', 'approved',
            'pictures', 'geom'
        )


class TouristicContentGeoDetailSerializer(TouristicContentDetailSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TouristicContentDetailSerializer.Meta):
        geo_field = 'geom'


class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    length = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SerializerMethodField(read_only=True)

    def get_update_datetime(self, obj):
        return obj.topo_object.date_update

    def get_create_datetime(self, obj):
        return obj.topo_object.date_insert

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: "{}".format(getattr(obj, 'name_{}'.format(language)))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_description_teaser(self, obj):
        teasers = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            teasers.update({language: getattr(obj, 'description_teaser_{}'.format(language))})

        return teasers

    def get_length(self, obj):
        return obj.topo_object.length_2d

    def get_difficulty(self, obj):
        return obj.difficulty.difficulty if obj.difficulty else None

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'description_teaser',
            'description', 'duration', 'difficulty',
            'length', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'url',
            'geometry', 'update_datetime', 'create_datetime'
        )


class RoamingListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:roaming-detail')
    last_modified = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SlugRelatedField(slug_field='difficulty', read_only=True)

    def get_last_modified(self, obj):
        # return obj.last_author.logentry_set.last().action_time
        return obj.topo_object.date_update

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'url', 'last_modified', 'practice',
            'difficulty', 'themes', 'networks', 'accessibilities',
        )


class TrekDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    length = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SerializerMethodField(read_only=True)
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: getattr(obj, 'name_{}'.format(language))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_description_teaser(self, obj):
        teasers = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            teasers.update({language: getattr(obj, 'description_teaser_{}'.format(language))})

        return teasers

    def get_length(self, obj):
        return obj.topo_object.length_2d

    def get_pictures(self, obj):
        return obj.serializable_pictures

    def get_difficulty(self, obj):
        return obj.difficulty.difficulty if obj.difficulty else None

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'description_teaser', 'description',
            'duration', 'difficulty', 'length', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'pictures', 'geometry'
        )


class RoamingDetailSerializer(TrekDetailSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def get_children(self, obj):
        return TrekDetailSerializer(obj.children.transform(settings.API_SRID, field_name='geom'), many=True).data

    class Meta(TrekDetailSerializer.Meta):
        fields = TrekDetailSerializer.Meta.fields + ('children',)


class POIListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:poi-detail')
    description = serializers.SerializerMethodField(read_only=True)
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

    def get_update_datetime(self, obj):
        return obj.topo_object.date_update

    def get_create_datetime(self, obj):
        return obj.topo_object.date_insert

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = trekking_models.POI
        fields = ('id','url', 'description', 'geometry', 'update_datetime', 'create_datetime')


class POITypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        labels = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            labels.update({language: getattr(obj, 'label_{}'.format(language))})

        return labels

    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'label', 'pictogram')


class POIDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    type = POITypeSerializer(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: getattr(obj, 'name_{}'.format(language))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_pictures(self, obj):
        return obj.serializable_pictures

    class Meta:
        model = trekking_models.POI
        fields = "__all__"
