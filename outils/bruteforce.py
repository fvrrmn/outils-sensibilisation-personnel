import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

stop_event = None
worker_thread = None

def combinaison_check(mdp_secret, label_result, progress_bar, stop_event, on_finish):

    start_time = time.time()
    longueur = len(mdp_secret)
    total_combinaisons = 10 ** longueur

    update_every = max(1, total_combinaisons // 500)

    last_update_time = start_time

    for nombre in range(total_combinaisons):
        if stop_event.is_set():
            elapsed = time.time() - start_time
            def stopped():
                label_result.config(text=f"BruteForce arrêté après : {round(elapsed,3)} secondes \n Tentatives réalisées : {nombre}")
            label_result.after(0, stopped)
            on_finish()
            return

        combinaison = str(nombre).zfill(longueur)

        if combinaison == mdp_secret:
            end_time = time.time()
            temps = round(end_time - start_time, 3)
            def found():
                label_result.config(text=f"Mot de passe trouvé : {mdp_secret} \n Trouvé en {temps} secondes \n ({nombre+1} tentatives)")
            label_result.after(0, found)
            on_finish()
            return

        if (nombre + 1) % update_every == 0 or nombre + 1 == total_combinaisons:
            now = time.time()
            elapsed = now - start_time
            tried = nombre + 1
            speed = tried / elapsed if elapsed > 0 else 0
            remaining = total_combinaisons - tried
            est_remaining = remaining / speed if speed > 0 else float('inf')

            def ui_update():
                progress_bar["maximum"] = total_combinaisons
                progress_bar["value"] = tried
                label_result.config(text=(
                    f"BruteForce en cours... \n {tried} / {total_combinaisons} \n "
                    f"Temps écoulé : {round(elapsed,2)} secondes "
                ))
            progress_bar.after(0, ui_update)

    def not_found():
        label_result.config(text=f"Le mot de passe n'a pas été trouvé...") #Cela n'arrivera pas
    label_result.after(0, not_found)
    on_finish()


def valider_mdp(entry, label_result, progress_bar, btn_valider, btn_cancel):
    global stop_event, worker_thread

    mdp_secret = entry.get()

    if not mdp_secret.isdigit() or not (4 <= len(mdp_secret) <= 8):
        messagebox.showerror("Erreur", "Le mot de passe doit contenir 4 à 8 chiffres ! (Uniquement)")
        return

    longueur = len(mdp_secret)
    total_combinaisons = 10 ** longueur
    if total_combinaisons > 1_000_000:
        if not messagebox.askyesno("Avertissement",
                                   f"Il existe {total_combinaisons} combinaisons. \n"
                                   "Cela peut être long. Voulez-vous continuer ? "):
            return

    entry.config(state="disabled")
    btn_valider.config(state="disabled")
    btn_cancel.config(state="normal")

    label_result.config(text="BruteForce en cours...")
    progress_bar["value"] = 0
    progress_bar["maximum"] = total_combinaisons

    stop_event = threading.Event()

    def on_finish():
        entry.after(0, lambda: entry.config(state="normal"))
        btn_valider.after(0, lambda: btn_valider.config(state="normal"))
        btn_cancel.after(0, lambda: btn_cancel.config(state="disabled"))

    worker_thread = threading.Thread(
        target=combinaison_check,
        args=(mdp_secret, label_result, progress_bar, stop_event, on_finish),
        daemon=True
    )
    worker_thread.start()


def annuler(stop_event):
    if stop_event is not None:
        stop_event.set()


fenetre = tk.Tk()
fenetre.title("Démonstration : BruteForce by fvrrmn")
fenetre.geometry("480x250")

label_instruction = tk.Label(fenetre, text="Entrez un mot de passe (4 à 8 chiffres) :", font=("Arial", 12))
label_instruction.pack(pady=10)

entry_mdp = tk.Entry(fenetre, show="*", font=("Arial", 12))
entry_mdp.pack(pady=5)

progress_bar = ttk.Progressbar(fenetre, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

label_result = tk.Label(fenetre, text="", font=("Arial", 11))
label_result.pack(pady=10)

frame_btn = tk.Frame(fenetre)
frame_btn.pack(pady=5)

btn_valider = tk.Button(frame_btn, text="Valider", font=("Arial", 12),
                        command=lambda: valider_mdp(entry_mdp, label_result, progress_bar, btn_valider, btn_cancel))
btn_valider.grid(row=0, column=0, padx=5)

btn_cancel = tk.Button(frame_btn, text="Annuler", font=("Arial", 12),
                       command=lambda: annuler(stop_event), state="disabled")
btn_cancel.grid(row=0, column=1, padx=5)

entry_mdp.bind("<Return>", lambda event: valider_mdp(entry_mdp, label_result, progress_bar, btn_valider, btn_cancel))

fenetre.mainloop()