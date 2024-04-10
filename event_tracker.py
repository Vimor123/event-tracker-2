import os
import datetime
import codecs

# Event format: dd.mm.yyyy. - <event name>

event_file_directory = os.path.dirname(__file__)
event_file_name = 'events.txt'
event_file_path = os.path.join(event_file_directory, event_file_name)


# Birthday format: dd.mm.yyyy. - <name>

birthday_file_directory = os.path.dirname(__file__)
birthday_file_name = 'birthdays.txt'
birthday_file_path = os.path.join(birthday_file_directory, birthday_file_name)

def main():
    def main_menu():
        viewing = True
        show_birthdays = False
        while viewing:
            events = load_events(event_file_path)
            birthdays = load_events(birthday_file_path)

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


                    events.append({
                            "date" : datetime.datetime(birthday_year, birthday_month, birthday_day),
                            "name" : "{}'s {}{} birthday".format(birthday["name"], years, suffix)
                        })

            def event_date(event):
                return event["date"]
            events.sort(key=event_date)

            os.system("clear")

            print("Events:")
            
            current_month = 0
            current_year = 0
            for event in events:
                if event["date"].month != current_month or event["date"].year != current_year:
                    print("")
                    print(event["date"].strftime("%B %Y"))
                    print("=" * 20)
                    current_month = event["date"].month
                    current_year = event["date"].year
                
                print("{} - {}".format(event["date"].strftime("%d.%m.%Y."),
                                       event["name"]))

            option_chosen = False
            option = 0
            while not option_chosen:
                print("\nWhat do you wish to do?")
                print("1. Add events")
                print("2. Delete events")
                if show_birthdays:
                    print("3. Hide birthdays")
                else:
                    print("3. Show birthdays")
                print("4. Add birthdays")
                print("5. Delete birthdays")
                print("6. Delete past events")
                print("7. Quit")
                option = input()
                if option not in ["1", "2", "3", "4", "5", "6", "7"]:
                    print("\nPlease input a valid number\n")
                else:
                    option_chosen = True
            print("")

            if option == "1":
                add_events_prompt()
            elif option == "2":
                delete_events_prompt()
            elif option == "3":
                show_birthdays = not show_birthdays
            elif option == "4":
                add_birthdays_prompt()
            elif option == "5":
                delete_birthdays_prompt()
            elif option == "6":
                delete_past_events(event_file_path)
            elif option == "7":
                viewing = False

    def add_events_prompt():
        print("Add events in the following format: \"dd.mm.YYYY. - <event name>\"")
        print("Enter an empty line to go back")

        adding = True
        while adding:
            event_string = input()
            if event_string == "":
                adding = False
            else:
                add_event(event_file_path, event_string)

    def delete_events_prompt():
        deleting = True
        while deleting:

            events = load_events(event_file_path)
            event_index = 1
            for event in events:
                print("{}. {} - {}".format(event_index,
                                           event["date"].strftime("%d.%m.%Y."),
                                           event["name"]))
                event_index += 1
        
            print("\nEnter the index of the event which you wish to delete")
            print("Enter an empty line to go back")
            
            event_index_string = input()
            if event_index_string == "":
                deleting = False
            else:
                delete_event(event_file_path, event_index_string)
    
    def add_birthdays_prompt():
        print("Add birthdays in the following format: \"dd.mm.YYYY. - <name>\"")
        print("Enter an empty line to go back")

        adding = True
        while adding:
            birthday_string = input()
            if birthday_string == "":
                adding = False
            else:
                add_event(birthday_file_path, birthday_string)

    def delete_birthdays_prompt():
        deleting = True
        while deleting:

            birthdays = load_events(birthday_file_path)
            birthday_index = 1
            for birthday in birthdays:
                print("{}. {} - {}".format(birthday_index,
                                           birthday["date"].strftime("%d.%m.%Y."),
                                           birthday["name"]))
                birthday_index += 1

            print("\nEnter the index of the birthday which you wish to delete")
            print("Enter an empty line to go back")

            birthday_index_string = input()
            if birthday_index_string == "":
                deleting = False
            else:
                delete_event(birthday_file_path, birthday_index_string)

    main_menu()


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
        print("Invalid input: no separator between date and name")
        return
    date_string = event_string[:separator_index-1]
    date_list = date_string.split('.')
    if len(date_list) != 4 or date_list[3] != "":
        print("Invalid input: invalid date format")
        return
    try:
        date = datetime.datetime(int(date_list[2]),
                                 int(date_list[1]),
                                 int(date_list[0]))
    except ValueError:
        print("Invalid input: invalid date")
        return

    if len(event_string) < separator_index + 3:
        print("Invalid input: event has no name")
        return

    name = event_string[separator_index+2:]

    event = {
        "date" : date,
        "name" : name
        }

    events = load_events(event_file_path)
    events.append(event)

    save_events(event_file_path, events)
    print("Event added")


def delete_event(event_file_path, event_index_string):
    try:
        event_index = int(event_index_string)
    except ValueError:
        print("\nInvalid index\n")
        return
    
    events = load_events(event_file_path)
    
    if event_index > len(events):
        print("\nInvalid index\n")
        return
        
    events.pop(event_index-1)
    save_events(event_file_path, events)
    print("\nEvent deleted\n")


def delete_past_events(event_file_path):
    events = load_events(event_file_path)
    new_events = []

    for event in events:
        if event["date"] > (datetime.datetime.now() - datetime.timedelta(days = 1)):
            new_events.append(event)

    save_events(event_file_path, new_events)
    print("\nOld events deleted\n")


if __name__ == '__main__':
    main()
