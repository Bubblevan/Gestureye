import sys
import applescript
import pyautogui

def execute_applescript(script):
    """Executes an AppleScript command."""
    try:
        script_obj = applescript.AppleScript(script)
        result = script_obj.run()
        print(f"AppleScript result: {result}")
        return True
    except applescript.ScriptError as e:
        print(f"Error executing AppleScript: {e}", file=sys.stderr)
        return False


# --- Window Management Functions ---

# 1. 窗口全屏
def toggle_fullscreen():
    script = """
    tell application "System Events"
        key code 0 using {command down, control down}
    end tell
    """
    return execute_applescript(script)

# 2. 窗口最小化
def minimize_window():
    script = """
    tell application "System Events" to key code 46 using {command down}
    """
    return execute_applescript(script)

# 3. 窗口拖动
def move_window(dx, dy):

    # First, get information about the frontmost application
    app_info_script = """
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set frontAppName to name of frontApp
        return frontAppName
    end tell
    """

    try:
        script_obj = applescript.AppleScript(app_info_script)
        app_name = script_obj.run()
        print(f"Current frontmost application: {app_name}")
    except applescript.ScriptError as e:
        print(f"Error getting frontmost application: {e}", file=sys.stderr)
        return

    # Now try to move the window
    move_script = f"""
    try
        tell application "System Events"
            tell process "{app_name}"
                if (count of windows) is 0 then 
                    return "No windows found in {app_name}"
                end if
                
                tell first window
                    set windowPosition to position
                    set oldX to item 1 of windowPosition
                    set oldY to item 2 of windowPosition
                    set newX to oldX + {dx}
                    set newY to oldY + {dy}
                    set position to {{newX, newY}}
                    set finalPosition to position
                    return "Window moved from: " & oldX & "," & oldY & " to " & (item 1 of finalPosition) & "," & (item 2 of finalPosition)
                end tell
            end tell
        end tell
    on error errMsg
        return "Error moving window: " & errMsg
    end try
    """
    return execute_applescript(move_script)

# 4. 切换窗口
def switch_window():
    script = """
    tell application "System Events"
        key code 48 using {command down}
    end tell
    """
    return execute_applescript(script)


# 5. 关闭当前窗口
def close_window():
    script = """
    tell application "System Events"
        key code 13 using {command down}
    end tell
    """
    return execute_applescript(script)

# 6. 滚动窗口
def scroll_window(amount):
    pyautogui.scroll(amount)

# 7. 设置音量为静音
def set_volume_to_mute():
    script = "set volume with output muted"
    return execute_applescript(script)

# 8. 增大音量
def increase_volume():
    script = "set volume output volume (output volume of (get volume settings) + 10)"
    return execute_applescript(script)

# 9. 减小音量
def decrease_volume():
    script = "set volume output volume (output volume of (get volume settings) - 10)"
    return execute_applescript(script)

# 10. 播放/暂停音乐
def play_or_pause():
    script = """
    tell application "Music"
        playpause
    end tell
    """
    return execute_applescript(script)








# --- Command-Line Interface ---


def get_user_input(prompt, valid_options=None, input_type=int):
    """Get user input with validation."""
    while True:
        try:
            user_input = input(prompt)
            if input_type == int:
                value = int(user_input)
                if valid_options and value not in valid_options:
                    print(f"Please enter a valid option: {valid_options}")
                    continue
                return value
            elif input_type == str:
                if valid_options and user_input.lower() not in valid_options:
                    print(f"Please enter a valid option: {valid_options}")
                    continue
                return user_input.lower()
            else:
                return user_input
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


def main():
    """Main function with interactive menu interface."""
    print("=" * 60)
    print("           macOS Window Automation Tool")
    print("=" * 60)

    functions = {
        1: ("Toggle fullscreen", toggle_fullscreen),
        2: ("Minimize window", minimize_window),
        3: ("Move window", move_window),
        4: ("Switch window", switch_window),
        5: ("Close current window", close_window),
        6: ("Scroll window", scroll_window),
        7: ("Mute volume", set_volume_to_mute),
        8: ("Increase volume", increase_volume),
        9: ("Decrease volume", decrease_volume),
        10: ("Play/Pause music", play_or_pause),
    }

    while True:
        print("\nAvailable functions:")
        for i in range(1, len(functions) + 1):
            print(f"{i}. {functions[i][0]}")
        print("0. Exit")
        print("-" * 40)

        try:
            choice = get_user_input(
                f"Select a function (0-{len(functions)}): ", list(range(len(functions) + 1))
            )

            if choice == 0:
                print("Goodbye!")
                break
            
            print(f"\nExecuting: {functions[choice][0]}")
            action = functions[choice][1]

            if action == move_window:
                dx = get_user_input("Horizontal movement (dx): ", input_type=int)
                dy = get_user_input("Vertical movement (dy): ", input_type=int)
                action(dx, dy)
            elif action == scroll_window:
                amount = get_user_input("Scroll amount (positive=up, negative=down): ", input_type=int)
                action(amount)
            else:
                action()

            print("Done.")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue


if __name__ == "__main__":
    main()
