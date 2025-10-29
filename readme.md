## Overview
Speech Pacer is the evolution of the original [Pausing Information NVDA add-on](https://github.com/wendrillaksenow/pausingInformation). It keeps the same goal—making focus changes easier to follow—while replacing punctuation hacks with true synthesizer-managed pauses, adding richer configuration, and keeping braille and Speech History output intact. 

## Highlights
- Structured focus speech with synthesizer breaks between the name, type, state, shortcut, value, table position, and description of the focused control.
- Detail presets (Short, Medium, Long) plus a fully custom profile that lets you pick exactly which messages should read for each control type.
- Optional prefixes for shortcut keys and slider/scrollbar values so longer announcements stay easy to scan.
- Table awareness that announces headers, coordinates, and embedded values when NVDA exposes them.

## What is new compared to Pausing Information
- Real synthesizer break commands replace the old hyphen workaround.
- A configurable Pause between items setting (0–2000 ms) gives you direct control over the gap between chunks of information.
- Existing Pausing Information settings migrate automatically the first time Speech Pacer runs, making the upgrade seamless.

## Using Speech Pacer
Speech Pacer activates as soon as it is installed. By default, it speaks the same rich set of details long-time users expect from Pausing Information—only now the timing is handled by the synthesizer instead of symbol levels. You can toggle the add-on with `NVDA+Shift+P` (configurable from NVDA's Input Gestures dialog under Speech Pacer).

### Dialog options
- **Enable structured focus announcements:** Master switch that enables or disables Speech Pacer. Turning it off restores NVDA's default speech without uninstalling the add-on.
- **Allow the add-on to translate control and state names:** Uses Speech Pacer's internal dictionary instead of NVDA's built-in labels.
- **Announce shortcut keys:** Controls whether application-defined shortcut keys are spoken.
- **Message extension:** Short, Medium, Long, or Custom presets that determine how much context you hear.
- **Pause between items (milliseconds):** Sets the synthesizer break duration inserted between each piece of information.

### Custom profile
Choose the Custom message extension level and press **Configure…** to tailor Speech Pacer to your workflow:
- Pick which control types should report their type names.
- Toggle extras such as active window alerts or shortcut/value prefixes.
- Decide whether shortcuts are prefixed before their key or announced plainly.

### Additional behaviour
- When an object exposes selected text (documents, editable fields), the selection is spoken and very long passages are summarised by announcing the character count.
- For tables, grids, and menu items, column and row headers plus coordinates are announced once to give you the same context NVDA shows visually.
- Negative states (for example “not checked” or “off”) are spoken when they improve clarity and a translation exists.

## Compatibility
Speech Pacer works with NVDA 2019.3 and newer. It respects NVDA's speech, braille, and history infrastructure, so add-ons such as Speech History or output viewers continue to receive the exact text that was spoken.

If Pausing Information is still installed, the Speech Pacer installer offers to remove it automatically. All user settings are imported on first launch to smooth the transition.

## License
Speech Pacer is free software released under the GNU General Public License version 2.
