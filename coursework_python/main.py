import os
import re
import socket
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta

class Patient:
    def __init__(self, patient_id, first_name, last_name, middle_name, birth_date, contact):
        self.id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.birth_date = birth_date
        self.contact = contact

    def get_id(self):
        return f"{self.id}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def get_birth_info(self):
        return f"Дата народження: {self.birth_date}"

    def get_contact_info(self):
        return f"Контакт: {self.contact}"

class PatientVisit(Patient):
    def __init__(self, id, first_name, last_name, middle_name, birth_date, contact, visit_date, visit_time, doctor_name, diagnosis,
                 treatment):
        super().__init__(id, first_name, last_name, middle_name, birth_date, contact)
        self.visit_date = visit_date
        self.visit_time = visit_time
        self.doctor_name = doctor_name
        self.diagnosis = diagnosis
        self.treatment = treatment

    def get_patient_id(self):
        return f"{self.id}"

    def get_first_name(self):
        return f"{self.first_name}"

    def get_last_name(self):
        return f"{self.last_name}"

    def get_middle_name(self):
        return f"{self.middle_name}"

    def get_birth_date(self):
        return f"{self.birth_date}"

    def get_contact(self):
        return f"{self.contact}"

    def get_visit_date(self):
        return f"{self.visit_date}"

    def get_visit_time(self):
        return f"{self.visit_time}"

    def get_doctor_name(self):
        return f"{self.doctor_name}"

    def get_diagnosis(self):
        return f"{self.diagnosis}"

    def get_treatment(self):
        return f"{self.treatment}"

class DoctorSlot:
    def __init__(self, slot_id, doctorName, workDate, startTime):
        self.slot_id = slot_id
        self.doctorName = doctorName
        self.workDate = workDate
        self.startTime = startTime

    def get_slot_id(self):
        return f"{self.slot_id}"

    def get_doctor_name(self):
        return f"{self.doctorName}"

    def get_work_date(self):
        return f"{self.workDate}"

    def get_start_time(self):
        return f"{self.startTime}"

class Doctor:
    def __init__(self, doctor_id, first_name, last_name, middle_name, specialization, contact):
        self.doctor_id = doctor_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.specialization = specialization
        self.contact = contact

    def get_doctor_id(self):
        return f"{self.doctor_id}"

    def get_first_name(self):
        return f"{self.first_name}"

    def get_last_name(self):
        return f"{self.last_name}"

    def get_middle_name(self):
        return f"{self.middle_name}"

    def get_specialization(self):
        return f"{self.specialization}"

    def get_contact(self):
        return f"{self.contact}"


def load_image(container, image_path, image_size, background_color, placeholder_text=None, placeholder_font=None):
    absolute_image_path = os.path.abspath(os.path.expanduser(image_path))
    try:
        image = Image.open(absolute_image_path)
        resized_image = image.resize(image_size)
        image_photo = ImageTk.PhotoImage(resized_image)

        image_label = tk.Label(container, image=image_photo, bg=background_color)
        image_label.image = image_photo
        image_label.pack(pady=15)
    except Exception as error:
        print(f"Не вдалося завантажити фото: {error}")
        if placeholder_text:
            tk.Label(container, text=placeholder_text, font=placeholder_font or ("Helvetica", 18), bg=background_color, fg="white").pack(pady=15)


def send_credentials():
    username = username_entry.get().strip()
    user_password = password_entry.get().strip()
    error_message_label.pack_forget()

    if not username or not user_password:
        error_message_label.config(text="Будь ласка, введіть логін та пароль!", fg="lightgreen")
        error_message_label.pack(pady=5, before=login_button)
        return

    try:
        data = f"LOGIN,{username},{user_password}"
        response = send_data_to_server(data)
        response_parts = response.split(";", 1)

        status = response_parts[0]

        if status == "ADMIN":
            open_admin_panel()
        elif status == "DOCTOR":
            doctor_parts = response_parts[1].split("|")
            doctor = Doctor(doctor_id=int(doctor_parts[0]), first_name=doctor_parts[1], last_name=doctor_parts[2], middle_name=doctor_parts[3], specialization=doctor_parts[4], contact=doctor_parts[5])

            open_doctor_panel(doctor)
        else:
            error_message_label.config(text="Невірний логін або пароль!", fg="lightgreen")
            error_message_label.pack(pady=5, before=login_button)
    except Exception as connection_error:
        error_message_label.config(text=f"Помилка підключення: {str(connection_error)}", fg="lightgreen")
        error_message_label.pack(pady=5, before=login_button)


