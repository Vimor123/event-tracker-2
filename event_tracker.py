import os
import datetime
import calendar
import codecs
import curses
from curses.textpad import rectangle

# Event format: dd.mm.yyyy. - <event name>

event_file_directory = os.path.dirname(__file__)
event_file_name = 'events.txt'
event_file_path = os.path.join(event_file_directory, event_file_name)


# Birthday format: dd.mm.yyyy. - <name>

birthday_file_directory = os.path.dirname(__file__)
birthday_file_name = 'birthdays.txt'
birthday_file_path = os.path.join(birthday_file_directory, birthday_file_name)


max_event_length = 62


def main(stdscr):
    # Prepairing colors
    curses.start_color()
    curses.use_default_colors()

    color_names = [ "black", "red", "green", "yellow",
                    "blue", "magenta", "cyan", "white" ]

    normal_colors = {}
    bright_colors = {}
    inverted_normal_colors = {}
    inverted_bright_colors = {}
    
    for index, color in enumerate(color_names):
        curses.init_pair(index + 1, index, -1)
        normal_colors[color] = curses.color_pair(index + 1)
        curses.init_pair(index + 9, index + 8, -1)
        bright_colors[color] = curses.color_pair(index + 9)
        curses.init_pair(index + 17, -1, index)
        inverted_normal_colors[color] = curses.color_pair(index + 17)
        curses.init_pair(index + 25, -1, index + 8)
        inverted_bright_colors[color] = curses.color_pair(index + 25)

    curses.curs_set(0)

    rows, cols = stdscr.getmaxyx()

    def render_main_screen():

        viewing = True

        show_birthdays = False
        show_whole_year = False
        current_chosen = 0

        while viewing:
            # Reading files
            events = load_events(event_file_path)
            birthdays = load_events(birthday_file_path)

            all_events = events.copy()
            next_birthdays = []

            if show_birthdays:
                present_day = datetime.datetime.now()
                for birthday in birthdays:
                    birthday_day = birthday["date"].day
                    birthday_month = birthday["date"].month
                    birthday_year = datetime.datetime.now().year
                    if present_day > datetime.datetime(birthday_year, birthday_month, birthday_day):
                        birthday_year += 1

                    years = birthday_year - birthday["date"].year

                    suffix = "th"
                    if years % 10 == 1:
                        suffix = "st"
                    elif years % 10 == 2:
                        suffix = "nd"
                    elif years % 10 == 3:
                        suffix = "rd"

                    all_events.append({
                            "date" : datetime.datetime(birthday_year, birthday_month, birthday_day),
                            "name" : "{}' {}{} birthday".format(birthday["name"], years, suffix)
                        })

                    next_birthdays.append({
                            "date" : datetime.datetime(birthday_year, birthday_month, birthday_day),
                            "name" : "{}' {}{} birthday".format(birthday["name"], years, suffix)
                        })

            def event_date(event):
                return event["date"]
            all_events.sort(key = event_date)

            stdscr.clear()

            border = cols // 2 - 2

            stdscr.addstr(0, border // 2 - 3, "Events\n", curses.A_BOLD)
    
            current_month = 0
            current_year = 0

            months_displayed = 0
            calendar_months = []

            for event in all_events:
                if event["date"].month != current_month or event["date"].year != current_year:
                    if months_displayed < 3:
                        stdscr.addstr("\n" + event["date"].strftime("%B %Y") + "\n", curses.A_BOLD | normal_colors["cyan"])
                        current_month = event["date"].month
                        current_year = event["date"].year
                        calendar_months.append((current_month, current_year))
 
                    months_displayed += 1

                if months_displayed <= 3:
                    stdscr.addstr("{} - {}\n".format(event["date"].strftime("%d.%m.%Y."),
                                                     event["name"]))

            stdscr.addstr("\n")

            stdscr.addstr(0, border + (cols - border) // 2 - 5, "Calendar", curses.A_BOLD)

            current_row = 2

            def show_calendar(start_row, start_column, month, year):
                current_row = start_row
                title = calendar.month_name[month] + " " + str(year)
                stdscr.addstr(current_row, start_column + 11 - len(title) // 2 - 1,
                              title, curses.A_BOLD | normal_colors["cyan"])
                current_row += 1
                stdscr.addstr(current_row, start_column, "Mo Tu We Th Fr Sa Su", curses.A_BOLD)
                current_row += 1
                
                no_of_days = calendar.monthrange(year, month)[1]

                day_in_week = (int(datetime.datetime(year, month, 1).strftime("%w")) - 1 + 7) % 7

                for day in range(1, no_of_days + 1):
                    current_datetime = datetime.datetime(year, month, day)
                    date_status = "normal"

                    for event in events:
                        if event["date"] == current_datetime:
                            date_status = "event"

                    if show_birthdays:
                        for birthday in next_birthdays:
                            if birthday["date"] == current_datetime:
                                date_status = "birthday"

                    if current_datetime < datetime.datetime.now() -datetime.timedelta(days = 1):
                        if date_status == "event":
                            date_status = "past event"
                        elif date_status == "birthday":
                            date_status = "past birthday"
                        else:
                            date_status = "past"

                    text = str(day).rjust(2)
                    if date_status == "normal":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text)
                    elif date_status == "event":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text, inverted_normal_colors["blue"])
                    elif date_status == "birthday":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text, inverted_normal_colors["red"])
                    elif date_status == "past event":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text, normal_colors["blue"])
                    elif date_status == "past birthday":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text, normal_colors["red"])
                    elif date_status == "past":
                        stdscr.addstr(current_row, start_column + day_in_week * 3, text, bright_colors["white"])
                    
                    day_in_week += 1
                    if day_in_week >= 7:
                        day_in_week = 0
                        current_row += 1

                return current_row + 2

            
            options = [ "Show birthdays", "Show whole year on calendar", "Add events", "Delete events", 
                        "Add birthdays", "Delete birthdays", "Delete past events", "Quit" ]
            if show_birthdays == True:
                options[0] = "Hide birthdays"
            if show_whole_year == True:
                options[1] = "Show only three months on calendar"

            option_chosen = False

            while not option_chosen:
                for index, option in enumerate(options):
                    text = option.ljust(border)
                    if index != len(options) - 1:
                        text += "\n"

                    if index == current_chosen:
                        stdscr.addstr(rows - len(options) + index, 0, text, curses.A_REVERSE)
                    else:
                        stdscr.addstr(rows - len(options) + index, 0, text)

                for i in range(rows):
                    stdscr.addstr(i, border, "|")

                stdscr.refresh()
                
                current_row = 2

                if not show_whole_year:
                    current_row += 1
                    for month, year in calendar_months:
                        current_row = show_calendar(current_row, border + (cols - border) // 2 - 11, month, year) + 1

                else:
                    month, year = calendar_months[0]
                    for month_row in range(4):
                        current_rows = []
                        for month_column in range(3):
                            current_rows.append(show_calendar(current_row, border + (cols - border) // 2 - 11 - 23 + month_column * 23, month, year))
                            month += 1
                            if month >= 13:
                                month = 1
                                year += 1
                        current_row = max(current_rows)


                stdscr.addstr(current_row, border + (cols - border) // 2 - 8, "  ", inverted_normal_colors["blue"])
                stdscr.addstr(current_row, border + (cols - border) // 2 - 8 + 2, " - event")

                current_row += 1

                stdscr.addstr(current_row, border + (cols - border) // 2 - 8, "  ", inverted_normal_colors["red"])
                stdscr.addstr(current_row, border + (cols - border) // 2 - 8 + 2, " - birthday")

                stdscr.refresh()


                key = stdscr.getkey()

                if key == "KEY_UP":
                    current_chosen = (current_chosen - 1 + len(options)) % len(options)
                elif key == "KEY_DOWN":
                    current_chosen = (current_chosen + 1) % len(options)
                elif key == "q":
                    exit(0)
                elif key == "\n":
                    option_chosen = True

            selected_option = options[current_chosen]

            if selected_option == "Show birthdays":
                show_birthdays = True
            elif selected_option == "Hide birthdays":
                show_birthdays = False
            elif selected_option == "Show whole year on calendar":
                show_whole_year = True
            elif selected_option == "Show only three months on calendar":
                show_whole_year = False
            elif selected_option == "Add events":
                add_events_prompt()
            elif selected_option == "Delete events":
                delete_events_prompt()
            elif selected_option == "Add birthdays":
                add_birthdays_prompt()
            elif selected_option == "Delete birthdays":
                delete_birthdays_prompt()
            elif selected_option == "Delete past events":
                delete_past_events(event_file_path)
            elif selected_option == "Quit":
                viewing = False

            stdscr.addstr(selected_option)


    def add_events_prompt():
        stdscr.clear()

        adding = True

        stdscr.addstr(0, 27, "Add events", curses.A_BOLD)
        stdscr.addstr(2, 0, "Add events in the following format: \"dd.mm.YYYY. - <event name>\"")
        stdscr.addstr(3, 0, "Press ENTER to add the event.")

        rectangle(stdscr, 4, 0, 6, max_event_length + 2)
        stdscr.move(5, 1)
        curses.curs_set(2)

        writing = True

        options = ["writing", "Back"]
        current_chosen = 0

        new_event_string = ""
        current_index = 0

        while adding:
            for index, option in enumerate(options):
                if option != "writing":
                    if index != current_chosen:
                        stdscr.addstr(6 + index, 0, option.ljust(10))
                    else:
                        stdscr.addstr(6 + index, 0, option.ljust(10), curses.A_REVERSE)

            stdscr.move(5, 1 + current_index)

            key = stdscr.getkey()
            if key == "KEY_UP":
                current_chosen = (current_chosen - 1 + len(options)) % len(options)
            elif key == "KEY_DOWN":
                current_chosen = (current_chosen + 1) % len(options)
            elif key == "\n":
                if options[current_chosen] == "writing":
                    try:
                        add_event(event_file_path, new_event_string)
                        stdscr.addstr(5 + len(options) + 2, 0, "Event added".ljust(30), curses.A_BOLD)
                        stdscr.addstr(5 + len(options) + 3, 0, new_event_string.ljust(max_event_length), bright_colors["white"])
                        stdscr.addstr(5, 1, "".ljust(max_event_length))
                        stdscr.move(5, 1)
                        current_index = 0
                        new_event_string = ""
                    except Exception as e:
                        error_text = ""
                        if str(e) == "invalid_event_format":
                            error_text = "Event format incorrect!"
                        elif str(e) == "invalid_date_format":
                            error_text = "Date format invalid!"
                        elif str(e) == "impossible_date":
                            error_text = "Date cannot exist!"
                        elif str(e) == "no_event_name":
                            error_text = "Event has no name!"
                        stdscr.addstr(5 + len(options) + 2, 0, error_text.ljust(30), curses.A_BOLD | normal_colors["cyan"])
                        stdscr.move(5, 1 + current_index)
                elif options[current_chosen] == "Back":
                    adding = False

            elif writing:
                if key == "KEY_LEFT":
                    if current_index > 0:
                        current_index -= 1
                elif key == "KEY_RIGHT":
                    if current_index < len(new_event_string):
                        current_index += 1
                elif key == "KEY_BACKSPACE":
                    if current_index > 0:
                        new_event_string = new_event_string[:current_index - 1] + new_event_string[current_index:]
                        current_index -= 1
                        stdscr.addstr(5, 1, new_event_string.ljust(max_event_length))
                        stdscr.move(5, 1 + current_index)
                else:
                    if len(new_event_string) < 62:
                        new_event_string = new_event_string[:current_index] + key + new_event_string[current_index:]
                        current_index += 1
                    stdscr.addstr(5, 1, new_event_string.ljust(max_event_length))
                    stdscr.move(5, 1 + current_index)

            if options[current_chosen] != "writing":
                writing = False
                curses.curs_set(0)

            else:
                writing = True
                curses.curs_set(2)

            stdscr.refresh()


    def add_birthdays_prompt():
        stdscr.clear()

        adding = True

        stdscr.addstr(0, 26, "Add birthdays", curses.A_BOLD)
        stdscr.addstr(2, 0, "Add birthdays in the following format: \"dd.mm.YYYY. - <name>\"")
        stdscr.addstr(3, 0, "Press ENTER to add the birthday.")

        rectangle(stdscr, 4, 0, 6, max_event_length + 2)
        stdscr.move(5, 1)
        curses.curs_set(2)

        writing = True

        options = ["writing", "Back"]
        current_chosen = 0

        new_birthday_string = ""
        current_index = 0

        while adding:
            for index, option in enumerate(options):
                if option != "writing":
                    if index != current_chosen:
                        stdscr.addstr(6 + index, 0, option.ljust(10))
                    else:
                        stdscr.addstr(6 + index, 0, option.ljust(10), curses.A_REVERSE)

            stdscr.move(5, 1 + current_index)

            key = stdscr.getkey()
            if key == "KEY_UP":
                current_chosen = (current_chosen - 1 + len(options)) % len(options)
            elif key == "KEY_DOWN":
                current_chosen = (current_chosen + 1) % len(options)
            elif key == "\n":
                if options[current_chosen] == "writing":
                    try:
                        add_event(birthday_file_path, new_birthday_string)
                        stdscr.addstr(5 + len(options) + 2, 0, "Birthday added".ljust(30), curses.A_BOLD)
                        stdscr.addstr(5 + len(options) + 3, 0, new_birthday_string.ljust(max_event_length), bright_colors["white"])
                        stdscr.addstr(5, 1, "".ljust(max_event_length))
                        stdscr.move(5, 1)
                        current_index = 0
                        new_birthday_string = ""
                    except Exception as e:
                        error_text = ""
                        if str(e) == "invalid_event_format":
                            error_text = "Birthday format incorrect!"
                        elif str(e) == "invalid_date_format":
                            error_text = "Date format invalid!"
                        elif str(e) == "impossible_date":
                            error_text = "Date cannot exist!"
                        elif str(e) == "no_event_name":
                            error_text = "Birthday has no name!"
                        stdscr.addstr(5 + len(options) + 2, 0, error_text.ljust(30), curses.A_BOLD | normal_colors["cyan"])
                        stdscr.move(5, 1 + current_index)
                elif options[current_chosen] == "Back":
                    adding = False

            elif writing:
                if key == "KEY_LEFT":
                    if current_index > 0:
                        current_index -= 1
                elif key == "KEY_RIGHT":
                    if current_index < len(new_birthday_string):
                        current_index += 1
                elif key == "KEY_BACKSPACE":
                    if current_index > 0:
                        new_birthday_string = new_birthday_string[:current_index - 1] + new_birthday_string[current_index:]
                        current_index -= 1
                        stdscr.addstr(5, 1, new_birthday_string.ljust(max_event_length))
                        stdscr.move(5, 1 + current_index)
                else:
                    if len(new_birthday_string) < 62:
                        new_birthday_string = new_birthday_string[:current_index] + key + new_birthday_string[current_index:]
                        current_index += 1
                    stdscr.addstr(5, 1, new_birthday_string.ljust(max_event_length))
                    stdscr.move(5, 1 + current_index)

            if options[current_chosen] != "writing":
                writing = False
                curses.curs_set(0)

            else:
                writing = True
                curses.curs_set(2)

            stdscr.refresh()


    def delete_events_prompt():
        stdscr.clear()

        stdscr.addstr(0, 26, "Delete events", curses.A_BOLD)
        stdscr.addstr(2, 0, "Press ENTER to delete the highlighted event.")
        stdscr.addstr(3, 0, "Press Q to go back.")

        deleting = True
        current_chosen = 0

        events = load_events(event_file_path)

        while deleting:
            for index, event in enumerate(events):
                text = "{} - {}".format(event["date"].strftime("%d.%m.%Y."), event["name"])
                if index != current_chosen:
                    stdscr.addstr(5 + index, 0, text.ljust(max_event_length))
                else:
                    stdscr.addstr(5 + index, 0, text.ljust(max_event_length), curses.A_REVERSE)

            key = stdscr.getkey()
            
            if key == "KEY_UP":
                if len(events) > 0:
                    current_chosen = (current_chosen - 1 + len(events)) % len(events)
            elif key == "KEY_DOWN":
                if len(events) > 0:
                    current_chosen = (current_chosen + 1) % len(events)
            elif key == "\n":
                if len(events) > 0:
                    events.pop(current_chosen)
                stdscr.addstr(5 + len(events), 0, "".ljust(max_event_length))
                if current_chosen >= len(events):
                    current_chosen -= 1

            elif key == "q":
                deleting = False
                save_events(event_file_path, events)

            stdscr.refresh()


    def delete_birthdays_prompt():
        stdscr.clear()

        stdscr.addstr(0, 23, "Delete birthdays", curses.A_BOLD)
        stdscr.addstr(2, 0, "Press ENTER to delete the highlighted birthday.")
        stdscr.addstr(3, 0, "Press Q to go back.")

        deleting = True
        current_chosen = 0

        birthdays = load_events(birthday_file_path)

        while deleting:
            for index, birthday in enumerate(birthdays):
                text = "{} - {}".format(birthday["date"].strftime("%d.%m.%Y."), birthday["name"])
                if index != current_chosen:
                    stdscr.addstr(5 + index, 0, text.ljust(max_event_length))
                else:
                    stdscr.addstr(5 + index, 0, text.ljust(max_event_length), curses.A_REVERSE)

            key = stdscr.getkey()
            
            if key == "KEY_UP":
                if len(birthdays) > 0:
                    current_chosen = (current_chosen - 1 + len(birthdays)) % len(birthdays)
            elif key == "KEY_DOWN":
                if len(birthdays) > 0:
                    current_chosen = (current_chosen + 1) % len(birthdays)
            elif key == "\n":
                if len(birthdays) > 0:
                    birthdays.pop(current_chosen)
                stdscr.addstr(5 + len(birthdays), 0, "".ljust(max_event_length))
                if current_chosen >= len(birthdays):
                    current_chosen -= 1

            elif key == "q":
                deleting = False
                save_events(birthday_file_path, birthdays)

            stdscr.refresh()


    render_main_screen()


def load_events(event_file_path):
    events = []
    if os.path.isfile(event_file_path):
        events_file = codecs.open(event_file_path, 'r', "utf-8")
        for line in events_file:
            event_string = line[:-1]
            name_string = event_string[event_string.find('-')+2:]
            date_string = event_string[:event_string.find('-')-1]
            date_list = date_string.split('.')
            events.append({
                "date" : datetime.datetime(int(date_list[2]),
                                           int(date_list[1]),
                                           int(date_list[0])),
                "name" : name_string
                })
        events_file.close()
    return events


def save_events(event_file_path, events):
    def event_date(event):
        return event["date"]
    events.sort(key=event_date)
    
    events_file = codecs.open(event_file_path, 'w', "utf-8")
    for event in events:
        events_file.write("{} - {}\n".format(event["date"].strftime("%d.%m.%Y."),
                                             event["name"]))
    events_file.close()


def add_event(event_file_path, event_string):
    separator_index = event_string.find('-')
    if separator_index == -1:
        raise Exception("invalid_event_format")
    date_string = event_string[:separator_index-1]
    date_list = date_string.split('.')
    if len(date_list) != 4 or date_list[3] != "":
        raise Exception("invalid_date_format")
    try:
        date = datetime.datetime(int(date_list[2]),
                                 int(date_list[1]),
                                 int(date_list[0]))
    except ValueError:
        raise Exception("impossible_date")

    if len(event_string) < separator_index + 3:
        raise Exception("no_event_name")

    name = event_string[separator_index+2:]

    event = {
        "date" : date,
        "name" : name
        }

    events = load_events(event_file_path)
    events.append(event)

    save_events(event_file_path, events)


def delete_event(event_file_path, event_index_string):
    try:
        event_index = int(event_index_string)
    except ValueError:
        return
    
    events = load_events(event_file_path)
    
    if event_index > len(events):
        return
        
    events.pop(event_index-1)
    save_events(event_file_path, events)


def delete_past_events(event_file_path):
    events = load_events(event_file_path)
    new_events = []

    for event in events:
        if event["date"] > (datetime.datetime.now() - datetime.timedelta(days = 1)):
            new_events.append(event)

    save_events(event_file_path, new_events)


curses.wrapper(main)
