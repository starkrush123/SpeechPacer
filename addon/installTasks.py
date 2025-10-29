import gui
import wx
import addonHandler

addonHandler.initTranslation()

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.name == "Pausing Information":
			result = gui.messageBox(
				# Translators: Displays a message to the user asking if they want to uninstall the previous version of the add-on
				_("An older Pausing Information build is still installed. Speech Pacer replaces it and cannot run until the previous package is removed. Would you like to uninstall the legacy version now?"),
				# Translators: question title
				_("Previous version found"),
				wx.YES_NO|wx.ICON_QUESTION, gui.mainFrame)
			if result == wx.YES:
				addon.requestRemove()
			else:
				raise Exception(_("Installation canceled by the user."))