def show_login_screen():
    clear_screen()
    root.configure(bg="#4a4a4a")

    global username_entry, password_entry, error_message_label, login_button

    load_image(root, "images/hospital_image.jpg", image_size=(200, 200), background_color="#4a4a4a", placeholder_text="Лікарня 'Здорові разом'", placeholder_font=("Helvetica", 18))

    tk.Label(root, text="Логін:", font=("Helvetica", 16), bg="#4a4a4a", fg="white").pack()
    username_entry = tk.Entry(root, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
    username_entry.pack(pady=10, ipadx=5, ipady=5)
    username_entry.focus_set()

    tk.Label(root, text="Пароль:", font=("Helvetica", 16), bg="#4a4a4a", fg="white").pack()
    password_entry = tk.Entry(root, show="*", highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
    password_entry.pack(pady=10, ipadx=5, ipady=5)

    error_message_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#4a4a4a")
    error_message_label.pack_forget()

    login_button = tk.Button(root, text="Увійти", command=send_credentials, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=60, pady=5)
    login_button.pack(pady=10)


def open_admin_panel():
    clear_screen()

    main_container = tk.Frame(root, bg="#4a4a4a")
    main_container.pack(fill="both", expand=True)

    menu_panel = tk.Frame(main_container, bg="#333", width=250)
    menu_panel.pack(side="left", fill="y")

    workspace_panel = tk.Frame(main_container, bg="#555")
    workspace_panel.pack(side="right", fill="both", expand=True)

    load_image(menu_panel, "images/hospital_image.jpg", image_size=(140, 140), background_color="#4a4a4a", placeholder_text="Лікарня 'Здорові разом'", placeholder_font=("Helvetica", 18))

    info_frame = tk.Frame(menu_panel, bg="#333")
    info_frame.pack(fill="x", padx=10, pady=(0, 15))

    tk.Label(info_frame, text="Розклад:", font=("Helvetica", 14, "bold"), bg="#333", fg="lightgreen").pack(anchor="center", pady=(5, 0))
    tk.Label(info_frame, text="Пн-Сб 08:30 - 15:30", font=("Helvetica", 12), bg="#333", fg="white").pack(anchor="center")

    tk.Label(info_frame, text="Контакти:", font=("Helvetica", 14, "bold"), bg="#333", fg="lightgreen").pack(anchor="center", pady=(10, 0))
    tk.Label(info_frame, text="+38093-399-3393", font=("Helvetica", 12), bg="#333", fg="white").pack(anchor="center")
    tk.Label(info_frame, text="+38096-699-6696", font=("Helvetica", 12), bg="#333", fg="white").pack(anchor="center")

    tk.Label(info_frame, text="Адреса:", font=("Helvetica", 14, "bold"), bg="#333", fg="lightgreen").pack(anchor="center", pady=(10, 0))
    tk.Label(info_frame, text="місто Жовква", font=("Helvetica", 12), bg="#333", fg="white").pack(anchor="center")
    tk.Label(info_frame, text="вул. Воїнів УПА, 20", font=("Helvetica", 12), bg="#333", fg="white").pack(anchor="center")

    menu_options = ["Додати пацієнта", "Видалити пацієнта", "Шукати пацієнта", "Показати усіх пацієнтів", "Зробити запис", "Скасувати запис"]

    for option_label in menu_options:
        if option_label == "Додати пацієнта":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: patient_form(workspace_panel, "add"))
        elif option_label == "Видалити пацієнта":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: patient_form(workspace_panel, "delete"))
        elif option_label == "Шукати пацієнта":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: patient_form(workspace_panel, "search"))
        elif option_label == "Показати усіх пацієнтів":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: get_all_patients(workspace_panel))
        elif option_label == "Зробити запис":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: create_visit_booking_form(workspace_panel))
        elif option_label == "Скасувати запис":
            menu_button = tk.Button(menu_panel, text=option_label, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: cancel_visit_form(workspace_panel))
        menu_button.pack(pady=8, padx=10, ipady=1)

    exit_button = tk.Button(menu_panel, text="Вихід", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=exit_application)
    exit_button.pack(pady=8, padx=10, ipady=1)

    tk.Label(workspace_panel, text="Ласкаво просимо до панелі адміністратора", font=("Helvetica", 18), bg="#555", fg="white").pack(pady=20)


def send_data_to_server(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("127.0.0.1", 8080)
        client_socket.connect(server_address)

        client_socket.send(data.encode())
        server_response = client_socket.recv(8192).decode()

        client_socket.close()
        return server_response
    except Exception as e:
        return f"ERROR,{str(e)}"


def add_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, status_message_label, submit_button, workspace_panel):
    data = f"ADD_PATIENT,{first_name},{last_name},{middle_name},{birth_date},{contact}"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]

    if status == "SUCCESS" and len(response_parts) > 1:
        patients_data = response_parts[1].strip().split("|")
        patient = Patient(patient_id=int(patients_data[0]), first_name=patients_data[1], last_name=patients_data[2], middle_name=patients_data[3], birth_date=patients_data[4], contact=patients_data[5])

        for widget in workspace_panel.winfo_children():
            widget.destroy()

        create_patient_mini_window(workspace_panel, patient)
    elif response_parts[0] == "EXISTS":
        display_error_message("Такий пацієнт вже є в базі!", input_fields, status_message_label, submit_button)
    else:
        display_error_message("Не вдалося додати пацієнта!", input_fields, status_message_label, submit_button)


def delete_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, status_message_label, submit_button, workspace_panel):
    data = f"DELETE_PATIENT,{first_name},{last_name},{middle_name},{birth_date},{contact}"
    response = send_data_to_server(data)

    if response == "SUCCESS":
        messagebox.showinfo("Успішно", "Пацієнта успішно видалено!")
        display_error_message("", input_fields, status_message_label, submit_button)
    elif response == "NOT_FOUND":
        display_error_message("Такого пацієнта немає в базі!", input_fields, status_message_label, submit_button)
    else:
        display_error_message("Не вдалося видалити пацієнта!", input_fields, status_message_label, submit_button)


def search_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, status_message_label, submit_button, workspace_panel):
    data = f"SEARCH_PATIENT,{first_name},{last_name},{middle_name},{birth_date},{contact}"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]

    if status == "SUCCESS" and len(response_parts) > 1:
        patients_data = response_parts[1].strip().split("|")
        patient = Patient(patient_id=int(patients_data[0]), first_name=patients_data[1], last_name=patients_data[2], middle_name=patients_data[3], birth_date=patients_data[4], contact=patients_data[5])

        scrollable_frame, canvas = create_scrollable_workspace(workspace_panel)
        create_patient_mini_window(scrollable_frame, patient)

        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    elif status == "NOT_FOUND":
        display_error_message("Такого пацієнта немає в базі!", input_fields, status_message_label, submit_button)
    else:
        display_error_message("Помилка під час пошуку пацієнта!", input_fields, status_message_label, submit_button)


def get_all_patients(workspace_panel):
    scrollable_frame, canvas = create_scrollable_workspace(workspace_panel)

    data = "GET_PATIENTS"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]
    patients = []

    if status == "SUCCESS" and len(response_parts) > 1:
        patients_data = response_parts[1].strip().split("\n")

        for patient_line in patients_data:
            if not patient_line.strip():
                continue

            patient_parts = patient_line.split("|")
            if len(patient_parts) == 6:
                patient = Patient(patient_id=int(patient_parts[0]), first_name=patient_parts[1], last_name=patient_parts[2], middle_name=patient_parts[3], birth_date=patient_parts[4], contact=patient_parts[5])
                patients.append(patient)

        if patients:
            for patient in patients:
                create_patient_mini_window(scrollable_frame, patient)

            scrollable_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
    elif status == "NO_PATIENTS":
        messagebox.showinfo("Інформація", "В базі даних немає пацієнтів.")
    else:
        messagebox.showerror("Помилка", "Не вдалося отримати дані про пацієнтів.")


def get_patient_visits(patient_id, workspace_panel):
    data = f"GET_PATIENT_VISITS,{patient_id}"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]
    visits = []

    if status == "SUCCESS" and len(response_parts) > 1:
        visits_data = response_parts[1].strip().split("\n")

        for visit_line in visits_data:
            if not visit_line.strip():
                continue

            visit_parts = visit_line.split("|")
            if len(visit_parts) == 11:
                formatted_time = visit_parts[7].split(".")[0]
                patientVisit = PatientVisit(id=int(visit_parts[0]), first_name=visit_parts[1], last_name=visit_parts[2], middle_name=visit_parts[3], birth_date=visit_parts[4], contact=visit_parts[5], visit_date=visit_parts[6], visit_time=formatted_time, doctor_name=visit_parts[8], diagnosis=visit_parts[9], treatment=visit_parts[10])

                visits.append(patientVisit)

        if visits:
            open_patient_details(workspace_panel, visits)
    elif status == "NO_VISITS":
        messagebox.showinfo("Інформація", "Для пацієнта немає візитів.")
    else:
        messagebox.showerror("Помилка", "Не вдалося отримати дані про візити.")


