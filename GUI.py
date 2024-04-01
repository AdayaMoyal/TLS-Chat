import sys
from tkinter import *
from tkinter import PhotoImage
from threading import Thread, Event
from Client import Client
import CommandProtocol
import math
from tkinter import filedialog
from datetime import datetime
from tkinter import Label, Menubutton, Menu
from tkinter import Toplevel

CHARS_PER_CM = 6
screen_width = 800
screen_height = 500
last_message_y = screen_height / 2 - 240

message_canvas = None
scrollbar = None
scrollbarforusers = None
users_canvas = None
sender = None
receiver = None
user_update_thread = None
buttons = []
users_canvas = None
stop_event = Event()
current_users = None

def create_users_tag():
    global canvas
    canvas.delete("connected_users_text")
    canvas.create_text(screen_width / 2 + 210, screen_height / 2 - 240, fill="#E582A3", font="Times 18 italic bold",
                       text=sender, tags="username_tag")
def create_profile():
    global canvas
    profile_image = PhotoImage(file="Pics/profile.png")
    profile_button = Button(frame, image=profile_image, width=40, height=40, bd=0, highlightthickness=0, command=get_profile)
    profile_button.image = profile_image
    profile_button.place(x=screen_width / 2 + 140, y=screen_height / 2 - 260)

def get_profile():
    global canvas, sender
    for widget in frame.winfo_children():
        widget.destroy()
    canvas = Canvas(frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)
    canvas.create_image(screen_width / 2, screen_height / 2 - 25, image=background_image)
    add_phone_for_chats()
    canvas.delete("connected_users_text")
    create_back_button()
    name = "Name: " + sender
    canvas.create_text(screen_width / 2 + 210, screen_height / 2 - 150, fill="black", font="Times 16 italic bold",
                       text=name)
    canvas.create_text(screen_width / 2 + 235, screen_height / 2 - 110, fill="black", font="Times 16 italic bold",
                       text="Change password: ")
    change_pass_image = PhotoImage(file="Pics/change_pass.png")
    change_pass_button = Button(frame, image=change_pass_image, width=45, height=45, command=change_pass, bd=0, highlightthickness=0)
    change_pass_button.image = change_pass_image
    change_pass_button.place(x=screen_width / 2 + 320, y=screen_height / 2 - 130)

def change_pass():
    global sender
    change_pass_window = Toplevel(frame)
    x = 800
    y = 200
    width = 280
    height = 100
    change_pass_window.geometry(f"{width}x{height}+{x}+{y}")
    error_label = Label(change_pass_window, text="", fg="red")
    error_label.pack()
    def submit_message():
        new_message = entry.get()
        if len(new_message) < 8:
            error_label.config(text="Password should be more than 8 characters long.")
        else:
            message = CommandProtocol.change_password(sender, new_message)
            client.send_message_to_socket(message)
            change_pass_window.destroy()

    instruction_label = Label(change_pass_window, text="Enter the new password:")
    instruction_label.pack()
    entry = Entry(change_pass_window)
    entry.pack()
    submit_button = Button(change_pass_window, text="Submit", command=submit_message)
    submit_button.pack()

def create_back_button():
    back_image = PhotoImage(file="Pics/back.png")
    back_button = Button(frame, image=back_image, width=40, height=40, command=go_back, bd=0, highlightthickness=0)
    back_button.image = back_image
    back_button.place(x=screen_width / 2 + 320, y=screen_height / 2 - 260)

def create_logout_button():
    back_image = PhotoImage(file="Pics/Logout.png")
    back_button = Button(frame, image=back_image, width=200, height=58, command=logout, bd=0, highlightthickness=0)
    back_button.image = back_image
    back_button.place(x=screen_width / 2 - 630, y=screen_height / 2 - 350)

def logout():
    global sender
    msg = CommandProtocol.logout(sender)
    client.send_message_to_socket(msg)
    window.destroy()

def go_back():
    global stop_event, user_update_thread, canvas, scrollbar, current_users
    canvas.delete("username_tag")
    for widget in frame.winfo_children():
        widget.destroy()
    if scrollbar is not None:
        scrollbar.destroy()
    if scrollbarforusers is not None:
        scrollbarforusers.destroy()
    canvas = Canvas(frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)
    canvas.create_image(screen_width / 2, screen_height / 2 - 25, image=background_image)
    if message_canvas is not None:
        message_canvas.destroy()
    add_phone_for_chats()
    add_connected_user(current_users)

