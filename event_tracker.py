import os
import datetime
import calendar
import codecs
import curses

# Event format: dd.mm.yyyy. - <event name>

event_file_directory = os.path.dirname(__file__)
event_file_name = 'events.txt'
event_file_path = os.path.join(event_file_directory, event_file_name)


# Birthday format: dd.mm.yyyy. - <name>

birthday_file_directory = os.path.dirname(__file__)
birthday_file_name = 'birthdays.txt'
birthday_file_path = os.path.join(birthday_file_directory, birthday_file_name)

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

        show_birthdays = False
        show_whole_year = False

        while True:
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


            if not show_whole_year:
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

            options = [ "Show birthdays", "Show whole year on calendar", "Add events", "Delete events", 
                        "Add birthdays", "Delete birthdays", "Delete past events", "Quit" ]
            if show_birthdays == True:
                options[0] = "Hide birthdays"
            if show_whole_year == True:
                options[1] = "Show only three months on calendar"

            current_chosen = 0

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
                pass
            elif selected_option == "Delete events":
                pass
            elif selected_option == "Add birthdays":
                pass
            elif selected_option == "Delete birthdays":
                pass
            elif selected_option == "Delete past events":
                pass
            elif selected_option == "Quit":
                exit(0)

            stdscr.addstr(selected_option)

    render_main_screen()

    stdscr.getch()


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
        return
    date_string = event_string[:separator_index-1]
    date_list = date_string.split('.')
    if len(date_list) != 4 or date_list[3] != "":
        return
    try:
        date = datetime.datetime(int(date_list[2]),
                                 int(date_list[1]),
                                 int(date_list[0]))
    except ValueError:
        return

    if len(event_string) < separator_index + 3:
        return

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
