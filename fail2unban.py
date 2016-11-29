#!/usr/bin/python

# ========================= Beállítandó paraméterek ============================

# Kötelező paraméter.
# host = ip cím, vagy szerver URL
# pl: host = 'email.server.com'
host = ''
# username = felhasználónév, amivel belép ssh-val a megadott host nevű szerverre
# Kötelező paraméter.
# pl: username = 'mickey'
username = ''
# password = jelszó
# Nem kötelező paraméter! Ha üres akkor a script bekéri futtatások a jelszót.
# pl: password = ''          # A script bekéri a jelszót.
# pl: password = 'pwd123'    # A script nem kér jelszót, gombnyomásra lefut.
password = ''
# port = portszám, amin az ssh kapcsolat működni fog.
# Kötelező paraméter.
port = 22


# ======================= Innetől nemm kell változtatni ========================

import tkinter
import datetime
import paramiko


# ---------------------------- Globális változók -------------------------------

# Globális változó az aktuális jelszó, illetve ssh állapotok tárolására.
status = False


# =============================== Függvények ===================================


# ------------------- Képernyő frissítése, ip lista lekérés --------------------

def refresh():
    global password
    global status
    global main_window
    global data_frame

    if password == '':
        password_input()
    else:
        ssh_connect()

    if status:
        data_frame.destroy()
        data_frame = tkinter.Frame(main_window)
        data_frame.grid(row=1, columnspan=2)
        stdin, stdout, stderr = \
            ssh.exec_command("echo '" + password +
                             "' | sudo -S /usr/bin/fail2ban-client status")
        out = str(stdout.readlines())
        jail_list = out[out.find('Jail list:') +
                        12:out.find('\n', out.find('Jail list:')) - 3]
        jail_list = jail_list.replace(" ", "")
        jail_list = jail_list.split(',')

        display_jail = {}
        display_ip = {}
        i = 1
        for jail_name in jail_list:
            stdin, stdout, stderr = \
                ssh.exec_command("echo '" + password +
                                 "' | sudo -S /usr/bin/fail2ban-client status "
                                 + jail_name)
            out = str(stdout.readlines())
            ip_adresses = out[out.find("IP list:") + 10:]
            ip_adresses = ip_adresses.replace("\\n']", '')
            ip_adresses = ip_adresses.split()
            display_jail[i] = tkinter.Message(data_frame, text=jail_name,
                                              width=250)
            display_jail[i].grid(row=i, column=0, sticky='w')
            if ip_adresses:
                for ip in ip_adresses:
                    display_ip[i] = tkinter.Message(data_frame, text=ip,
                                                    width=350)
                    display_ip[i].grid(row=i, column=1, sticky='w')
                    unban_button = tkinter.Button(data_frame, text="Unban",
                                                  command=lambda j=jail_name,
                                                  x=ip: unban(j, x))
                    unban_button.grid(row=i, column=2, sticky='w')
                    i += 1
            else:
                display_ip[i] = tkinter.Message(data_frame,
                                                text='nincs bannolt ip',
                                                width=350)
                display_ip[i].grid(row=i, column=1, sticky='w')
            i += 1
        now = datetime.datetime.today()
        status_label.configure(text='Frissítve: {:%b.%d. - %H:%M:%S}'
                               .format(now))


# ------------------------------ Jelszó bekérés --------------------------------

def password_input():
    pwd_window = tkinter.Toplevel(main_window)
    pwd_window.geometry('+550+150')
    plabel = tkinter.Label(pwd_window, text='Jelszó:')
    plabel.pack()
    pinput = tkinter.Entry(pwd_window, textvariable=pwd, show='*')
    pinput.pack()
    pinput.focus()
    pbutton = tkinter.Button(pwd_window, text="Ok",
                             command=lambda: password_ok(pwd_window))
    pbutton.pack()
    pwd_window.bind('<Return>', lambda event: password_ok(pwd_window))
    pwd_window.bind('<KP_Enter>', lambda event: password_ok(pwd_window))


# ----------------------------- Jeszó OK gomb ----------------------------------

def password_ok(pwd_window):
    global status_label
    global password

    password = pwd.get()
    pwd_window.destroy()
    refresh()


# --------------------------- SSH kapcsolat kezelése ---------------------------

def ssh_connect():
    global password
    global refresh_button
    global status_label
    global username
    global host
    global status

    try:
        ssh.connect(host, port=port, username=username, password=password)
        refresh_button.configure(bg='green')
        status_label.configure(text='--> Kapcsolatban <--')
        status = True
        return True
    except paramiko.AuthenticationException:
        refresh_button.configure(bg='yellow')
        status_label.configure(text='--> Hibás jelszó <--')
        status = False
        password = ''
        return False
    except:
        refresh_button.configure(bg='red')
        status_label.configure(text='--> Kapcsolódási hiba <--')
        status = False
        password = ''
        return False


# ------------------------------ Unban -----------------------------------------

def unban(unban_jail_name, unban_ip):
    #    print(unban_jail_name)
    #    print(unban_ip)
    status_label.configure(text='--> unban <--')
    stdin, stdout, stderr = ssh.exec_command(
        "echo '" + password + "' | sudo -S /usr/bin/fail2ban-client set " +
        unban_jail_name + ' unbanip ' + unban_ip)
    refresh()
    return


#  ============================= Főprogram =====================================

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

main_window = tkinter.Tk()
pwd = tkinter.StringVar()
main_window.title('Fail2ban blokkolt IP-k listája')
main_window.geometry('400x500+500+100')

data_frame = tkinter.Frame(main_window)

refresh_button = tkinter.Button(main_window, text="Frissítés",
                                command=refresh, activebackground='lightgreen')

status_label = tkinter.Message(main_window, text='--> Nincs kapcsolat <--',
                               width=200)

refresh_button.grid(row=0, column=0)
status_label.grid(row=0, column=1)

data_frame.grid(row=1, columnspan=2)

main_window.mainloop()

ssh.close()
