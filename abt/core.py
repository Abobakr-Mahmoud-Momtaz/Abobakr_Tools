import sys
import subprocess
from pathlib import Path
import json
import datetime
import logging
import threading
# ==========================================
# 1. Constants & Global State
# ==========================================

(
    events, window_start, win_d, users_attempts, login_attempts_count, reached_end, stop_event,
    login_success_event_type, login_failed_event_type, events_count, time, time_f,
    datetime_value
) = (
    {}, 0, 0, {}, 0, False, threading.Event(), "", "", 0, "", "", 0
)

DIGIT_MAP = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
    "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
}

# Note: Logic preserved, global variables moved here.
RANDOM_DIGITS_POOL_RAW = (
    "3665873791420124765739852205995993847220940841857296174552312874967313464901791571408399755733276853571743092262182236459870273215283962557075660278731324319454000168933885542192243120521902818539668640411049605910861132638859897525800776575490782900940084180776085777811096023811664190763546770862807262104154200666435964711825605699106023954971425698774694675860327507880001658167131346274979922162033628753465661839093290256438946509929317670576038525821222918509031916727012718999679932805500098176463701154004046735195332317763251394553022859946047623276932146894591401879064566180480642202960976029193569734594261774010335413602635918813348483362442164116255677106734284891590814712461317020890864739984713949627924250583015472360299806894461199495388896565811865260583997789984733503027625946604835628431785414106376063769381324947250599419621906520087789984733503027625946604835628431785414106376063769381324947250599419621906520087780522456728086364223899802055503465899080505906439145266726826823058252317248314743643279920915382108750682730748029437608855019639073111316"
)

MODULE_DIR = Path(__file__).parent
random_digits_script_path = MODULE_DIR / "random_digits_pool.py"
random_digit_pool = []
random_digit_index = 0

# ==========================================
# 2. String & List Manipulation
# ==========================================

remove_all_occurrences = lambda items, item: [x for x in items if x != item]

def insert_text_after_in_file(file_path, insert_text, target_text):
    match_end_positions = [];file_characters = [];file_lines = [];comment_indices = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:file_characters.extend(line);file_lines.append(line)

        line_index = 0
        for char_index in range(len(file_characters)):

            
            current_line = file_lines[line_index]
            line_start_index = sum(len(line) for line in file_lines[:line_index]);line_end_index = line_start_index + len(current_line)
            if file_characters[char_index] == "\n":line_index += 1
            
            if "#" in current_line:
                comment_start_index = current_line.index("#")
                comment_start_global_index = line_start_index + comment_start_index
                comment_indices = list(range(comment_start_global_index, line_end_index))
            if (
                "".join(map(str, file_characters[char_index:char_index+len(target_text)])) == target_text
                and file_characters[char_index - 1] != '"' 
                and char_index not in comment_indices
                ):
                match_end_positions.append(char_index + (len(target_text) - 1))

    inserted_count = 0

    for position in match_end_positions:
        inserted_count += 1
        file_characters.insert(position + inserted_count, insert_text)

    result = "".join(map(str, file_characters))
    return result

def is_number(text: str, type_number: str) -> bool:
    if not text:
        return False

    if type_number == "float":
        if text.count(".") > 1:
            return False
        text = text.replace(".", "", 1)

    elif type_number != "int":
        return False

    return bool(text) and text.isdigit()

def contains_digit(text: str) -> bool:

    for character in text:
        if character.isdigit():
            return True
    return False

def text_replace(text, index, replacement_text, placeholder_text):
    text = list(text)

    for _ in range(len(placeholder_text)):
        text.pop(index)

    text.insert(index, replacement_text)

    return "".join(map(str, text))

# ==========================================
# 3. Input Helpers
# ==========================================

def read_integer(message: str) -> int:
    """Prompt user for integer input with validation."""
    while True:
        try: number = int(input(message).strip()); return number
        except ValueError: continue

def read_float(message: str) -> float:
    """Prompt user for float input with validation."""
    while True:
        try: number = float(input(message).strip()); return number
        except ValueError: continue

def read_non_numeric_string(message: str) -> str:
    """Prompt for non-empty string that is not a valid integer."""
    user_input = input(message)
    while user_input.replace(" ", "") == "" or user_input.isdigit():
        user_input = input(message)
    return user_input

# ==========================================
# 4. Random Number Generation
# ==========================================


def generate_random_digit_pool():
    """Generate a result by running the random digits pool library script."""
    global random_digit_pool
    random_digit_pool = [int(item) for item in subprocess.run([sys.executable, f'{random_digits_script_path}'], capture_output=True, text=True, check=True).stdout.strip()]
generate_random_digit_pool()

random_digit_index = 0
def generate_next_random_value(start: int, stop: int, seed: int) -> int:
    """Calculate the next random value based on seed."""
    range_size = stop - start + 1
    seed = (seed * 7 + 1) % range_size
    return seed + start

