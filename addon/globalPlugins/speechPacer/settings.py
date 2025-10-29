import config as nvda_config
import gui
import wx
from gui import guiHelper, nvdaControls

from .constants import CONFIG_SECTION, CONTROL_TYPE_NAMES


class SpeechPacerSettingsPanel(gui.settingsDialogs.SettingsPanel):
	# Translators: The name of the panel in the NVDA settings dialog.
	title = _("Speech Pacer")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		self.enabledCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("&Enable paused reading of control types and states")))
		self.enabledCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["enabled"])
		self.enabledCheckbox.Bind(wx.EVT_CHECKBOX, self.onEnabledCheckbox)

		self.useCustomTranslations = sHelper.addItem(wx.CheckBox(self, label=_("&Allow the add-on to translate the names of control types and states")))
		self.useCustomTranslations.SetValue(nvda_config.conf[CONFIG_SECTION]["useCustomTranslations"])

		self.announceShortcutsCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("A&nnounce shortcut keys")))
		self.announceShortcutsCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["announceShortcuts"])

		messageExtensionGroupLabel = _("Message Extension")
		messageExtensionGroup = guiHelper.BoxSizerHelper(self, sizer=sHelper.addItem(wx.StaticBoxSizer(wx.VERTICAL, self, label=messageExtensionGroupLabel)))

		self.messageExtensionShort = messageExtensionGroup.addItem(wx.RadioButton(self, label=_("&Short"), style=wx.RB_GROUP))
		self.messageExtensionShort.SetValue(nvda_config.conf[CONFIG_SECTION]["messageExtension"] == 0)

		self.messageExtensionMedium = messageExtensionGroup.addItem(wx.RadioButton(self, label=_("&Medium")))
		self.messageExtensionMedium.SetValue(nvda_config.conf[CONFIG_SECTION]["messageExtension"] == 1)

		self.messageExtensionLong = messageExtensionGroup.addItem(wx.RadioButton(self, label=_("&Long")))
		self.messageExtensionLong.SetValue(nvda_config.conf[CONFIG_SECTION]["messageExtension"] == 2)

		self.messageExtensionCustom = messageExtensionGroup.addItem(wx.RadioButton(self, label=_("&Custom")))
		self.messageExtensionCustom.SetValue(nvda_config.conf[CONFIG_SECTION]["messageExtension"] == 3)

		self.pauseDurationSpin = sHelper.addLabeledControl(
			_("Pause between items (milliseconds):"),
			wx.SpinCtrl,
			min=0,
			max=2000,
			initial=nvda_config.conf[CONFIG_SECTION]["pauseDurationMs"]
		)

		self.configureButton = wx.Button(self, label=_("Configure..."))
		sHelper.addItem(self.configureButton)
		self.configureButton.Bind(wx.EVT_BUTTON, self.onConfigure)

		self.configureButton.Enable(nvda_config.conf[CONFIG_SECTION]["messageExtension"] == 3)

		self.messageExtensionShort.Bind(wx.EVT_RADIOBUTTON, self.updateConfigureButton)
		self.messageExtensionMedium.Bind(wx.EVT_RADIOBUTTON, self.updateConfigureButton)
		self.messageExtensionLong.Bind(wx.EVT_RADIOBUTTON, self.updateConfigureButton)
		self.messageExtensionCustom.Bind(wx.EVT_RADIOBUTTON, self.updateConfigureButton)

		self.updateControlState(nvda_config.conf[CONFIG_SECTION]["enabled"])

	def onEnabledCheckbox(self, event):
		self.updateControlState(event.IsChecked())

	def updateControlState(self, enabled):
		for control in [self.useCustomTranslations, self.messageExtensionShort, self.messageExtensionMedium,
						self.messageExtensionLong, self.messageExtensionCustom, self.announceShortcutsCheckbox,
						self.pauseDurationSpin]:
			control.Enable(enabled)

	def updateConfigureButton(self, event=None):
		self.configureButton.Enable(self.messageExtensionCustom.GetValue())

	def onConfigure(self, event):
		dlg = ConfigureDialog(self)
		dlg.ShowModal()
		dlg.Destroy()

	def onSave(self):
		nvda_config.conf[CONFIG_SECTION]["enabled"] = self.enabledCheckbox.GetValue()
		nvda_config.conf[CONFIG_SECTION]["useCustomTranslations"] = self.useCustomTranslations.GetValue()
		nvda_config.conf[CONFIG_SECTION]["announceShortcuts"] = self.announceShortcutsCheckbox.GetValue()
		if self.messageExtensionShort.GetValue():
			nvda_config.conf[CONFIG_SECTION]["messageExtension"] = 0
		elif self.messageExtensionMedium.GetValue():
			nvda_config.conf[CONFIG_SECTION]["messageExtension"] = 1
		elif self.messageExtensionLong.GetValue():
			nvda_config.conf[CONFIG_SECTION]["messageExtension"] = 2
		elif self.messageExtensionCustom.GetValue():
			nvda_config.conf[CONFIG_SECTION]["messageExtension"] = 3
		nvda_config.conf[CONFIG_SECTION]["pauseDurationMs"] = self.pauseDurationSpin.GetValue()


