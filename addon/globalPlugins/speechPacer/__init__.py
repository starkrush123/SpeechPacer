import addonHandler

addonHandler.initTranslation()

import config as nvda_config
import controlTypes
import gui
import speech
import ui
import globalPluginHandler
from scriptHandler import script

from .configuration import initialize_configuration
from .constants import CONFIG_SECTION
from .settings import SpeechPacerSettingsPanel
from .speech_engine import SpeechPacerSpeechEngine

initialize_configuration()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.speech_engine = SpeechPacerSpeechEngine()
		self.originalSpeakObject = speech.speakObject
		speech.speakObject = self.customSpeakObject
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SpeechPacerSettingsPanel)
		self.last_announced_window = None

	def terminate(self):
		speech.speakObject = self.originalSpeakObject
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SpeechPacerSettingsPanel)
		super(GlobalPlugin, self).terminate()

	@script(
		description=_("Toggles Speech Pacer on and off"),
		category=_("Speech Pacer"),
		gesture="kb:NVDA+shift+p"
	)
	def script_toggleSpeechPacer(self, gesture):
		nvda_config.conf[CONFIG_SECTION]["enabled"] = not nvda_config.conf[CONFIG_SECTION]["enabled"]
		message = _("Speech Pacer enabled") if nvda_config.conf[CONFIG_SECTION]["enabled"] else _("Speech Pacer disabled")
		ui.message(message)

	def event_foreground(self, obj, nextHandler):
		if not nvda_config.conf[CONFIG_SECTION]["enabled"]:
			nextHandler()
			return

		message_extension = nvda_config.conf[CONFIG_SECTION]["messageExtension"]
		announce_active_windows = nvda_config.conf[CONFIG_SECTION].get("announceActiveWindows", False)

		if message_extension == 3 and not announce_active_windows:
			nextHandler()
			return
		if message_extension < 2:
			nextHandler()
			return

		if obj.role in [controlTypes.Role.DIALOG, controlTypes.Role.PANE, controlTypes.Role.WINDOW]:
			if obj.name != self.last_announced_window:
				message = _("Window activated: {name}").format(name=obj.name if obj.name != "Program Manager" else " ")
				if obj.description:
					message += f", {obj.description}"
				nextHandler()
				ui.message(message)
				self.last_announced_window = obj.name
			return

		nextHandler()

	def customSpeakObject(self, obj, *args, **kwargs):
		if not nvda_config.conf[CONFIG_SECTION]["enabled"]:
			self.originalSpeakObject(obj, *args, **kwargs)
			return

		if obj.role in [controlTypes.Role.DIALOG, controlTypes.Role.PANE, controlTypes.Role.WINDOW] and obj.name == self.last_announced_window:
			self.last_announced_window = None
			return

		try:
			message_extension = nvda_config.conf[CONFIG_SECTION]["messageExtension"]
			enabled_controls_setting = nvda_config.conf[CONFIG_SECTION].get("enabledControls", "")
			enabled_controls = [
				int(role) for role in enabled_controls_setting.split(",") if role
			] if enabled_controls_setting else []

			description_parts = self.speech_engine.build_description_parts(
				obj,
				message_extension,
				enabled_controls if message_extension == 3 else None,
			)
			if description_parts is None:
				self.originalSpeakObject(obj, *args, **kwargs)
				return

			self.speech_engine.speak_description(description_parts)

			if obj.role in [controlTypes.Role.DOCUMENT, controlTypes.Role.EDITABLETEXT]:
				self.speech_engine.announce_selected_text(obj)
		except Exception:
			self.originalSpeakObject(obj, *args, **kwargs)

	def customEventGainFocus(self, obj, nextHandler):
		self.customSpeakObject(obj)
		nextHandler()
