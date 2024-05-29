"""Constant for the eco-devices integration."""

DOMAIN = "ecodevices"

CONTROLLER = "controller"
COORDINATOR = "coordinator"
PLATFORMS = ["binary_sensor", "sensor"]
UNDO_UPDATE_LISTENER = "undo_update_listener"

CONF_T1_ENABLED = "t1_enabled"
CONF_T1_TYPE = "t1_type"
CONF_T2_ENABLED = "t2_enabled"
CONF_T2_TYPE = "t2_type"
CONF_C1_ENABLED = "c1_enabled"
CONF_C1_UNIT_OF_MEASUREMENT = "c1_unit_of_measurement"
CONF_C1_DIVIDER_FACTOR = "c1_divider_factor"
CONF_C1_TOTAL_UNIT_OF_MEASUREMENT = "c1_total_unit_of_measurement"
CONF_C1_DEVICE_CLASS = "c1_device_class"
CONF_C2_ENABLED = "c2_enabled"
CONF_C2_UNIT_OF_MEASUREMENT = "c2_unit_of_measurement"
CONF_C2_DIVIDER_FACTOR = "c2_divider_factor"
CONF_C2_TOTAL_UNIT_OF_MEASUREMENT = "c2_total_unit_of_measurement"
CONF_C2_DEVICE_CLASS = "c2_device_class"

DEFAULT_T1_NAME = "Teleinfo 1"
DEFAULT_T2_NAME = "Teleinfo 2"
DEFAULT_C1_NAME = "Meter 1"
DEFAULT_C2_NAME = "Meter 2"
DEFAULT_SCAN_INTERVAL = 5

CONF_TI_TYPE_BASE = "base"
CONF_TI_TYPE_HCHP = "hchp"
CONF_TI_TYPE_TEMPO = "tempo"
CONF_TI_TYPES = [
    CONF_TI_TYPE_BASE,
    CONF_TI_TYPE_HCHP,
    CONF_TI_TYPE_TEMPO,
]

TELEINFO_EXTRA_ATTR = {
    "type_heures": "PTEC",
    "souscription": "ISOUSC",
    "intensite_max": "IMAX",
    "intensite_max_ph1": "IMAX1",
    "intensite_max_ph2": "IMAX2",
    "intensite_max_ph3": "IMAX3",
    "intensite_now": "IINST",
    "intensite_now_ph1": "IINST1",
    "intensite_now_ph2": "IINST2",
    "intensite_now_ph3": "IINST3",
    "conso_instant_general": "PPAP",
    "puissance_apparente": "PAPP",
    "avertissement_depassement": "ADPS",
    "numero_compteur": "ADCO",
    "option_tarifaire": "OPTARIF",
    "index_base": "BASE",
    "etat": "MOTDETAT",
    "presence_potentiels": "PPOT",
    # HCHP
    "index_heures_creuses": "HCHC",
    "index_heures_pleines": "HCHP",
    "index_heures_normales": "EJPHN",
    "index_heures_pointes": "EJPHPM",
    "preavis_heures_pointes": "PEJP",
    "groupe_horaire": "HHPHC",
    # Tempo
    "index_heures_creuses_jour_bleu": "BBRHCJB",
    "index_heures_pleines_jour_bleu": "BBRHPJB",
    "index_heures_creuses_jour_blanc": "BBRHCJW",
    "index_heures_pleines_jour_blanc": "BBRHPJW",
    "index_heures_creuses_jour_rouge": "BBRHCJR",
    "index_heures_pleines_jour_rouge": "BBRHPJR",
    "type_heures_demain": "DEMAIN",
}
TELEINFO_TEMPO_ATTR = {
    "Jour Bleu HC": "BBRHCJB",
    "Jour Bleu HP": "BBRHPJB",
    "Jour Blanc HC": "BBRHCJW",
    "Jour Blanc HP": "BBRHPJW",
    "Jour Ro" + "uge HC": "BBRHCJR",  # bypass codespell
    "Jour Ro" + "uge HP": "BBRHPJR",  # bypass codespell
}