def get_pseudo_random_int(start: int, stop: int) -> int:
    """Generate a pseudo-random integer in the specified range."""
    global random_digit_index
    seed_digit = random_digit_pool[random_digit_index]
    random_value = generate_next_random_value(start, stop, seed_digit)

    random_digit_index += 1
    if random_digit_index == len(random_digit_pool):
        random_digit_index = 0
        generate_random_digit_pool()
    return random_value

# ==========================================
# 5. soc_analyst
# ==========================================

def create_events(events_file_path):
    global events

    while True:
        try:
            with open(events_file_path, "r") as events_file:
                events = json.loads(events_file.read())
            break

        except:
            continue
    return events

def count_user_attempts(window_start, window_end):
    global login_attempts_count
    for event in events[window_start: window_end]:
        if event["username"] not in users_attempts.keys(): 
            users_attempts[event["username"]] = [event["event_type"]]
            login_attempts_count += 1
        else:
            users_attempts[event["username"]] += [event["event_type"]]
            login_attempts_count += 1
    return users_attempts

get_event_time = lambda value: datetime.datetime.strptime(value[time], time_f)

def count_occurrences(items ,target):
    occurrences_count = 0
    for item in items:
        if item == target:
            occurrences_count += 1
    return occurrences_count

def count_user_event_types():
    user_event_counts = {}
    for username in users_attempts:
        for user_attempt in users_attempts[username]:
            user_event_counts[f"{username}_{user_attempt}"] = count_occurrences(users_attempts[username] , user_attempt)
    return user_event_counts

def create_users_list(items, condition):
    users_list = []
    if not isinstance(condition, list):
        condition = [condition]
    for item in items:
        its_len = len(items[item])
        if its_len >= condition[0] if len(condition) == 1 else its_len in condition: users_list.append(item)
    
    return users_list

def log_user_activity():
    global users_attempts , window_start , login_attempts_count
    
    logger = logging.getLogger("SOC_ANALYST")  
    log_messege = f"{get_event_time(events[window_start])}: {count_user_event_types()}\n" if users_attempts else ""
    users_attempts_create_users_list = {
        user: [event for event in users_attempts[user] if event in {login_success_event_type, login_failed_event_type}]
        for user in users_attempts
    }
    users_list_warning = create_users_list(users_attempts_create_users_list , list(range(2, 5)))
    users_list_critical = create_users_list(users_attempts_create_users_list , 5)
    

    if users_list_critical: logger.critical(log_messege)

    elif users_list_warning: logger.warning(log_messege)

    else: logger.info(log_messege)

    users_attempts = {}
    login_attempts_count = 0

def wait_for_new_events(events_file_path, events_count):
    global reached_end

    while len(events) <= events_count:

        create_events(events_file_path)
        
        if stop_event.is_set() and len(events) <= events_count:
            return
    
    reached_end = False
    return get_event_time(events[-1]) - datetime.timedelta(seconds=5)

def find_window_end(window_start, window_end_time, end_event):
    global reached_end

    for event in range(window_start, len(events)):
        datetime_value = get_event_time(events[event])

        if datetime_value > window_end_time:
            return event

        elif datetime_value > end_event and not any(
            get_event_time(events[i]) > window_end_time
            for i in range(event + 1, len(events))):

            reached_end = True
            return None

def analyze_event_windows(events_file_path, end_event):
    global window_start

    while window_start < len(events):
        window_end_time = get_event_time(events[window_start]) + datetime.timedelta(seconds=5)
        events_count = len(events)

        window_end = find_window_end(window_start, window_end_time, end_event)

        if reached_end:
            end_event = wait_for_new_events(events_file_path, events_count)

            if end_event is None:
                return

            continue

        users_attempts = count_user_attempts(window_start, window_end)
        if users_attempts:
            log_user_activity()

        window_start = window_end

def analyze_events(events_file_path, login_success_event_types, login_failed_event_types, window_duration,
                   timestamp_key="timestamp", timestamp_format="%Y-%m-%dT%H:%M:%S.%f%z"):

    global events, window_start, win_d, users_attempts, login_attempts_count, reached_end
    global login_failed_event_type, login_success_event_type, events_count, time, time_f

    (
        events_file_path, login_failed_event_type, login_success_event_type, time, time_f) = (
        Path(events_file_path), login_failed_event_types, login_success_event_types, timestamp_key, timestamp_format
    );  events = create_events(events_file_path)

    if not events: raise ValueError("No events found in the events file.")

    (
        window_start, win_d, users_attempts, login_attempts_count, reached_end, end_event) = (
        0, 0, {}, 0, False, get_event_time(events[-1]) - datetime.timedelta(seconds=5)
    )

    logging.basicConfig(
        filename=events_file_path.parent / "soc_analyst.log", level=logging.INFO,
        format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
    );  analyze_event_windows(events_file_path, end_event)
