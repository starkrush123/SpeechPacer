import braille
import config as nvda_config
import controlTypes
import speech
import textInfos
import ui
import speech.priorities as speechPriorities
from speech import commands as speechCommands

from .constants import (
	CONFIG_SECTION,
	CONTROL_TYPE_NAMES,
	IGNORED_CONTROL_TYPES,
	IGNORED_STATES,
	NEGATIVE_STATE_NAMES,
	STATE_NAMES,
)


class SpeechPacerSpeechEngine:
	def __init__(self):
		self.last_menu_item = None
		self.last_menu_states = []

	def build_description_parts(self, obj, message_extension, enabled_controls=None):
		description_parts = []

		if obj.role in IGNORED_CONTROL_TYPES:
			return None

		if obj.name:
			description_parts.append(obj.name)

		if obj.role in [controlTypes.Role.COMBOBOX, controlTypes.Role.HOTKEYFIELD] and obj.value:
			description_parts.append(obj.value)

		if message_extension == 3 and enabled_controls and obj.role.value in enabled_controls:
			description_parts.append(self.get_control_type(obj))
		elif message_extension == 2:
			description_parts.append(self.get_control_type(obj))
		elif message_extension in [0, 1] and obj.role not in [controlTypes.Role.LISTITEM, controlTypes.Role.TREEVIEWITEM, controlTypes.Role.MENUITEM, controlTypes.Role.RADIOMENUITEM, controlTypes.Role.CHECKMENUITEM]:
			description_parts.append(self.get_control_type(obj))

		if obj.role in [
			controlTypes.Role.ALERT,
			controlTypes.Role.BUTTON,
			controlTypes.Role.CHECKBOX,
			controlTypes.Role.CHECKMENUITEM,
			controlTypes.Role.COMBOBOX,
			controlTypes.Role.DIALOG,
			controlTypes.Role.EDITABLETEXT,
			controlTypes.Role.GROUPING,
			controlTypes.Role.LINK,
			controlTypes.Role.LISTITEM,
			controlTypes.Role.MENUITEM,
			controlTypes.Role.MENUBAR,
			controlTypes.Role.MENUBUTTON,
			controlTypes.Role.PROPERTYPAGE,
			controlTypes.Role.RADIOBUTTON,
			controlTypes.Role.RADIOMENUITEM,
			controlTypes.Role.SCROLLBAR,
			controlTypes.Role.SPLITBUTTON,
			controlTypes.Role.SWITCH,
			controlTypes.Role.STATICTEXT,
			controlTypes.Role.TERMINAL,
			controlTypes.Role.TOGGLEBUTTON,
			controlTypes.Role.TOOLBAR,
		] and obj.description:
			description_parts.append(obj.description)

		relevant_states = self.get_relevant_states(obj, None)
		description_parts.extend(relevant_states)

		self.add_table_context(obj, description_parts)

		if obj.role in [controlTypes.Role.MENUITEM, controlTypes.Role.RADIOMENUITEM, controlTypes.Role.CHECKMENUITEM] and obj.value:
			self._append_if_missing(description_parts, obj.value)

		if obj.role in [controlTypes.Role.SLIDER, controlTypes.Role.SCROLLBAR] and obj.value:
			if message_extension == 3:
				if nvda_config.conf[CONFIG_SECTION]["announceValuePrefix"]:
					description_parts.append(_("Value: {value}").format(value=obj.value))
				else:
					description_parts.append(str(obj.value))
			elif message_extension > 0:
				description_parts.append(_("Value: {value}").format(value=obj.value))
			else:
				description_parts.append(str(obj.value))

		if nvda_config.conf[CONFIG_SECTION].get("announceShortcuts", True) and hasattr(obj, "keyboardShortcut") and obj.keyboardShortcut:
			if message_extension == 3:
				if nvda_config.conf[CONFIG_SECTION]["announceShortcutPrefix"]:
					description_parts.append(_("Shortcut: {shortcut}").format(shortcut=obj.keyboardShortcut))
				else:
					description_parts.append(str(obj.keyboardShortcut))
			elif message_extension > 0:
				description_parts.append(_("Shortcut: {shortcut}").format(shortcut=obj.keyboardShortcut))
			else:
				description_parts.append(str(obj.keyboardShortcut))

		if obj.role in [
			controlTypes.Role.BUTTON,
			controlTypes.Role.HEADING,
			controlTypes.Role.ICON,
			controlTypes.Role.LISTITEM,
			controlTypes.Role.MENUITEM,
			controlTypes.Role.RADIOMENUITEM,
			controlTypes.Role.CHECKMENUITEM,
			controlTypes.Role.SLIDER,
			controlTypes.Role.TAB,
			controlTypes.Role.TOGGLEBUTTON,
			controlTypes.Role.TREEVIEWITEM,
		]:
			position_info = self.get_position_info(obj)
			if position_info:
				description_parts.extend(position_info)

		if obj.role in [controlTypes.Role.DOCUMENT, controlTypes.Role.EDITABLETEXT, controlTypes.Role.STATICTEXT, controlTypes.Role.TERMINAL]:
			self.add_document_content(obj, description_parts)

		if obj.role in [controlTypes.Role.LISTITEM, controlTypes.Role.PROGRESSBAR] and obj.value:
			self._append_if_missing(description_parts, obj.value)

		if obj.role in [controlTypes.Role.DATAITEM, controlTypes.Role.TABLECELL] and obj.value:
			self._append_if_missing(description_parts, obj.value)

		return description_parts

	def speak_description(self, description_parts):
		parts = [part for part in description_parts if part]
		if not parts:
			return
		display_message = ", ".join(parts)
		break_command_cls = getattr(speechCommands, "BreakCommand", None)
		if not callable(break_command_cls):
			ui.message(display_message)
			return
		try:
			pause_duration = nvda_config.conf[CONFIG_SECTION].get("pauseDurationMs", 200)
			try:
				pause_duration = max(0, int(pause_duration))
			except Exception:
				pause_duration = 200
			sequence = []
			for index, part in enumerate(parts):
				if index and pause_duration:
					sequence.append(break_command_cls(pause_duration))
				sequence.append(part)
			end_command_cls = getattr(speechCommands, "EndUtteranceCommand", None)
			if callable(end_command_cls):
				sequence.append(end_command_cls())
			speech_module = getattr(speech, "speech", None)
			speak_func = getattr(speech_module, "speak", None) if speech_module else None
			if speak_func is None:
				speak_func = getattr(speech, "speak", None)
			if speak_func is None:
				raise RuntimeError("Unable to locate NVDA speech speak function")
			try:
				next_priority = getattr(speechPriorities.SpeechPriority, "NEXT", None)
				if next_priority is None:
					speak_func(sequence)
				else:
					speak_func(sequence, priority=next_priority)
			except TypeError:
				speak_func(sequence)
			try:
				braille.handler.message(display_message)
			except Exception:
				pass
		except Exception:
			ui.message(display_message)

	def get_relevant_states(self, obj, enabled_controls):
		relevant_states = []
		use_custom_translations = nvda_config.conf[CONFIG_SECTION]["useCustomTranslations"]

		last_obj = getattr(self, "last_menu_item", None)
		last_states = getattr(self, "last_menu_states", [])

		for state in obj.states:
			if state not in IGNORED_STATES:
				state_name = STATE_NAMES.get(state) if use_custom_translations else controlTypes.stateLabels.get(state)
				if not state_name:
					continue
				if state == controlTypes.State.HASPOPUP and controlTypes.State.COLLAPSED in obj.states and obj.role == controlTypes.Role.MENUITEM:
					continue
				if state in [controlTypes.State.UNAVAILABLE, controlTypes.State.CHECKED] and obj.role in [controlTypes.Role.MENUITEM, controlTypes.Role.RADIOMENUITEM, controlTypes.Role.CHECKMENUITEM]:
					if last_obj and last_obj.role in [controlTypes.Role.MENUITEM, controlTypes.Role.RADIOMENUITEM, controlTypes.Role.CHECKMENUITEM] and state_name in last_states:
						continue
				if enabled_controls is None or state_name in enabled_controls:
					if state == controlTypes.State.READONLY:
						if self.is_read_only_relevant(obj):
							relevant_states.append(state_name)
					else:
						relevant_states.append(state_name)

		negative_state = self.get_relevant_negative_state(obj)
		if negative_state and (enabled_controls is None or negative_state in enabled_controls):
			relevant_states.append(negative_state)

		if obj.role in [controlTypes.Role.MENUITEM, controlTypes.Role.RADIOMENUITEM, controlTypes.Role.CHECKMENUITEM]:
			self.last_menu_item = obj
			self.last_menu_states = relevant_states
		else:
			self.last_menu_item = None
			self.last_menu_states = []

		return relevant_states

	def is_read_only_relevant(self, obj):
		return obj.role in [
			controlTypes.Role.COMBOBOX,
			controlTypes.Role.DOCUMENT,
			controlTypes.Role.EDITABLETEXT,
			controlTypes.Role.SPINBUTTON,
		]

	def get_position_info(self, obj):
		position_info = []
		if obj.positionInfo:
			index = obj.positionInfo.get("indexInGroup")
			total = obj.positionInfo.get("similarItemsInGroup")
			level = obj.positionInfo.get("level")
			if index is not None and total is not None:
				position_info.append(_("{index} of {total}").format(index=index, total=total))
			if level is not None:
				position_info.append(_("Level {level}").format(level=level))
		return position_info

	def add_table_context(self, obj, description_parts):
		table_related_roles = {
			role
			for role in [
				getattr(controlTypes.Role, "DATAGRID", None),
				getattr(controlTypes.Role, "DATAITEM", None),
				getattr(controlTypes.Role, "TABLECELL", None),
				getattr(controlTypes.Role, "ROWHEADER", None),
				getattr(controlTypes.Role, "COLUMNHEADER", None),
			]
			if role is not None
		}
		if obj.role not in table_related_roles:
			return

		column_header = getattr(obj, "columnHeaderText", None)
		if column_header:
			self._append_if_missing(description_parts, column_header)

		row_header = getattr(obj, "rowHeaderText", None)
		if row_header:
			self._append_if_missing(description_parts, row_header)

		coords_text = getattr(obj, "tableCellCoordsText", None)
		if coords_text:
			self._append_if_missing(description_parts, coords_text)
		else:
			column_number = getattr(obj, "columnNumber", None)
			if column_number not in (None, -1):
				self._append_if_missing(description_parts, _("column {number}").format(number=column_number))
			row_number = getattr(obj, "rowNumber", None)
			if row_number not in (None, -1):
				self._append_if_missing(description_parts, _("row {number}").format(number=row_number))

	def announce_selected_text(self, obj):
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
			if not info.isCollapsed:
				selected_text = info.text
				if selected_text:
					if len(selected_text) > 512:
						ui.message(_("{chars} characters selected").format(chars=len(selected_text)))
					else:
						ui.message(_("Selected {text}").format(text=selected_text))
		except Exception:
			pass

	def get_control_type(self, obj):
		if nvda_config.conf[CONFIG_SECTION]["useCustomTranslations"]:
			return CONTROL_TYPE_NAMES.get(obj.role)
		return controlTypes.roleLabels.get(obj.role)

	def add_document_content(self, obj, description_parts):
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
			if info.isCollapsed:
				info = obj.makeTextInfo(textInfos.POSITION_CARET)
				info.expand(textInfos.UNIT_LINE)
				if info.text:
					description_parts.append(info.text)
		except Exception:
			if obj.value:
				description_parts.append(obj.value)

	def _append_if_missing(self, description_parts, text):
		if text in (None, ""):
			return
		if not isinstance(text, str):
			text = str(text)
		if text not in description_parts:
			description_parts.append(text)

	def get_relevant_negative_state(self, obj):
		if nvda_config.conf[CONFIG_SECTION]["useCustomTranslations"]:
			if obj.role in [controlTypes.Role.CHECKBOX, controlTypes.Role.CHECKMENUITEM]:
				return NEGATIVE_STATE_NAMES[controlTypes.State.CHECKED] if controlTypes.State.CHECKED not in obj.states else None
			if obj.role in [controlTypes.Role.RADIOBUTTON, controlTypes.Role.RADIOMENUITEM]:
				return NEGATIVE_STATE_NAMES[controlTypes.State.CHECKED] if controlTypes.State.CHECKED not in obj.states else None
			if obj.role == controlTypes.Role.TOGGLEBUTTON:
				return NEGATIVE_STATE_NAMES[controlTypes.State.PRESSED] if controlTypes.State.PRESSED not in obj.states else None
			if obj.role == controlTypes.Role.SWITCH:
				return NEGATIVE_STATE_NAMES[controlTypes.State.ON] if controlTypes.State.ON not in obj.states else None
			if obj.role in [controlTypes.Role.LISTITEM, controlTypes.Role.TAB, controlTypes.Role.TREEVIEWITEM]:
				return NEGATIVE_STATE_NAMES[controlTypes.State.SELECTED] if controlTypes.State.SELECTED not in obj.states else None
		else:
			if obj.role in [controlTypes.Role.CHECKBOX, controlTypes.Role.CHECKMENUITEM]:
				return controlTypes.negativeStateLabels[controlTypes.State.CHECKED] if controlTypes.State.CHECKED not in obj.states else None
			if obj.role in [controlTypes.Role.RADIOBUTTON, controlTypes.Role.RADIOMENUITEM]:
				return controlTypes.negativeStateLabels[controlTypes.State.CHECKED] if controlTypes.State.CHECKED not in obj.states else None
			if obj.role == controlTypes.Role.TOGGLEBUTTON:
				return controlTypes.negativeStateLabels[controlTypes.State.PRESSED] if controlTypes.State.PRESSED not in obj.states else None
			if obj.role == controlTypes.Role.SWITCH:
				return controlTypes.negativeStateLabels[controlTypes.State.ON] if controlTypes.State.ON not in obj.states else None
			if obj.role in [controlTypes.Role.LISTITEM, controlTypes.Role.TAB, controlTypes.Role.TREEVIEWITEM]:
				return controlTypes.negativeStateLabels[controlTypes.State.SELECTED] if controlTypes.State.SELECTED not in obj.states else None
		return None