def get_patient_and_doctor(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, input_fields, status_message_label, continue_button, workspace_panel):
    data = (f"CHECK_PATIENT_DOCTOR,{patient_first_name},{patient_last_name},{patient_middle_name},{patient_birth_date},{patient_contact},{doctor_first_name},{doctor_last_name},{doctor_middle_name}")
    response = send_data_to_server(data)

    if response == "SUCCESS":
        current_date = datetime.now().date()
        get_available_slots(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, current_date, workspace_panel)
    elif response == "NOT_FOUND_Patient":
        display_error_message("Такого пацієнта немає в базі!", input_fields, status_message_label, continue_button)
    elif response == "NOT_FOUND_Doctor":
        display_error_message("Такого лікаря немає в базі!", input_fields, status_message_label, continue_button)
    elif response == "NOT_FOUND_Patient_AND_Doctor":
        display_error_message("Такого пацієнта та лікаря немає в базі!", input_fields, status_message_label, continue_button)
    else:
        display_error_message("Сталася помилка при перевірці даних на сервері!", input_fields, status_message_label, continue_button)


def get_available_slots(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, current_date, workspace_panel):
    data = f"GET_AVAILABLE_SLOTS,{doctor_first_name},{doctor_last_name},{doctor_middle_name},{current_date}"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]
    slots = []

    if status == "SUCCESS":
        slots_data = response_parts[1].strip().split("\n")

        for slot_line in slots_data:
            if not slot_line.strip():
                continue

            slot_parts = slot_line.split("|")
            if len(slot_parts) == 4:
                formatted_time = slot_parts[2].split(".")[0]
                slot = DoctorSlot(slot_id=slot_parts[0], workDate=slot_parts[1], startTime=formatted_time, doctorName=slot_parts[3])

                slots.append(slot)

        open_date_selection_window(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, workspace_panel, slots, slots_available=True, current_date=current_date)
    elif response == "NO_SLOTS":
        open_date_selection_window(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, workspace_panel, slots=[], slots_available=False, current_date=current_date)
    else:
        messagebox.showerror("Помилка", "Не вдалося отримати вільні слоти.")


def book_appointment(slot_id, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, workspace_panel):
    data = (f"BOOK_APPOINTMENT,{slot_id},{patient_first_name},{patient_last_name},{patient_middle_name},{patient_birth_date},{patient_contact}")

    response = send_data_to_server(data)

    for widget in workspace_panel.winfo_children():
        widget.destroy()

    if response == "SUCCESS":
        tk.Label(workspace_panel, text="Запис на прийом успішно створено!", font=("Helvetica", 18), fg="lightgreen", bg="#555").pack(expand=True)
    elif response == "ALREADY_BOOKED":
        tk.Label(workspace_panel, text="Цей слот вже зайнятий!", font=("Helvetica", 18), fg="lightgreen", bg="#555").pack(expand=True)
    elif response == "ERROR":
        tk.Label(workspace_panel, text="Не вдалося створити запис. Спробуйте ще раз.", font=("Helvetica", 18), fg="red", bg="#555").pack(expand=True)
    else:
        tk.Label(workspace_panel, text=f"Сталася невідома помилка: {response}", font=("Helvetica", 18), fg="red", bg="#555").pack(expand=True)


def get_patient_appointment(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, input_fields, status_message_label, continue_button, workspace_panel):
    data = (f"GET_PATIENT_APPOINTMENT,{patient_first_name},{patient_last_name},{patient_middle_name},{patient_birth_date},{patient_contact}")
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]
    visits = []

    if status == "SUCCESS" and len(response_parts) > 1:
        visits_data = response_parts[1].strip().split("\n")

        for visit_line in visits_data:
            if not visit_line.strip():
                continue

            visit_parts = visit_line.split("|")
            if len(visit_parts) == 11:
                formatted_time = visit_parts[7].split(".")[0]
                patientVisit = PatientVisit(id=int(visit_parts[0]), first_name=visit_parts[1], last_name=visit_parts[2], middle_name=visit_parts[3], birth_date=visit_parts[4], contact=visit_parts[5], visit_date=visit_parts[6], visit_time=formatted_time, doctor_name=visit_parts[8], diagnosis=visit_parts[9], treatment=visit_parts[10])

                visits.append(patientVisit)

        if visits:
            open_patient_future_appointment(workspace_panel, visits)
    elif response == "NOT_FOUND_Patient":
        display_error_message("Такого пацієнта немає в базі!", input_fields, status_message_label, continue_button)
    elif response == "NOT_FOUND_Patient":
        display_error_message("У цього пацієнта немає записів!", input_fields, status_message_label, continue_button)
    else:
        display_error_message("Сталася помилка при перевірці даних на сервері!", input_fields, status_message_label, continue_button)


def cancel_appointment(visit_date, visit_time, first_name, last_name, middle_name, birth_date, contact, workspace_panel):
    data = f"CANCEL_APPOINTMENT,{first_name},{last_name},{middle_name},{birth_date},{contact},{visit_date},{visit_time}"
    response = send_data_to_server(data)

    if response == "SUCCESS":
        messagebox.showinfo("Успіх", "Запис успішно скасовано!")
    elif response == "NOT_FOUND":
        messagebox.showwarning("Не знайдено", "Запис не знайдено!")
    else:
        messagebox.showerror("Помилка", "Сталася помилка при скасуванні запису!")

    get_patient_appointment(first_name, last_name, middle_name, birth_date, contact, {}, None, None, workspace_panel)


def exit_application():
    send_data_to_server("LOGOUT")

    show_login_screen()


def display_error_message(message, input_fields, status_message_label, submit_button):
    for field in input_fields.values():
        if isinstance(field, tk.Entry):
            field.delete(0, tk.END)
            field.insert(0, "")

    placeholders = {
        "Прізвище": "Введіть прізвище",
        "Ім'я": "Введіть ім'я",
        "По-батькові": "Введіть по-батькові",
        "Дата народження": "yyyy-mm-dd",
        "Контакт": "+380---------"
    }

    for placeholder_label, field in zip(placeholders, input_fields.values()):
        if isinstance(field, tk.Entry):
            field.insert(0, placeholders[placeholder_label])

    status_message_label.config(text=message, fg="lightgreen")
    status_message_label.pack(before=submit_button)


