import config as nvda_config
from logHandler import log

from .constants import CONFIG_SECTION, LEGACY_CONFIG_SECTION

CONFSPEC = {
	"useCustomTranslations": "boolean(default=True)",
	"messageExtension": "integer(min=0,max=3,default=2)",
	"enabled": "boolean(default=True)",
	"announceActiveWindows": "boolean(default=False)",
	"announceShortcuts": "boolean(default=True)",
	"announceShortcutPrefix": "boolean(default=False)",
	"announceValuePrefix": "boolean(default=False)",
	"enabledControls": "string(default='')",
	"pauseDurationMs": "integer(min=0,max=2000,default=200)",
}


def register_config_spec():
	nvda_config.conf.spec[CONFIG_SECTION] = CONFSPEC


def migrate_legacy_settings():
	if LEGACY_CONFIG_SECTION in nvda_config.conf and CONFIG_SECTION not in nvda_config.conf:
		try:
			nvda_config.conf[CONFIG_SECTION] = nvda_config.conf[LEGACY_CONFIG_SECTION]
			del nvda_config.conf[LEGACY_CONFIG_SECTION]
			nvda_config.conf.save()
		except Exception:
			log.exception("Speech Pacer: failed to migrate legacy settings")


def initialize_configuration():
	register_config_spec()
	migrate_legacy_settings()