def clear_canvas():
    if save_user() == 1:
        return
    global canvas
    for widget in frame.winfo_children():
        widget.destroy()
    canvas = Canvas(frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)
    canvas.create_image(screen_width / 2, screen_height / 2 - 25, image=background_image)
    add_phone_for_chats()

def update_connected_users():
    global current_users
    if not current_users:
        message = client.recv_message(client.sock)
        message = client.decryption(message)
        try:
            message = message.decode('utf-8')
        except:
            pass
        list_of_connected_users = parse_user_list(message)
        current_users = list_of_connected_users
        add_connected_user(list_of_connected_users)
    else:
        add_connected_user(current_users)

def create_error_msg(error):
    canvas.create_text(screen_width / 2 + 30, screen_height / 2 + 170, fill="red", font="Times 18 italic bold",
                       text=error, tags="error_tag")

def check_users_login():
    global sender
    sender = entry_username_signup.get()
    if not entry_username_login.get():
        if not sender or not entry_password_signup.get() or not entry_signup_mail.get() or not entry_signup_phone.get():
            error_message = "One of the fields is empty."
            create_error_msg(error_message)
            clear_signup_entries()
            return 1
        elif client.db.add_a_user(sender, entry_password_signup.get(), entry_signup_mail.get(), entry_signup_phone.get()) == 2:
            error_message = "One of the fields is not acceptable."
            create_error_msg(error_message)
            clear_signup_entries()
            return 1
        client.login(entry_username_signup.get(), entry_password_signup.get())
    else:
        client.login(entry_username_login.get(), entry_password_login.get())
        sender = entry_username_login.get()
        if not client.db.user_exists(entry_username_login.get(), entry_password_login.get()):
            error_message = "User does not exist."
            create_error_msg(error_message)
            clear_login_entries()
            return 1

def save_user():
    global sender
    canvas.delete("error_tag")
    if check_users_login() == 1:
        return 1
    networking_thread = Thread(target=client.connect_to_server)
    networking_thread.start()

def parse_user_list(msg):
    user_list_str = msg.split(":")[1].strip()
    user_list = [name.strip() for name in user_list_str.split(",")]
    return user_list

def add_phone_for_chats():
    global phone_image, user_update_thread, stop_event, current_users
    receive_thread = Thread(target=receive_messages)
    receive_thread.start()
    phone_image = PhotoImage(file="Pics/phone.png")
    canvas.create_image(screen_width / 2 + 230, screen_height / 2 - 20, anchor=CENTER, image=phone_image)
    canvas.create_text(screen_width / 2 + 265, screen_height / 2 - 240, fill="deeppink2", font="Times 18 italic bold",
                       text="Connected Users:", tags="connected_users_text")
    create_profile()
    create_logout_button()

def add_connected_user(list_of_connected_users):
    global users_canvas, scrollbarforusers, buttons, user_box_image
    if not list_of_connected_users:
        return
    user_box_image = PhotoImage(file="Pics/userbox.png")
    y = user_box_image.height() * (-1)
    users_canvas = Canvas(canvas, bg='white')
    users_canvas.place(x=screen_width / 2 + 130, y=screen_height / 2 - 200, width=6 * 40, height=400)
    scrollbarforusers = Scrollbar(frame, command=users_canvas.yview)
    scrollbarforusers.place(x=screen_width / 2 + 360, y=screen_height / 2 - 185, height=400)
    users_canvas.config(yscrollcommand=scrollbarforusers.set)
    buttons = []
    for name in list_of_connected_users:
        button = Button(users_canvas, text=name, image=user_box_image, compound="center", borderwidth=0, command=lambda t=name: get_chosen_user(t))
        button.image = user_box_image
        button.place(x=screen_width / 2 + 130, y=screen_height / 2 - 220 + y)
        font = ("Times", 12, "bold")
        button.configure(font=font, fg="white")
        y += user_box_image.height() + 5
        users_canvas.create_window(0, y, anchor='nw', window=button)
        users_canvas.config(scrollregion=users_canvas.bbox("all"))
        buttons.append(button)

def delete_buttons():
    global users_canvas, buttons
    for button in buttons:
        button.destroy()
    users_canvas.destroy()
    if scrollbarforusers is not None:
        scrollbarforusers.destroy()