def set_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def patient_form(workspace_panel, operation):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    operation_title = {
        "add": "Додавання пацієнта",
        "delete": "Видалення пацієнта",
        "search": "Пошук пацієнта"
    }
    button_text = {
        "add": "Додати пацієнта",
        "delete": "Видалити пацієнта",
        "search": "Знайти пацієнта"
    }

    operation_title_text = operation_title.get(operation, "Невідома операція")
    button_text_label = button_text.get(operation, "Виконати")

    tk.Label(workspace_panel, text=operation_title_text, font=("Helvetica", 18), bg="#555", fg="lightgreen", anchor="w").pack(pady=(0, 5), padx=20, fill="x")

    form_fields = [
        ("Прізвище", "Введіть прізвище"),
        ("Ім'я", "Введіть ім'я"),
        ("По-батькові", "Введіть по-батькові"),
        ("Дата народження", "yyyy-mm-dd"),
        ("Контакт", "+380---------")
    ]
    input_fields = {}
    error_messages = {}

    for field_label, placeholder in form_fields:
        field_frame = tk.Frame(workspace_panel, bg="#555")
        field_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(field_frame, text=field_label, font=("Helvetica", 16), bg="#555", fg="white", anchor="w").pack(fill="x")

        entry = tk.Entry(field_frame, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
        set_placeholder(entry, placeholder)
        entry.focus_set()
        entry.pack(fill="x", pady=(10, 0), ipadx=5, ipady=5)
        input_fields[field_label] = entry

        field_error_message = tk.Label(field_frame, text="", font=("Helvetica", 12), bg="#555", fg="lightgreen", anchor="w")
        field_error_message.pack(fill="x", pady=(4, 0))
        error_messages[field_label] = field_error_message

    def process_patient_data():
        has_error = False

        for error_label in error_messages.values():
            error_label.config(text="")
        main_status_label.config(text="")

        first_name = input_fields["Ім'я"].get().strip()
        last_name = input_fields["Прізвище"].get().strip()
        middle_name = input_fields["По-батькові"].get().strip()
        birth_date = input_fields["Дата народження"].get().strip()
        contact = input_fields["Контакт"].get().strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", last_name):
            error_messages["Прізвище"].config(text="Прізвище повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", first_name):
            error_messages["Ім'я"].config(text="Ім'я повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", middle_name):
            error_messages["По-батькові"].config(text="По-батькові повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", birth_date):
            error_messages["Дата народження"].config(text="Дата повинна бути у форматі yyyy-mm-dd")
            has_error = True
        else:
            try:
                datetime.strptime(birth_date, "%Y-%m-%d")
            except ValueError:
                error_messages["Дата народження"].config(text="Введіть коректну дату (yyyy-mm-dd)")
                has_error = True

        if not re.match(r"^\+380\d{9}$", contact):
            error_messages["Контакт"].config(text="Контакт повинен бути у форматі +380---------")
            has_error = True

        if has_error:
            return

        if (operation == "add"):
            add_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, main_status_label, submit_button, workspace_panel)
        elif (operation == "delete"):
            delete_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, main_status_label, submit_button, workspace_panel)
        elif (operation == "search"):
            search_patient(first_name, last_name, middle_name, birth_date, contact, input_fields, main_status_label, submit_button, workspace_panel)

    main_status_label = tk.Label(workspace_panel, text="", font=("Helvetica", 14), bg="#555", fg="lightgreen", anchor="center", height=2)
    main_status_label.pack(fill="x", padx=10)

    submit_button = tk.Button(workspace_panel, text=button_text_label, command=process_patient_data, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=60, pady=5)
    submit_button.pack(pady=10, padx=20, fill="x")


def create_patient_mini_window(workspace_panel, patient):
    patient_frame = tk.Frame(workspace_panel, bg="#4a4a4a", bd=2, relief="groove", highlightbackground="lightgreen", highlightthickness=2, height=140)
    patient_frame.pack(fill="both", padx=10, pady=5)

    top_frame = tk.Frame(patient_frame, bg="#4a4a4a")
    top_frame.pack(fill="both", expand=True, padx=4, pady=(2, 0))

    image_container = tk.Frame(top_frame, bg="#4a4a4a", width=90, height=90)
    image_container.pack(side="left")
    load_image(container=image_container, image_path="images/patient.jpg", image_size=(75, 75), background_color="#4a4a4a", placeholder_text="Фото", placeholder_font=("Helvetica", 12, "bold"))

    text_frame = tk.Frame(top_frame, bg="#4a4a4a")
    text_frame.pack(side="left", fill="both", expand=True, padx=6, pady=8)

    tk.Label(text_frame, text=patient.get_full_name(), font=("Helvetica", 14, "bold"), bg="#4a4a4a", fg="white", anchor="w").pack(fill="both", pady=(0, 3))
    tk.Label(text_frame, text=patient.get_birth_info(), font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady = (3, 3))
    tk.Label(text_frame, text=patient.get_contact_info(), font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady=(3, 0))

    bottom_frame = tk.Frame(patient_frame, bg="#4a4a4a")
    bottom_frame.pack(fill="both", padx=4, pady=(0, 2))

    view_button = tk.Button(bottom_frame, text="Переглянути", command=lambda pid=patient.get_id(): get_patient_visits(pid, workspace_panel), bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=5, pady=2)
    view_button.pack(fill="both")

    image_container.pack_propagate(False)


def create_scrollable_workspace(workspace_panel):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    container = tk.Frame(workspace_panel, bg="#4a4a4a")
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#4a4a4a", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tk.Frame(canvas, bg="#4a4a4a")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    return scrollable_frame, canvas


