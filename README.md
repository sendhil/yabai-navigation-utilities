# Yabai Navigation Utilities

I made this CLI to hold for a few utilities that make Yabai feel more like i3wm to me. The primary use case when I set out to write this was to recreate the scratch window feature from i3wm. Along the way I decided to try to tweak a few things about Yabai that I wished were more i3wm like and thus this CLI was born (e.g. multiple monitors, clunky integration with alt-tab). 

**Note** - this version is very rough and early, so I can't promise to keep the CLI surface stable. I may try to combine it with https://github.com/sendhil/yabai-stack-navigator which I wrote previously to simplify how to navigate stacks in Yabai.

# Installation

```
pip install yabai-navigation-utilities
```

# Usage

**"Scratch" Windows**

To use this, you'll want to use `store` and `toggle` commands. `store` will add the currently active window to a list of windows that the utility is tracking (persists this info to disk). Calling `toggle` will cycle through the list, pulling the next window on the list into the current space and sending the current one back to it's original space. Unlike i3wm, these windows aren't hidden completely from view, but rather live in another space. For my purposes I found this to be good enough but at some point I may try to invest in actually hiding these windows. 

Here's a video demonstrating this:

![CleanShot 2022-09-22 at 22 39 05](https://user-images.githubusercontent.com/437043/191898782-56e925d4-1b45-4d6a-8e32-d2bb7bc2cefb.gif)

Note that the "Added Window"/"Removed Window" isn't baked into the CLI but something I added to my skhd configuration, e.g. `yabai-navigation-utilities store | jq 'if .result == "added_window" then "Added Window" else "Removed Window" end' | xargs -n 1 -I {} hs -c 'hs.alert.show("{}", 2)'`

**Other Utilities**

- `focus` this will focus on a space by focusing on the first window within that space (and without needing to disable SIP like `yabai -m space --focus 2` does). This was added because the use case I was trying to deal with was trying to focus on a space that's already visible in a multi monitor situation. MacOS has a shortcut that lets you shift over to a space and focus on a window there, but it doesn't do anything if the space is currently visible. I hated having to use my mouse to move between multiple monitors with yabai so I added this and it lets me very trivially jump between monitors. Note that this command only works if there's a window visible on the space so see details below on a sample configuration to get around this in conjunction with skhd. 
- `recent-space` this exists to sort of streamline alt-tab for me as I found the MacOS alt-tab to be less than reliable with yabai. I also added this because yabai requires SIP to be disabled to use this. 

# Example Configuration

**Scratch Windows**

Here's how I have scratch windows setup. To use this properly, I mark a few windows that I want to cycle through at any time with `alt+shift+backspace` and then when I want to pull them into view press `alt+backspace`. 

```
# Note - 0x33 is backspace
alt - 0x33: yabai-navigation-utilities/main.py toggle
shift + alt - 0x33: yabai-navigation-utilities/main.py store
```


**Focusing with multiple monitors**

My typical setup has 10 spaces for my primary monitor, and 1 for the second monitor. Here's how I set things up in conjunction with skhd to get around the limitation of only being able to focus on a space with a window while gaining the ability to jump between multiple visible monitors:

```
alt - 1: skhd -k "shift + alt + ctrl - 1" && yabai-navigation-utilities focus 1
alt - 2: skhd -k "shift + alt + ctrl - 2" && yabai-navigation-utilities focus 2
alt - 3: skhd -k "shift + alt + ctrl - 3" && yabai-navigation-utilities focus 3
alt - 4: skhd -k "shift + alt + ctrl - 4" && yabai-navigation-utilities focus 4
alt - 5: skhd -k "shift + alt + ctrl - 5" && yabai-navigation-utilities focus 5
alt - 6: skhd -k "shift + alt + ctrl - 6" && yabai-navigation-utilities focus 6
alt - 7: skhd -k "shift + alt + ctrl - 7" && yabai-navigation-utilities focus 7
alt - 8: skhd -k "shift + alt + ctrl - 8" && yabai-navigation-utilities focus 8
alt - 9: skhd -k "shift + alt + ctrl - 9" && yabai-navigation-utilities focus 9
alt - 0: skhd -k "shift + alt + ctrl - 0" && yabai-navigation-utilities focus 0
alt - 0x1B: yabai-navigation-utilities focus 11
```

The trick here is that the "shift + alt + ctrl + num" shortcut is bound in MacOS Keyboard Shortcuts to switch the space and the `&& ..` makes sure we focus on the first visible window (which doesn't happen with the MacOS shortcut alone if you can already see the space).

**Focusing on Recent Space (aka alt-tab alternate)**

```
alt - tab: yabai-navigation-utilities/main.py recent-space
```
