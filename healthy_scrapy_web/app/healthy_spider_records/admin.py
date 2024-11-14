from django.contrib import admin

from common.csv_tools import ClinicPointRecordsCSVDownloadView, QuironRecordsCSVDownloadView, \
    SaludOnNetRecordsCSVDownloadView, SmartSalusRecordsCSVDownloadView, IglobalmedRecordsCSVDownloadView, \
    OperarmeRecordCSVDownloadView, MiDiagnosticoRecordsCSVDownloadView, BonomedicoCSVDownloadView, \
    PortalsaludSanitasCSVDownloadView
from healthy_spider_records.models import QuironRecord, SaludonnetRecord, ClinicPointRecord, SmartSalusRecord, \
    IglobalmedRecord, OperarmeRecord, MiDiagnosticoRecord, BonomedicoRecord, PortalsaludSanitasRecord


def quiron_export_all_csv(ma, request, queryset):
    quiron_csv = QuironRecordsCSVDownloadView()
    return quiron_csv.get(request)


@admin.register(QuironRecord)
class QuironRecordAdmin(admin.ModelAdmin):
    list_display = ('type_product_name', 'product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'type_product_name', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name',)
    readonly_fields = ['creation_timestamp', ]
    quiron_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [quiron_export_all_csv]


def saludonnet_export_all_csv(ma, request, queryset):
    salud_csv = SaludOnNetRecordsCSVDownloadView()
    return salud_csv.get(request)


@admin.register(SaludonnetRecord)
class SaludonnetRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    saludonnet_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [saludonnet_export_all_csv]


def clinicpoint_export_all_csv(ma, request, queryset):
    salud_csv = ClinicPointRecordsCSVDownloadView()
    return salud_csv.get(request)


@admin.register(ClinicPointRecord)
class ClinicPointRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    clinicpoint_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [clinicpoint_export_all_csv]


def smart_salus_export_all_csv(ma, request, queryset):
    salud_csv = SmartSalusRecordsCSVDownloadView()
    return salud_csv.get(request)


@admin.register(SmartSalusRecord)
class SmartSalusRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    smart_salus_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [smart_salus_export_all_csv]


def iglobalmed_export_all_csv(ma, request, queryset):
    iglobalmed_csv = IglobalmedRecordsCSVDownloadView()
    return iglobalmed_csv.get(request)


@admin.register(IglobalmedRecord)
class IglobalmedRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'city', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'city',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    iglobalmed_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [iglobalmed_export_all_csv]


def operarme_export_all_csv(ma, request, queryset):
    operarme_csv = OperarmeRecordCSVDownloadView()
    return operarme_csv.get(request)


@admin.register(OperarmeRecord)
class OperarmeRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'city', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'city',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    operarme_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [operarme_export_all_csv]


def midiagnostico_export_all_csv(ma, request, queryset):
    salud_csv = MiDiagnosticoRecordsCSVDownloadView()
    return salud_csv.get(request)


@admin.register(MiDiagnosticoRecord)
class MiDiagnosticoRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    midiagnostico_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [midiagnostico_export_all_csv]


def bonomedico_export_all_csv(ma, request, queryset):
    salud_csv = BonomedicoCSVDownloadView()
    return salud_csv.get(request)


@admin.register(BonomedicoRecord)
class BonomedicoRecordRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    bonomedico_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [bonomedico_export_all_csv]


def portalsalud_sanitas_export_all_csv(ma, request, queryset):
    salud_csv = PortalsaludSanitasCSVDownloadView()
    return salud_csv.get(request)


@admin.register(PortalsaludSanitasRecord)
class PortalsaludSanitasRecordRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'speciality_name', 'province_name', 'center',)
    list_filter = ('creation_timestamp', 'last_update_timestamp', 'gender', 'speciality_name', 'province_name',)
    search_fields = ('product_name', 'speciality_name', 'center')
    readonly_fields = ['creation_timestamp', 'last_update_timestamp']
    portalsalud_sanitas_export_all_csv.short_description = 'Exportar todos a CSV'
    actions = [portalsalud_sanitas_export_all_csv]