def open_patient_details(workspace_panel, visits):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    patient = visits[0]

    container = tk.Frame(workspace_panel, bg="#4a4a4a")
    container.pack(fill="both", expand=True, padx=35)

    header_frame = tk.Frame(container, bg="#4a4a4a", pady=10)
    header_frame.pack(fill="x", padx=10)

    image_container = tk.Frame(header_frame, bg="#4a4a4a", width=90, height=90)
    image_container.pack(side="left")
    load_image(container=image_container, image_path="images/patient.jpg", image_size=(80, 80), background_color="#4a4a4a", placeholder_text="Фото", placeholder_font=("Helvetica", 12, "bold"))

    text_frame = tk.Frame(header_frame, bg="#4a4a4a")
    text_frame.pack(side="left", padx=10)

    full_name = f"{patient.get_last_name()} {patient.get_first_name()} {patient.get_middle_name()}"
    tk.Label(text_frame, text=patient.get_full_name(), font=("Helvetica", 14, "bold"), bg="#4a4a4a", fg="white", anchor="w").pack(fill="both", pady=(0, 3))

    birth_date = f"Дата народження: {patient.get_birth_date()}"
    tk.Label(text_frame, text=birth_date, font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady=(3, 3))

    contact = f"Контакт: {patient.get_contact()}"
    tk.Label(text_frame, text=contact, font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady=(3, 0))

    tk.Frame(container, bg="lightgreen", height=2).pack(fill="x", pady=10)
    tk.Label(container, text="Заплановані візити", font=("Helvetica", 16, "bold"), bg="#4a4a4a", fg="white").pack(fill="x", padx=10, pady=5)

    for visit in [v for v in visits if not v.get_diagnosis() and not v.get_treatment()]:
        create_visit_frame(container, visit.visit_date, visit.get_visit_time(), visit.get_doctor_name(), visit.get_diagnosis(), visit.get_treatment())

    tk.Frame(container, bg="lightgreen", height=2).pack(fill="x", pady=10)
    tk.Label(container, text="Попередні візити", font=("Helvetica", 16, "bold"), bg="#4a4a4a", fg="white").pack(fill="x", padx=10, pady=5)

    for visit in [v for v in visits if v.get_diagnosis() or v.get_treatment()]:
        create_visit_frame(container, visit.get_visit_date(), visit.get_visit_time(), visit.get_doctor_name(), visit.get_diagnosis(), visit.get_treatment())


def create_table_block(parent, header, content):
    block = tk.Frame(parent, bg="#333", highlightbackground="white", highlightthickness=1)
    block.pack(side="left", fill="both", expand=True)

    tk.Label(block, text=header, font=("Helvetica", 12, "bold"), bg="#333", fg="white").pack()
    tk.Frame(block, bg="white", height=1).pack(fill="x", pady=2)  # Лінія
    tk.Label(block, text=content, font=("Helvetica", 10), bg="#333", fg="lightgreen", wraplength=200).pack()


def create_visit_frame(parent, date, time, doctor, diagnosis, treatment):
    frame = tk.Frame(parent, bg="#333", bd=1, relief="solid", highlightbackground="lightgreen", highlightthickness=1)
    frame.pack(fill="x", padx=10, pady=10)

    # Перший рядок
    top_row = tk.Frame(frame, bg="#333", bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)
    top_row.pack(fill="x", pady=(0, 5))

    create_table_block(top_row, "Дата", date)
    create_table_block(top_row, "Час", time)
    create_table_block(top_row, "Лікар", doctor)

    # Другий рядок
    bottom_row = tk.Frame(frame, bg="#333", bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)
    bottom_row.pack(fill="x", pady=(5, 0))

    create_table_block(bottom_row, "Діагноз", diagnosis)
    create_table_block(bottom_row, "Лікування", treatment)


