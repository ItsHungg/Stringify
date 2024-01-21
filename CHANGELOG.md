# Changelog

All notable changes to this project will be documented in this file.<br>
(**Note:** The format is mostly based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/))

**Format:** `[x.y.z] - mm/dd/yyyy`
<hr>

## [1.3.0] - 08/12/2023
### Added
- Added logs to track application/user actions
- Added a console so users can run custom commands
- Added a tooltip for the no signal display button
- Added a platform/OS filter
- Added an information display window to display info/stats
### Changed
- Auto check for update option now has a timeout
- Loading window now follows the "Sticky setting" option
- The settings window won't close when a new theme is saved
- Plugin initializer (`__init__.py`) won't be executed when application started
- Users now can change font and font size
- Placeholder will be inserted if the main textbox loses focus by using the `esc` key
- Texts which are uploaded through file will be inserted, instead of deleting/clearing the whole textbox
- The insertion cursor will stay at the same position after changing cases
- All hotkeys will be cleared after the application is closed
- Save & Quit window now follows the "Sticky setting" option
- Changed "Original" case option to "Default"
- Improved auto check for update feature
- Reformatted/Improved the whole code
- Improved the pop-up (right-click) menu
### Fixed
- Fixed a bug when auto check for update option is disabled
- Fixed a bug when theme colors aren't displayed properly
- Fixed a bug at the Plugin Editor's buttons
- Fixed a small mistake at the Plugin Editor file browser
- Fixed a bug when application closes to soon, before the threading loops are closed
- Fixed a bug at the find feature
- Fixed the encoding error while writing files
- Fixed plenty of other bugs

## [1.2.0] - 07/29/2023
### Added
- Added alternative case converter
- Added a real-time internet checker
- Added a small timer to count elapsed time
- Added more options for config.txt file
- Added "Words without numbers" statistic
- Added "Occurrences" statistic for the find feature
- Added a pop-up (right click) menu for the main textbox
- Added an exit window
### Changed
- You can now modify, cut, copy, paste,... your text through the pop-up menu
- You can insert a sample text through the pop-up menu
- You can now upload text through files
- Improved the find feature
### Removed
- Removed sentence case converter (for maintenance)
### Fixed
- Fixed plenty of bugs

## [1.1.1] - 07/22/2023
### Fixed
- Fixed a problem with the auto check for updates feature

## [1.1.0] - 07/22/2023
### Added
- Added a setting option for auto-check for updates
- Added 1 attribute (command) to config.txt
### Changed
- Changed [data site](https://clients-data.netlify.app)
- Changed the [changelog hyperlink site](https://github.com/ItsHungg/Stringify/blob/main/CHANGELOG.md)
- Users can automatically add `__init__.py` file while adding a plugin instead of opening the manage window
### Fixed
- Fixed a bug at the no-signal warning messagebox
- Fixed a small bug at the Viewer of Theme Editor 1.1
- Fixed a bug at the while-loops detector (beta)

## [1.0.1] - 07/20/2023
### Fixed
- Fixed a bug at the initialization

## [1.0.0] - 07/20/2023
### Added
- Initial commit

<hr>

# ToDo List
- Improve the Manage Plugins Windows
- Add replace text feature
- Finish the website for Stringify
