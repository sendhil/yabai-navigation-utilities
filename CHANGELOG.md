# 0.0.14

- Tweaked `swap-spaces` to allow 1 or 2 arguments.

# 0.0.13

- Tweaked `swap-spaces` to only require a single spacet:w.

# 0.0.12

- Added a `swap-spaces` command which will swap all the windows between two spaces.

# 0.0.11

- Added a `swap-displays` command which will swap the windows between two monitors.

# 0.0.10

- Fixed a bug where `recent-space` didn't work properly if the most recent space had an unmanaged window.

# 0.0.9

- Fixed a bug with `toggle` introduced by 0.0.8.
# 0.0.8

- Added a `list-scratch-windows` command to output the currently saved windows.

# 0.0.6

- Added output for the `store` command to allow scripting that displays modifications. For example, this is what I have in my skhdrc `yabai-navigation-utilities store | jq 'if .result == "added_window" then "Added Window" else "Removed Window" end' | xargs -n 1 -I {} hs -c 'hs.alert.show("{}", 2)'`.

# 0.0.5

- Adjusting focus on window to no-op if the window already has focus.

# 0.0.2

- Fixing bug where installing utility would create a top line main.py within python site-packages.

# 0.0.1

- Initial version