def get_chosen_user(name):
    global receiver, user_update_thread, stop_event, user_texter_image, last_message_y
    stop_event.set()
    create_users_tag()
    last_message_y = screen_height / 2 - 355
    delete_buttons()
    create_back_button()
    receiver = name
    user_texter_image = PhotoImage(file="Pics/usertexter.png")
    button = Button(frame, text=name, image=user_texter_image, compound="center", anchor='nw',borderwidth=0)
    font = ("Times", 14, "bold")
    button.configure(font=font, fg="black")
    button.place(x=screen_width / 2 + 130, y=screen_height / 2 - 220)
    create_textbox_for_messaging()

def signup_info():
    global entry_username_signup, entry_password_signup, submit_image_signup, entry_signup_mail, entry_signup_phone
    entry_username_signup = Entry(frame, width=20, font=("italic bold", 12))
    entry_username_signup.place(x=360, y=210)
    canvas.create_text(300, 220, fill="black", font="Times 17 italic bold",
                       text="Username:")

    entry_password_signup = Entry(frame, width=20, font=("italic bold", 12))
    entry_password_signup.place(x=360, y=260)
    canvas.create_text(300, 270, fill="black", font="Times 17 italic bold",
                       text="Password:")

    entry_signup_mail = Entry(frame, width=20, font=("italic bold", 12))
    entry_signup_mail.place(x=360, y=310)
    canvas.create_text(300, 320, fill="black", font="Times 17 italic bold",
                       text="Mail:")

    entry_signup_phone = Entry(frame, width=20, font=("italic bold", 12))
    entry_signup_phone.place(x=360, y=360)
    canvas.create_text(300, 370, fill="black", font="Times 17 italic bold",
                       text="Phone:")

    submit_image_signup = PhotoImage(file="Pics/Signup.png")
    submit_button = Button(frame, image=submit_image_signup, compound=LEFT, command=clear_canvas, width=235,
                           height=65, bd=0, highlightthickness=0, bg="#E582A3", activebackground="#E582A3")
    submit_button.place(x=300, y=422)

def login_info():
    global entry_username_login, entry_password_login, submit_image_login
    entry_username_login = Entry(frame, width=20, font=("italic bold", 12))
    entry_username_login.place(x=840, y=240)
    canvas.create_text(780, 250, fill="black", font="Times 17 italic bold",
                       text="Username:")

    entry_password_login = Entry(frame, width=20, font=("italic bold", 12))
    entry_password_login.place(x=840, y=290)
    canvas.create_text(780, 300, fill="black", font="Times 17 italic bold",
                       text="Password:")

    submit_image_login = PhotoImage(file="Pics/Login.png")
    submit_button = Button(frame, image=submit_image_login, compound=LEFT, command=clear_canvas, width=235,
                           height=67, bd=0, highlightthickness=0, bg="#E582A3", activebackground="#E582A3")
    submit_button.place(x=780, y=425)

def clear_signup_entries():
    global entry_username_signup, entry_password_signup, entry_signup_mail, entry_signup_phone
    entry_username_signup.delete(0, END)
    entry_password_signup.delete(0, END)
    entry_signup_mail.delete(0, END)
    entry_signup_phone.delete(0, END)

def clear_login_entries():
    global entry_username_login, entry_password_login
    entry_username_login.delete(0, END)
    entry_password_login.delete(0, END)

def display_text(input_text, color, time):
    global last_message_y, message_canvas  # Access the global variable
    type, recv, send, con = CommandProtocol.recv_message(input_text)
    required_height = calculate_required_height(input_text, CHARS_PER_CM * 40)
    display_label = Label(message_canvas, text=con, bg=color, width=26, height=required_height, anchor="nw",
                          justify="left", wraplength=CHARS_PER_CM * 30)
    message_canvas.create_window(65, last_message_y + 10, anchor='nw', window=display_label)
    time_label = Label(message_canvas, text=time, bg=color, font=("Helvetica", 8), fg="red", width=30, height=1,
                       anchor="nw", justify="left", wraplength=CHARS_PER_CM * 40)
    time_label_y = last_message_y + display_label.winfo_reqheight()+ time_label.winfo_reqheight()-10  # Adjust the value as needed
    message_canvas.create_window(65, time_label_y, anchor='nw', window=time_label)
    # Adjust the scroll region dynamically
    message_canvas.config(scrollregion=message_canvas.bbox("all"))
    last_message_y += display_label.winfo_reqheight() + time_label.winfo_reqheight() + 10

