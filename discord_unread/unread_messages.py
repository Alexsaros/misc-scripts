import os
import json
import tkinter as tk
import webbrowser
import time
import datetime


def search_unread_messages():
    global unread_messages, searched_messages
    searched_messages = True
    # Retrieve entered settings
    user = string_select_user.get()
    print("Searching for unread messages from user: %s." % user)
    print("With the following criteria:")
    skip_responded = bool_responded.get()
    if skip_responded:
        print("-Skipping messages with a response.")
    skip_reactions = bool_reaction.get()
    if skip_reactions:
        print("-Skipping messages with a reaction.")
    skip_quick_messages = bool_quick_message.get()
    if skip_quick_messages:
        print("-Skipping messages where a message has been sent within 1 hour.")
    skip_whitelisted = bool_whitelisted.get()
    if skip_whitelisted:
        print("-Skipping messages which have been whitelisted.")
    if not any((skip_responded, skip_reactions, skip_quick_messages, skip_whitelisted)):
        print("-No criteria.")

    unread_messages = []
    mentioned_message_ids = []
    fast_responses = []
    FAST_RESPONSE_TIME_HRS = 1
    for i, msg in enumerate(messages):
        # Keep track of messages that have been mentioned by the other user
        if msg["type"] == "Reply" and msg["author"]["name"] != user:
            mentioned_message_ids.append(msg["reference"]["messageId"])

        # Filter messages from other users
        if msg["author"]["name"] != user:
            continue

        # Keep track of messages where the other user sent a message quickly
        sent_time = msg["timestamp"][:19]
        sent_time = datetime.datetime.strptime(sent_time, "%Y-%m-%dT%H:%M:%S")
        sent_time = time.mktime(sent_time.timetuple())
        # Finds the first message of the other user
        for j in range(i+1, len(messages)):
            msg_new = messages[j]
            # If the same user sends a quick message afterwards, don't count it
            if msg_new["author"]["name"] == user:
                continue
            sent_time_response = msg_new["timestamp"][:19]
            sent_time_response = datetime.datetime.strptime(sent_time_response, "%Y-%m-%dT%H:%M:%S")
            sent_time_response = time.mktime(sent_time_response.timetuple())
            if (sent_time_response - sent_time) <= FAST_RESPONSE_TIME_HRS * 60 * 60:
                fast_responses.append(msg["id"])
            break

        unread_messages.append(msg)

    whitelisted_message_ids = []
    try:
        with open("whitelisted_messages.txt", encoding="utf8") as f:
            whitelisted_file = f.read()
            whitelisted_message_ids = whitelisted_file.split("\n")
    except FileNotFoundError:
        pass

    unread_messages_temp = []
    for msg in unread_messages:
        # Skip messages that have been mentioned/responded to
        if skip_responded and msg["id"] in mentioned_message_ids:
            mentioned_message_ids.remove(msg["id"])
            continue
        # Skip messages that have been reacted to
        if skip_reactions and msg["reactions"]:
            continue
        # Skip messages that have been reacted to
        if skip_quick_messages and msg["id"] in fast_responses:
            fast_responses.remove(msg["id"])
            continue
        # Skip whitelisted messages
        if skip_whitelisted and msg["id"] in whitelisted_message_ids:
            whitelisted_message_ids.remove(msg["id"])
            continue
        unread_messages_temp.append(msg)
    unread_messages = unread_messages_temp
    unread_messages.reverse()   # Newer messages will show first

    window.destroy()


current_dir = os.getcwd()

json_files = []
for file in os.listdir(current_dir):
    if file.endswith(".json"):
        json_files.append(file)

json_file = None
if len(json_files) == 0:
    print("No .json files found!")
elif len(json_files) > 1:
    print("Multiple .json files found: %s.\nSelecting: \"%s\"." % (json_files, json_files[0]))
    json_file = json_files[0]
else:
    print("Using .json file: \"%s\"." % json_files[0])
    json_file = json_files[0]