def create_visit_booking_form(workspace_panel):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    tk.Label(workspace_panel, text="Запис на візит", font=("Helvetica", 18), bg="#555", fg="lightgreen", anchor="w").pack(pady=(0, 5), padx=20, fill="x")

    form_fields = [
        ("Прізвище пацієнта", "Введіть прізвище"),
        ("Ім'я пацієнта", "Введіть ім'я"),
        ("По-батькові пацієнта", "Введіть по-батькові"),
        ("Дата народження пацієнта", "yyyy-mm-dd"),
        ("Контакт пацієнта", "+380---------"),
        ("Прізвище лікаря", "Введіть прізвище"),
        ("Ім'я лікаря", "Введіть ім'я"),
        ("По-батькові лікаря", "Введіть по-батькові"),
    ]
    input_fields = {}
    error_messages = {}

    for field_label, placeholder in form_fields:
        field_frame = tk.Frame(workspace_panel, bg="#555")
        field_frame.pack(fill="x", padx=20)

        tk.Label(field_frame, text=field_label, font=("Helvetica", 16), bg="#555", fg="white", anchor="w").pack(fill="x", pady=(3, 0))

        entry = tk.Entry(field_frame, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
        set_placeholder(entry, placeholder)
        entry.focus_set()
        entry.pack(fill="x", pady=(2, 0), ipadx=5, ipady=5)
        input_fields[field_label] = entry

        field_error_message = tk.Label(field_frame, text="", font=("Helvetica", 12), bg="#555", fg="lightgreen", anchor="w")
        field_error_message.pack(fill="x", pady=(2, 0))
        error_messages[field_label] = field_error_message

    def proceed_to_date_selection():
        has_error = False

        for error_label in error_messages.values():
            error_label.config(text="")
        main_status_label.config(text="")

        patient_first_name = input_fields["Ім'я пацієнта"].get().strip()
        patient_last_name = input_fields["Прізвище пацієнта"].get().strip()
        patient_middle_name = input_fields["По-батькові пацієнта"].get().strip()
        patient_birth_date = input_fields["Дата народження пацієнта"].get().strip()
        patient_contact = input_fields["Контакт пацієнта"].get().strip()
        doctor_first_name = input_fields["Ім'я лікаря"].get().strip()
        doctor_last_name = input_fields["Прізвище лікаря"].get().strip()
        doctor_middle_name = input_fields["По-батькові лікаря"].get().strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_last_name):
            error_messages["Прізвище пацієнта"].config(text="Прізвище повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_first_name):
            error_messages["Ім'я пацієнта"].config(text="Ім'я повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_middle_name):
            error_messages["По-батькові пацієнта"].config(text="По-батькові повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", patient_birth_date):
            error_messages["Дата народження пацієнта"].config(text="Дата повинна бути у форматі yyyy-mm-dd")
            has_error = True
        else:
            try:
                datetime.strptime(patient_birth_date, "%Y-%m-%d")
            except ValueError:
                error_messages["Дата народження пацієнта"].config(text="Введіть коректну дату (yyyy-mm-dd)")
                has_error = True

        if not re.match(r"^\+380\d{9}$", patient_contact):
            error_messages["Контакт пацієнта"].config(text="Контакт повинен бути у форматі +380---------")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", doctor_last_name):
            error_messages["Прізвище лікаря"].config(text="Прізвище повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", doctor_first_name):
            error_messages["Ім'я лікаря"].config(text="Ім'я повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", doctor_middle_name):
            error_messages["По-батькові лікаря"].config(text="По-батькові повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if has_error:
            return

        get_patient_and_doctor(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact,  doctor_first_name, doctor_last_name, doctor_middle_name, input_fields, main_status_label, continue_button, workspace_panel)

    main_status_label = tk.Label(workspace_panel, text="", font=("Helvetica", 14), bg="#555", fg="lightgreen", anchor="center")
    main_status_label.pack(fill="x", padx=10)

    continue_button = tk.Button(workspace_panel, text="Продовжити", command=proceed_to_date_selection, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=60, pady=5)
    continue_button.pack(pady=5, padx=20, fill="x")


def open_date_selection_window(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, workspace_panel, slots=None, slots_available=True, current_date=None):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    if slots is None:
        slots = []

    if current_date is None:
        current_date = datetime.now().date()

    # Заголовок з вибраною датою
    tk.Label(workspace_panel, text=f"Доступні години на {current_date}", font=("Helvetica", 18, "bold"), bg="#555", fg="white").pack(pady=10)

    if not slots_available or not slots:
        tk.Label(workspace_panel, text="Немає доступних годин на запис", font=("Helvetica", 14), bg="#555", fg="lightgreen").pack(pady=20)
    else:
        for slot in slots:
            slot_frame = tk.Frame(workspace_panel, bg="#333", bd=1, relief="solid", highlightbackground="lightgreen", highlightthickness=1)
            slot_frame.pack(fill="x", padx=10, pady=10)

            in_slot_frame = tk.Frame(slot_frame, bg="#333", relief="solid")
            in_slot_frame.pack(fill="x", pady=5, padx=5)

            create_table_block(in_slot_frame, "Лікар", slot.get_doctor_name())
            create_table_block(in_slot_frame, "Дата", slot.get_work_date())
            create_table_block(in_slot_frame, "Час", slot.get_start_time())

            tk.Button(in_slot_frame, text="Записати", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=10, pady=5, command=lambda slot_id=slot.get_slot_id(): book_appointment(slot_id, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, workspace_panel)).pack(side="right", padx=(8, 0), pady=5)

    button_frame = tk.Frame(workspace_panel, bg="#555")
    button_frame.pack(fill="x", pady=10)

    back_button = tk.Button(button_frame, text="Назад", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=25, pady=5)
    forward_button = tk.Button(button_frame, text="Вперед", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=25, pady=5)

    def update_button_states():
        back_button.config(state="disabled" if current_date <= datetime.now().date() else "normal")
        forward_button.config(state="disabled" if current_date >= datetime.now().date() + timedelta(days=7) else "normal")

    def change_date(direction):
        nonlocal current_date
        if direction == "back" and current_date > datetime.now().date():
            current_date -= timedelta(days=1)
        elif direction == "forward" and current_date < datetime.now().date() + timedelta(days=7):
            current_date += timedelta(days=1)
        get_available_slots(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, doctor_first_name, doctor_last_name, doctor_middle_name, current_date, workspace_panel)

    back_button.config(command=lambda: change_date("back"))
    forward_button.config(command=lambda: change_date("forward"))

    back_button.pack(side="left", padx=10, pady=10)
    forward_button.pack(side="right", padx=10, pady=10)

    update_button_states()


def cancel_visit_form(workspace_panel):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    tk.Label(workspace_panel, text="Скасувати запис на візит", font=("Helvetica", 18), bg="#555", fg="lightgreen", anchor="w").pack(pady=(0, 5), padx=20, fill="x")

    form_fields = [
        ("Прізвище пацієнта", "Введіть прізвище"),
        ("Ім'я пацієнта", "Введіть ім'я"),
        ("По-батькові пацієнта", "Введіть по-батькові"),
        ("Дата народження пацієнта", "yyyy-mm-dd"),
        ("Контакт пацієнта", "+380---------")
    ]
    input_fields = {}
    error_messages = {}

    for field_label, placeholder in form_fields:
        field_frame = tk.Frame(workspace_panel, bg="#555")
        field_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(field_frame, text=field_label, font=("Helvetica", 16), bg="#555", fg="white", anchor="w").pack(fill="x")

        entry = tk.Entry(field_frame, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
        set_placeholder(entry, placeholder)
        entry.focus_set()
        entry.pack(fill="x", pady=(10, 0), ipadx=5, ipady=5)
        input_fields[field_label] = entry

        field_error_message = tk.Label(field_frame, text="", font=("Helvetica", 12), bg="#555", fg="lightgreen", anchor="w")
        field_error_message.pack(fill="x", pady=(4, 0))
        error_messages[field_label] = field_error_message

    def proceed_to_date_selection():
        has_error = False

        for error_label in error_messages.values():
            error_label.config(text="")
        main_status_label.config(text="")

        patient_first_name = input_fields["Ім'я пацієнта"].get().strip()
        patient_last_name = input_fields["Прізвище пацієнта"].get().strip()
        patient_middle_name = input_fields["По-батькові пацієнта"].get().strip()
        patient_birth_date = input_fields["Дата народження пацієнта"].get().strip()
        patient_contact = input_fields["Контакт пацієнта"].get().strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_last_name):
            error_messages["Прізвище пацієнта"].config(text="Прізвище повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_first_name):
            error_messages["Ім'я пацієнта"].config(text="Ім'я повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^[a-zA-Zа-яА-ЯїЇєЄіІ']{2,}$", patient_middle_name):
            error_messages["По-батькові пацієнта"].config(text="По-батькові повинно містити мінімум 2 літери та без цифр")
            has_error = True

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", patient_birth_date):
            error_messages["Дата народження пацієнта"].config(text="Дата повинна бути у форматі yyyy-mm-dd")
            has_error = True
        else:
            try:
                datetime.strptime(patient_birth_date, "%Y-%m-%d")
            except ValueError:
                error_messages["Дата народження пацієнта"].config(text="Введіть коректну дату (yyyy-mm-dd)")
                has_error = True

        if not re.match(r"^\+380\d{9}$", patient_contact):
            error_messages["Контакт пацієнта"].config(text="Контакт повинен бути у форматі +380---------")
            has_error = True

        if has_error:
            return

        get_patient_appointment(patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact, input_fields, main_status_label, continue_button, workspace_panel)

    main_status_label = tk.Label(workspace_panel, text="", font=("Helvetica", 14), bg="#555", fg="lightgreen", anchor="center")
    main_status_label.pack(fill="x", padx=10)

    continue_button = tk.Button(workspace_panel, text="Продовжити", command=proceed_to_date_selection, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=60, pady=5)
    continue_button.pack(pady=5, padx=20, fill="x")


def open_patient_future_appointment(workspace_panel, visits):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    patient = visits[0]

    container = tk.Frame(workspace_panel, bg="#4a4a4a")
    container.pack(fill="both", expand=True)

    header_frame = tk.Frame(container, bg="#4a4a4a", pady=10)
    header_frame.pack(fill="x", padx=10)

    image_container = tk.Frame(header_frame, bg="#4a4a4a", width=90, height=90)
    image_container.pack(side="left")
    load_image(container=image_container, image_path="images/patient.jpg", image_size=(80, 80), background_color="#4a4a4a", placeholder_text="Фото", placeholder_font=("Helvetica", 12, "bold"))

    text_frame = tk.Frame(header_frame, bg="#4a4a4a")
    text_frame.pack(side="left", padx=10)

    full_name = f"{patient.get_last_name()} {patient.get_first_name()} {patient.get_middle_name()}"
    tk.Label(text_frame, text=patient.get_full_name(), font=("Helvetica", 14, "bold"), bg="#4a4a4a", fg="white", anchor="w").pack(fill="both", pady=(0, 3))

    birth_date = f"Дата народження: {patient.get_birth_date()}"
    tk.Label(text_frame, text=birth_date, font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady=(3, 3))

    contact = f"Контакт: {patient.get_contact()}"
    tk.Label(text_frame, text=contact, font=("Helvetica", 12), bg="#4a4a4a", fg="lightgreen", anchor="w").pack(fill="both", pady=(3, 0))

    tk.Frame(container, bg="lightgreen", height=2).pack(fill="x", pady=10)

    for visit in visits:
        create_appointment_frame(container, visit, visits)


def create_appointment_frame(parent, visit, visits):
    frame = tk.Frame(parent, bg="#333", bd=1, relief="solid", highlightbackground="lightgreen", highlightthickness=1)
    frame.pack(fill="x", padx=10, pady=10)

    # Перший рядок
    top_row = tk.Frame(frame, bg="#333", bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)
    top_row.pack(fill="x", pady=(0, 5))

    create_table_block(top_row, "Дата", visit.get_visit_date())
    create_table_block(top_row, "Час", visit.get_visit_time())
    create_table_block(top_row, "Лікар", visit.get_doctor_name())

    # Другий рядок
    middle_row = tk.Frame(frame, bg="#333", bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)
    middle_row.pack(fill="x")

    create_table_block(middle_row, "Діагноз", visit.get_diagnosis())
    create_table_block(middle_row, "Лікування", visit.get_treatment())

    bottom_row = tk.Frame(frame, bg="#333", bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)
    bottom_row.pack(fill="x", pady=(5, 0))

    cancel_button = tk.Button(bottom_row, text="Скасувати", command=lambda: cancel_appointment(visit.get_visit_date(), visit.get_visit_time(), visit.get_first_name(), visit.get_last_name(), visit.get_middle_name(), visit.get_birth_date(), visit.get_contact(), parent), bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=5, pady=2)
    cancel_button.pack(fill="both")


def open_doctor_panel(doctor):
    clear_screen()

    main_container = tk.Frame(root, bg="#4a4a4a")
    main_container.pack(fill="both", expand=True)

    doctor_panel = tk.Frame(main_container, bg="#333", width=250)
    doctor_panel.pack(side="left", fill="y")

    workspace_panel = tk.Frame(main_container, bg="#555")
    workspace_panel.pack(side="right", fill="both", expand=True)

    tk.Label(doctor_panel, text="Лікарня 'Здорові разом'", font=("Helvetica", 18, "bold"), bg="#333", fg="white").pack(anchor="center", pady=(20, 15))

    load_image(doctor_panel, "images/doctor.jpg", image_size=(140, 140), background_color="#333", placeholder_text="Лікар лікарні 'Здорові разом'", placeholder_font=("Helvetica", 20))

    last_name = doctor.get_last_name()
    patronym = f"{doctor.get_first_name()} {doctor.get_middle_name()}"
    tk.Label(doctor_panel, text=last_name, font=("Helvetica", 18, "bold"), bg="#333", fg="white").pack(anchor="center", pady=(15, 5))
    tk.Label(doctor_panel, text=patronym, font=("Helvetica", 18, "bold"), bg="#333", fg="white").pack(anchor="center", pady=(5, 15))

    contact = doctor.get_contact()
    tk.Label(doctor_panel, text="Контакт:", font=("Helvetica", 18, "bold"), bg="#333", fg="green").pack(anchor="center", pady=(15, 0))
    tk.Label(doctor_panel, text=contact, font=("Helvetica", 16), bg="#333", fg="white").pack(anchor="center", pady=(0, 15))

    specialization = doctor.get_specialization()
    tk.Label(doctor_panel, text="Спеціальність:", font=("Helvetica", 18, "bold"), bg="#333", fg="green").pack(anchor="center", pady=(15, 0))
    tk.Label(doctor_panel, text=specialization, font=("Helvetica", 16), bg="#333", fg="white").pack(anchor="center", pady=(0, 15))

    appointments_button = tk.Button(doctor_panel, text="Відкрити записи", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=lambda: get_today_appointments(doctor.get_doctor_id(), workspace_panel))
    appointments_button.pack(pady=(200, 8), padx=10, ipady=1)

    exit_button = tk.Button(doctor_panel, text="Вихід", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), width=30, height=2, command=exit_application)
    exit_button.pack(pady=(8, 15), padx=10, ipady=1)

    tk.Label(workspace_panel, text="Ласкаво просимо до лікарської панелі", font=("Helvetica", 18), bg="#555", fg="white").pack(pady=20)


def get_today_appointments(doctor_id, workspace_panel):
    today_date = datetime.now().strftime("%Y-%m-%d")
    data = f"GET_TODAY_APPOINTMENTS|{today_date}"
    response = send_data_to_server(data)
    response_parts = response.split(";", 1)

    status = response_parts[0]
    appointments = []

    if status == "SUCCESS":
        appointments_data = response_parts[1].strip().split("\n")

        for appointments_line in appointments_data:
            if not appointments_line.strip():
                continue

            appointments_parts = appointments_line.split("|")
            if len(appointments_parts) == 11:
                formatted_time = appointments_parts[7].split(".")[0]
                appointment = PatientVisit(id=int(appointments_parts[0]), first_name=appointments_parts[1], last_name=appointments_parts[2],  middle_name=appointments_parts[3], birth_date=appointments_parts[4], contact=appointments_parts[5], visit_date=appointments_parts[6], visit_time=formatted_time, doctor_name=appointments_parts[8], diagnosis=appointments_parts[9], treatment=appointments_parts[10])

                appointments.append(appointment)

        if appointments:
            open_appointments(workspace_panel, doctor_id, appointments)

    elif status == "NO_APPOINTMENTS":
        open_appointments(workspace_panel, doctor_id, appointments)
    else:
        messagebox.showerror("Помилка", "Помилка отримання даних")


def submit_review(appointment, diagnosis, treatment, doctor_id, workspace_panel):
    try:
        data = (f"ADD_DIAGNOSIS|{appointment.get_last_name()}|{appointment.get_first_name()}|{appointment.get_middle_name()}|{appointment.get_visit_date()}|{appointment.get_visit_time()}|{diagnosis}|{treatment}|{doctor_id}")
        response = send_data_to_server(data)

        if response == "SUCCESS":
            messagebox.showinfo("Успіх", "Діагноз та лікування успішно внесено в базу даних!")
        elif response == "NOT_FOUND":
            messagebox.showwarning("Помилка", "Запис про пацієнта не знайдено!")
        else:
            messagebox.showerror("Помилка", "Не вдалося внести дані до бази. Спробуйте ще раз.")
    except Exception as e:
        messagebox.showerror("Помилка підключення", f"Помилка під час відправки даних: {str(e)}")

    get_today_appointments(doctor_id, workspace_panel)


def open_appointments(workspace_panel, doctor_id, appointments=None):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    if appointments is None:
        appointments = []

    current_date = datetime.now().date()

    tk.Label(workspace_panel, text=f"Записи на {current_date}", font=("Helvetica", 18, "bold"), bg="#555", fg="white").pack(pady=10)

    if not appointments:
        tk.Label(workspace_panel, text="Немає не переглянутих записів", font=("Helvetica", 14), bg="#555", fg="lightgreen").pack(
            pady=20)
    else:
        for appointment in appointments:
            appointment_frame = tk.Frame(workspace_panel, bg="#333", bd=1, relief="solid", highlightbackground="lightgreen", highlightthickness=1)
            appointment_frame.pack(fill="x", padx=10, pady=10)

            in_appointment_frame = tk.Frame(appointment_frame, bg="#333", relief="solid")
            in_appointment_frame.pack(fill="x", pady=5, padx=5)

            full_name = f"{appointment.get_last_name()} {appointment.get_first_name()[0]}. {appointment.get_middle_name()[0]}."
            create_table_block(in_appointment_frame, "Дата", appointment.get_visit_date())
            create_table_block(in_appointment_frame, "Час", appointment.get_visit_time())
            create_table_block(in_appointment_frame, "Пацієнт", full_name)

            tk.Button(in_appointment_frame, text="Огляд", bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=10, pady=5, command=lambda appt=appointment: open_patient_review(workspace_panel, doctor_id, appt)).pack(side="right", padx=(8, 0), pady=5)


def open_patient_review(workspace_panel, doctor_id, appointment):
    for widget in workspace_panel.winfo_children():
        widget.destroy()

    tk.Label(workspace_panel, text="Огляд пацієнта", font=("Helvetica", 18, "bold"), bg="#555", fg="lightgreen").pack(pady=10)

    complete_form_fields = [
        ("Прізвище", appointment.get_last_name()),
        ("Ім'я", appointment.get_first_name()),
        ("По-батькові", appointment.get_middle_name()),
    ]

    for field_label, value in complete_form_fields:
        field_frame = tk.Frame(workspace_panel, bg="#555")
        field_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(field_frame, text=field_label, font=("Helvetica", 16), bg="#555", fg="white").pack(anchor="w")

        entry = tk.Entry(field_frame, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
        entry.focus_set()
        entry.insert(0, value)
        entry.pack(fill="x", pady=(10, 0), ipadx=5, ipady=5)
        entry.config(state="disabled", disabledbackground="white", disabledforeground="black")

    uncomplete_form_fields = [
        ("Діагноз", "Введіть діагноз"),
        ("Лікування", "Введіть лікування"),
    ]
    input_fields = {}
    error_messages = {}

    for field_label, placeholder in uncomplete_form_fields:
        field_frame = tk.Frame(workspace_panel, bg="#555")
        field_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(field_frame, text=field_label, font=("Helvetica", 16), bg="#555", fg="white").pack(anchor="w")

        entry = tk.Entry(field_frame, highlightthickness=2, highlightbackground="lightgreen", highlightcolor="lightgreen", bg="white", fg="black")
        set_placeholder(entry, placeholder)
        entry.pack(fill="x", pady=(10, 0), ipadx=5, ipady=5)
        input_fields[field_label] = entry

        field_error_message = tk.Label(field_frame, text="", font=("Helvetica", 12), bg="#555", fg="lightgreen", anchor="w")
        field_error_message.pack(fill="x", pady=(4, 0))
        error_messages[field_label] = field_error_message

    def proceed_to_date_review():
        has_error = False

        for error_label in error_messages.values():
            error_label.config(text="")

        diagnosis = input_fields["Діагноз"].get().strip()
        treatment = input_fields["Лікування"].get().strip()

        placeholder_diagnosis = "Введіть діагноз"
        placeholder_treatment = "Введіть лікування"

        if diagnosis == placeholder_diagnosis or not re.match(r"^(.*?[a-zA-Zа-яА-ЯїЇєЄіІ0-9]){4,}.*$", diagnosis):
            error_messages["Діагноз"].config(text="Діагноз повинен містити мінімум 4 літер")
            has_error = True

        if treatment == placeholder_treatment or not re.match(r"^(.*?[a-zA-Zа-яА-ЯїЇєЄіІ0-9]){4,}.*$", treatment):
            error_messages["Лікування"].config(text="Лікування повинен містити мінімум 4 літер")
            has_error = True

        if has_error:
            return

        submit_review(appointment, diagnosis, treatment, doctor_id, workspace_panel)

    tk.Button(workspace_panel, text="Завершити огляд", command=proceed_to_date_review, bg="white", fg="black", borderwidth=1, highlightbackground="lightgreen", font=("Helvetica", 14), padx=20, pady=5).pack(pady=15, padx=20, fill="x")


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


# Головне вікно
root = tk.Tk()
root.title("Лікарня 'Здорові разом'")
root.geometry("700x810")
root.configure(bg="#4a4a4a")

show_login_screen()
root.mainloop()