def upload_text(input_text, color, x, time):
    global last_message_y, message_canvas  # Access the global variable
    menu_x = 190
    required_height = calculate_required_height(input_text, CHARS_PER_CM * 30)
    display_label = Label(message_canvas, text=input_text, bg=color, width=26, height=required_height, anchor="nw",
                          justify="left", wraplength=CHARS_PER_CM * 30)
    message_canvas.create_window(x, last_message_y + 10, anchor='nw', window=display_label)

    # Create the time label
    time_label = Label(message_canvas, text=time, bg=color, font=("Helvetica", 8), fg="red", width=30, height=1,
                       anchor="nw",
                       justify="left", wraplength=CHARS_PER_CM * 30)

    # Adjust the y-coordinate to position the time label very close to the display label from the bottom
    time_label_y = last_message_y + display_label.winfo_reqheight() + time_label.winfo_reqheight()-10  # Adjust the value as needed
    if color == "pink":
        message_canvas.create_window(35, time_label_y, anchor='nw', window=time_label)
        options_button = Menubutton(message_canvas, text="+", bg="pink", width=3, font=("Helvetica", 10, "bold"))
        options_button.menu = Menu(options_button)
        options_button["menu"] = options_button.menu
        options_button.menu.add_command(label="Edit Message", command=lambda: edit_message(display_label, time_label))
        options_button.menu.add_command(label="Delete Message", command=lambda: delete_message(display_label, time_label, options_button))
        message_canvas.create_window(menu_x, time_label_y - 7, anchor='nw', window=options_button)
    else:
        message_canvas.create_window(65, time_label_y, anchor='nw', window=time_label)
    # Adjust the scroll region dynamically
    message_canvas.config(scrollregion=message_canvas.bbox("all"))

    # Update the last message position considering both display and time label
    last_message_y += display_label.winfo_reqheight() + time_label.winfo_reqheight() + 10

def calculate_required_height(text, width):
    # Calculate the required height for the given text and width
    text = text.strip()
    lines = math.ceil(len(text) / (width / (CHARS_PER_CM-10)))
    return lines

def create_textbox_for_writing_message(entered_text, time):
    global message_canvas, receiver, sender, client, last_message_y  # Access the global variables

    required_height = calculate_required_height(entered_text, CHARS_PER_CM * 40)
    display_label = Label(message_canvas, text=entered_text, bg="pink", width=26, height=required_height, anchor="nw",
                          justify="left", wraplength=CHARS_PER_CM * 30)
    message_canvas.create_window(35, last_message_y + 10, anchor='nw', window=display_label)

    # Create the time label
    time_label = Label(message_canvas, text=time, bg="pink", font=("Helvetica", 8), fg="red", width=30, height=1,
                       anchor="nw", justify="left", wraplength=CHARS_PER_CM * 40)

    # Position the time label close to the display label from the bottom
    time_label_y = last_message_y + display_label.winfo_reqheight() + time_label.winfo_reqheight() - 10  # Adjust as needed
    message_canvas.create_window(35, time_label_y, anchor='nw', window=time_label)

    # Create a Menubutton for options
    options_button = Menubutton(message_canvas, text="+", bg="pink", width=3, font=("Helvetica", 10, "bold"))
    options_button.menu = Menu(options_button)
    options_button["menu"] = options_button.menu
    options_button.menu.add_command(label="Edit Message", command=lambda: edit_message(display_label, time_label))
    options_button.menu.add_command(label="Delete Message", command=lambda: delete_message(display_label, time_label, options_button))
    message_canvas.create_window(190, time_label_y-7, anchor='nw', window=options_button)

    # Adjust the scroll region dynamically
    message_canvas.config(scrollregion=message_canvas.bbox("all"))
    data = entered_text
    friends_name = receiver
    client.send_message_to_friend(data, friends_name, sender)
    last_message_y += display_label.winfo_reqheight() + time_label.winfo_reqheight() + 10

def edit_message(label, timelabel):
    global sender, receiver
    edit_window = Toplevel(frame)
    x = 800
    y = 200
    width = 150
    height = 100
    edit_window.geometry(f"{width}x{height}+{x}+{y}")
    time = timelabel.cget("text")
    def submit_message():
        new_message = entry.get()
        client.db.edit_message(sender, receiver, time, new_message)
        label.config(text=new_message)
        data = "EDITED_MESSAGE"
        message = CommandProtocol.edit_message(sender, receiver, data)
        client.send_message_to_socket(message)
        edit_window.destroy()

    instruction_label = Label(edit_window, text="Enter the new message:")
    instruction_label.pack()
    entry = Entry(edit_window)
    entry.pack()
    submit_button = Button(edit_window, text="Submit", command=submit_message)
    submit_button.pack()