if json_file:
    with open(json_file, encoding="utf8") as f:
        json_data = json.load(f)
    messages = json_data["messages"]
    channel_id = json_data["channel"]["id"]
    unread_messages = []
    searched_messages = False   # Keeps track of if a search has been performed

    # Assumes there are only two users
    users = []
    for message in messages:
        if message["author"]["name"] not in users:
            users.append(message["author"]["name"])
            if len(users) >= 2:
                break

    # Set up the window
    window = tk.Tk()
    window.title('Unread message finder (not a virus)')
    window.geometry('400x300')

    # Add functionality to select a user
    frame_select_user = tk.Frame(window)
    frame_select_user.pack(side=tk.TOP)
    label_select_user = tk.Label(frame_select_user, text="Select the user to find unread messages from:")
    label_select_user.pack()
    string_select_user = tk.StringVar(frame_select_user)
    string_select_user.set(users[0])
    menu_select_user = tk.OptionMenu(frame_select_user, string_select_user, *users)
    menu_select_user.pack(pady=5)

    # Add functionality to select the unread criteria
    frame_message_criteria = tk.Frame(window)
    frame_message_criteria.pack(side=tk.TOP)
    label_message_criteria = tk.Label(frame_message_criteria, text="A message has been read if either:")
    label_message_criteria.pack(pady=5)
    bool_responded = tk.BooleanVar()
    bool_responded.set(True)
    check_responded = tk.Checkbutton(frame_message_criteria, text='it has been mentioned/responded to',
                                     variable=bool_responded, justify=tk.LEFT, anchor=tk.W)
    check_responded.pack(fill=tk.BOTH)
    bool_reaction = tk.BooleanVar()
    bool_reaction.set(True)
    check_reaction = tk.Checkbutton(frame_message_criteria, text='a reaction has been added',
                                    variable=bool_reaction, justify=tk.LEFT, anchor=tk.W)
    check_reaction.pack(fill=tk.BOTH)
    bool_quick_message = tk.BooleanVar()
    bool_quick_message.set(True)
    check_quick_message = tk.Checkbutton(frame_message_criteria, text='a message has been sent within 1 hour',
                                         variable=bool_quick_message, justify=tk.LEFT, anchor=tk.W)
    check_quick_message.pack(fill=tk.BOTH)
    bool_whitelisted = tk.BooleanVar()
    bool_whitelisted.set(True)
    check_whitelisted = tk.Checkbutton(frame_message_criteria, text='it has been whitelisted',
                                       variable=bool_whitelisted, justify=tk.LEFT, anchor=tk.W)
    check_whitelisted.pack(fill=tk.BOTH)

    # Add the button
    button_search = tk.Button(window, text="Search messages", command=search_unread_messages)
    button_search.pack(pady=5)

    bool_cut_off_msg = tk.BooleanVar()
    check_cut_off_msg = tk.Checkbutton(window, text='Cut off long messages (click them to expand)',
                                       variable=bool_cut_off_msg)
    check_cut_off_msg.pack()

    window.mainloop()

    cut_off_length = -1
    if bool_cut_off_msg.get():
        cut_off_length = 150

    if searched_messages:
        window_width = 1000
        window_height = 800
        # Search has finished, show window with results
        results_window = tk.Tk()
        results_window.title('Unread messages')
        results_window.geometry('%sx%s' % (window_width, window_height))

        # Create the main frame encompassing the whole window
        frame_main = tk.Frame(results_window)
        frame_main.pack(fill=tk.BOTH, expand=True)

        # Create a frame to hold the canvas
        frame_canvas = tk.Frame(frame_main)
        frame_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a canvas inside the canvas frame
        canvas = tk.Canvas(frame_canvas)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(frame_canvas, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind the scrollbar to the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox(tk.ALL)))

        # Create a frame to hold the grid, and place the frame in the canvas
        frame_grid = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_grid, anchor=tk.NW)

        # Add mouse scroll wheel functionality
        def _on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        def open_url_lambda(url):
            return lambda e: webbrowser.open_new_tab(url)

        def expand_message(label, msg_content):
            label.config(text=msg_content)
            canvas.update()
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        def expand_message_lambda(label, msg):
            msg_content = msg["content"]
            if msg["stickers"]:
                for sticker in msg["stickers"]:
                    msg_content = "[Sticker: %s] %s" % (sticker["name"], msg_content)
            if msg["attachments"]:
                for attachment in msg["attachments"]:
                    msg_content = "[Attached: %s] %s" % (attachment["fileName"].split(".")[-1], msg_content)
            return lambda e: expand_message(label, msg_content)

        checkboxes = []
        message_labels = []
        for i, msg in enumerate(unread_messages):
            # Add a checkbox to select a message to be whitelisted
            bool_selected_msg = tk.BooleanVar()
            checkboxes.append(bool_selected_msg)
            check_selected_msg = tk.Checkbutton(frame_grid, variable=bool_selected_msg)
            check_selected_msg.grid(column=0, row=i, padx=5, pady=3)

            # Add the timestamp, which is a link to the message
            timestamp = msg["timestamp"][:10] + " " + msg["timestamp"][11:16]
            label_timestamp = tk.Label(frame_grid, text=timestamp, fg="blue")
            url_message = "https://discord.com/channels/@me/%s/%s" % (channel_id, msg["id"])
            label_timestamp.bind("<Button-1>", open_url_lambda(url_message))
            label_timestamp.grid(column=1, row=i, sticky=tk.W, padx=5, pady=3)

            # Add the actual message
            if cut_off_length != -1:
                msg_content = msg["content"][:cut_off_length]
                if len(msg["content"]) > cut_off_length:
                    msg_content += "..."
            else:
                msg_content = msg["content"]
            if msg["stickers"]:
                for sticker in msg["stickers"]:
                    msg_content = "[Sticker: %s] %s" % (sticker["name"], msg_content)
            if msg["attachments"]:
                for attachment in msg["attachments"]:
                    msg_content = "[Attached: %s] %s" % (attachment["fileName"].split(".")[-1], msg_content)
            label_unread_message = tk.Label(frame_grid, text=msg_content, relief=tk.GROOVE, justify=tk.LEFT)
            label_unread_message.bind("<Button-1>", expand_message_lambda(label_unread_message, msg))
            label_unread_message.grid(column=2, row=i, sticky=tk.W, padx=5, pady=3)
            message_labels.append(label_unread_message)

        if len(unread_messages) == 0:
            label_no_unread_msg = tk.Label(frame_grid, text="No unread messages! Yay!")
            label_no_unread_msg.grid(column=0, row=0, padx=5, pady=3)

        canvas.update()
        canvas_width = canvas.winfo_width()
        scrollbar_width = scrollbar.winfo_width()

        def refit_labels():
            start_of_column = frame_grid.grid_bbox(column=2, row=0)[0]
            max_width = canvas_width - start_of_column - scrollbar_width
            for message_label in message_labels:
                message_label.configure(wraplength=max_width)
            canvas.update()
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        def on_window_resize(event):
            global canvas_width
            if not isinstance(event.widget, tk.Canvas):
                return
            # Only continue if the canvas width has been resized
            current_width = event.width
            if current_width == canvas_width:
                return
            canvas_width = current_width
            refit_labels()

        refit_labels()
        canvas.bind("<Configure>", on_window_resize)

        def add_messages_to_whitelist():
            whitelisted_ids = []
            for j, checkbox in enumerate(checkboxes):
                whitelist_msg = checkbox.get()
                if whitelist_msg:
                    whitelisted_msg_id = unread_messages[j]["id"]
                    whitelisted_ids.append(whitelisted_msg_id)

            whitelisted_ids_file = []
            try:
                with open("whitelisted_messages.txt", encoding="utf8") as f:
                    whitelisted_file = f.read()
                    whitelisted_ids_file = whitelisted_file.split("\n")
            except FileNotFoundError:
                pass

            all_whitelisted_ids = whitelisted_ids_file + whitelisted_ids
            unique_whitelisted_ids = []
            for whitelisted_id in all_whitelisted_ids:
                if whitelisted_id and whitelisted_id not in unique_whitelisted_ids:
                    unique_whitelisted_ids.append(whitelisted_id)

            with open("whitelisted_messages.txt", "w", encoding="utf8") as f:
                unique_whitelisted_ids_string = "\n".join(unique_whitelisted_ids)
                f.write(unique_whitelisted_ids_string)

            results_window.destroy()

        # Add the whitelist button
        button_add_whitelist = tk.Button(frame_main, text="Add selected messages to whitelist and exit",
                                         command=add_messages_to_whitelist)
        button_add_whitelist.pack(side=tk.LEFT, padx=5, pady=5)

        def select_all_messages():
            if len(checkboxes) == 0:
                return
            set_to = True
            if checkboxes[0].get():
                set_to = False
            for checkbox in checkboxes:
                checkbox.set(set_to)

        # Add the select all button
        button_select_all = tk.Button(frame_main, text="Select all messages", command=select_all_messages)
        button_select_all.pack(side=tk.LEFT, padx=5, pady=5)

        results_window.mainloop()

print("end")