class ConfigureDialog(wx.Dialog):
	def __init__(self, parent):
		super(ConfigureDialog, self).__init__(parent, title=_("Settings for the custom message extension level"))
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

		sHelper.addItem(wx.StaticText(self, label=_("You can individually adjust all the information announced by the add-on")))

		controlsGroupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Types of control"))
		controlsGroupHelper = guiHelper.BoxSizerHelper(self, sizer=controlsGroupSizer)

		self.controlChoices = list(CONTROL_TYPE_NAMES.keys())
		controlDisplayNames = [CONTROL_TYPE_NAMES[role] for role in self.controlChoices]

		self.controlsList = controlsGroupHelper.addLabeledControl(
			_("Select the controls to be announced:"),
			nvdaControls.CustomCheckListBox,
			choices=controlDisplayNames
		)

		enabledControlsStr = nvda_config.conf[CONFIG_SECTION].get("enabledControls", "")
		enabledControls = [int(role) for role in enabledControlsStr.split(",")] if enabledControlsStr else []

		self.controlsList.CheckedItems = [
			i for i, role in enumerate(self.controlChoices) if role.value in enabledControls
		]

		sHelper.addItem(controlsGroupSizer, flag=wx.EXPAND)

		messagesGroupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Other additional messages"))
		messagesGroupHelper = guiHelper.BoxSizerHelper(self, sizer=messagesGroupSizer)

		self.announceActiveWindowsCheckbox = messagesGroupHelper.addItem(
			wx.CheckBox(self, label=_("Announce active windows"))
		)
		self.announceActiveWindowsCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["announceActiveWindows"])

		self.announceShortcutsCheckbox = messagesGroupHelper.addItem(
			wx.CheckBox(self, label=_("Announce shortcut keys"))
		)
		self.announceShortcutsCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["announceShortcuts"])

		self.prefixShortcutCheckbox = messagesGroupHelper.addItem(
			wx.CheckBox(self, label=_("Announce shortcut before object shortcut keys"))
		)
		self.prefixShortcutCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["announceShortcutPrefix"])
		self.prefixShortcutCheckbox.Enable(self.announceShortcutsCheckbox.GetValue())

		self.announceShortcutsCheckbox.Bind(wx.EVT_CHECKBOX, self.onToggleShortcuts)

		self.prefixValueCheckbox = messagesGroupHelper.addItem(
			wx.CheckBox(self, label=_("Announce value before slider and scrollbar values"))
		)
		self.prefixValueCheckbox.SetValue(nvda_config.conf[CONFIG_SECTION]["announceValuePrefix"])

		sHelper.addItem(messagesGroupSizer, flag=wx.EXPAND)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))

		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		self.SetSizer(mainSizer)
		mainSizer.Fit(self)
		self.CenterOnScreen()

		self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
		wx.CallAfter(self.controlsList.SetFocus)

	def GetSelections(self):
		selectedControls = [self.controlChoices[i].value for i in self.controlsList.CheckedItems]

		nvda_config.conf[CONFIG_SECTION]["announceActiveWindows"] = self.announceActiveWindowsCheckbox.GetValue()
		nvda_config.conf[CONFIG_SECTION]["announceShortcuts"] = self.announceShortcutsCheckbox.GetValue()
		nvda_config.conf[CONFIG_SECTION]["announceShortcutPrefix"] = self.prefixShortcutCheckbox.GetValue()
		nvda_config.conf[CONFIG_SECTION]["announceValuePrefix"] = self.prefixValueCheckbox.GetValue()

		return selectedControls

	def onToggleShortcuts(self, event):
		is_checked = event.IsChecked()
		if not is_checked:
			self.prefixShortcutCheckbox.SetValue(False)
		self.prefixShortcutCheckbox.Enable(is_checked)

	def OnOk(self, event):
		try:
			selectedControls = self.GetSelections()
			nvda_config.conf[CONFIG_SECTION]["enabledControls"] = ",".join(str(role) for role in selectedControls)
			nvda_config.conf.save()
		except Exception as e:
			wx.MessageBox(f"Error saving settings: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
		finally:
			self.EndModal(wx.ID_OK)

	def OnCancel(self, event):
		self.EndModal(wx.ID_CANCEL)
