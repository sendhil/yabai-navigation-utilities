# 0.0.7

- Added a `list-scratch-windows` command to output the currently saved windows.

# 0.0.6

- Added output for the `store` command to allow scripting that displays modifications. For example, this is what I have in my skhdrc `yabai-navigation-utilities store | jq 'if .result == "added_window" then "Added Window" else "Removed Window" end' | xargs -n 1 -I {} hs -c 'hs.alert.show("{}", 2)'`.

# 0.0.5

- Adjusting focus on window to no-op if the window already has focus.

# 0.0.2

- Fixing bug where installing utility would create a top line main.py within python site-packages.

# 0.0.1

- Initial version