def delete_message(label, timelabel, menu):
    global sender, receiver, message_canvas, last_message_y
    label_time = timelabel.cget("text")
    client.db.delete_message(sender, receiver, label_time)
    label.destroy()
    timelabel.destroy()
    menu.destroy()
    for widget in message_canvas.winfo_children():
        widget.destroy()
    last_message_y = screen_height / 2 - 355
    load_history()
    data = "DELETED_MESSAGE"
    message = CommandProtocol.delete_message(sender, receiver, data)
    client.send_message_to_socket(message)

def load_history():
    global sender, receiver
    messages = client.db.get_messages(sender, receiver)
    for i in messages:
        if i[1] == sender and i[2] == sender:
            upload_text(i[5], "pink", 35, i[4])
            upload_text(i[5], "tomato", 65, i[4])
        else:
            if i[1] == sender:
                upload_text(i[5], "pink", 35, i[4])
            if i[2] == sender:
                upload_text(i[5], "tomato", 65, i[4])

def create_textbox_for_messaging():
    global message_canvas, scrollbar, textbox, send_button, message_text, sender, receiver

    if message_canvas is not None:
        message_canvas.destroy()

    message_canvas = Canvas(frame, bg='white')
    message_canvas.place(x=screen_width / 2 + 130, y=screen_height / 2 - 185, width=6 * 40, height=360)

    scrollbar = Scrollbar(frame, command=message_canvas.yview)
    scrollbar.place(x=screen_width / 2 + 355, y=screen_height / 2 - 175, height=340)
    message_canvas.config(yscrollcommand=scrollbar.set)

    textbox = Text(frame, font=("italic bold", 12), wrap=WORD, width=20, height=2)
    textbox.place(x=screen_width / 2 + 135, y=screen_height / 2 + 180)

    message_text = textbox.get("1.0", "end-1c")

    send_button = Button(frame, text="Send", font=("italic bold", 12), bg="#dab2b2", fg="white", command=send_message)
    send_button.place(x=screen_width / 2 + 320, y=screen_height / 2 + 180)
    load_history()

def receive_messages():
    global current_users, receiver, sender
    while True:
        try:
            message = client.recv_message(client.sock)
            print(message)
            if message is not None:
                message = client.decryption(message)
                message = message.decode('utf-8')
                info = CommandProtocol.recv_message(message)
                if info[0] == "UPDATE_KEY":
                    client.key = info[1].encode('utf-8')
                    client.nonce_or_iv = info[2].encode('utf-8')
                    print(info)
                elif info[0] == "DELETE_MESSAGE" or info[0] == "EDIT_MESSAGE":
                    refresh_messages()
                elif "Users connected:" not in message:
                    current_time = datetime.now()
                    formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
                    display_text(message, "tomato", formatted_time)
                else:
                    list_of_connected_users = parse_user_list(message)
                    current_users = list_of_connected_users
                    add_connected_user(list_of_connected_users)
        except Exception as e:
            print(f"Error receiving message1: {e}")
            break

def refresh_messages():
    global sender, receiver, message_canvas, last_message_y
    for widget in message_canvas.winfo_children():
        widget.destroy()
    last_message_y = screen_height / 2 - 355
    load_history()

def send_message():
    global textbox, message_text, last_message_y

    # Get the text from the textbox
    message_text = textbox.get("1.0", "end-1c")

    # Check if the message is not empty
    if message_text.strip() != "":
        time = client.db.add_chats_history(sender, receiver, message_text)
        create_textbox_for_writing_message(message_text, time)

    # Clear the textbox
    textbox.delete(1.0, END)

if __name__ == "__main__":
    client = Client()
    window = Tk()
    window.title("GUI")

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{screen_width}x{screen_height}")

    frame = Frame(window)
    frame.pack(fill=BOTH, expand=YES)

    background_image = PhotoImage(file="Pics/1.png")
    welcome = PhotoImage(file="Pics/WelcomeToTLChat.png")

    canvas = Canvas(frame, bg="black")
    canvas.pack(fill=BOTH, expand=YES)
    canvas.create_image(screen_width / 2, screen_height / 2 - 20, image=background_image)
    canvas.create_image(screen_width / 2, 0, anchor=N, image=welcome)
    canvas.create_text(screen_width / 4 + 100, 160, fill="#DF6781", font="Times 30 italic bold", text="Sign Up")
    canvas.create_text(3 * (screen_width / 4) - 100, 160, fill="#FFC6D2", font="Times 30 italic bold", text="Login")
    message_canvas = Canvas(frame, bg='white')

    signup_info()
    login_info()

    window.mainloop()
