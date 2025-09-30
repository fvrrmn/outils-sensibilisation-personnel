import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import os

stop_event = None
worker_thread = None
wordlist_path = None

def combinaison_check_wordlist(mdp_secret, path, label_result, progress_bar, stop_event, on_finish):
    start_time = time.time()

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            total_combinaisons = sum(1 for _ in f)
    except Exception as e:
        label_result.after(0, lambda: label_result.config(text=f"Erreur - Lecture fichier : {e}"))
        on_finish()
        return

    if total_combinaisons == 0:
        label_result.after(0, lambda: label_result.config(text="La liste est vide..."))
        on_finish()
        return

    update_every = max(1, total_combinaisons // 500)

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, ligne in enumerate(f, start=1):
                if stop_event.is_set():
                    elapsed = time.time() - start_time
                    label_result.after(0, lambda: label_result.config(text=f"BruteForce arrêté après : {round(elapsed,3)} secondes \n Tentatives réalisées : {idx-1}"))
                    on_finish()
                    return

                tentative = ligne.rstrip("\n\r")

                if tentative == mdp_secret:
                    end_time = time.time()
                    temps = round(end_time - start_time, 3)
                    label_result.after(0, lambda: label_result.config(text=f"Mot de passe trouvé : {mdp_secret} \n Trouvé en {temps} secondes \n ({idx} tentatives)"))
                    on_finish()
                    return

                if idx % update_every == 0 or idx == total_combinaisons:
                    now = time.time()
                    elapsed = now - start_time
                    tried = idx
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

    except Exception as e:
        label_result.after(0, lambda: label_result.config(text=f"Erreur pendant l'analyse : {e}"))
        on_finish()
        return

    label_result.after(0, lambda: label_result.config(text=f"Le mot de passe n'a pas été trouvé dans la liste..."))
    on_finish()

def charger_liste(label_fichier, btn_charger):
    global wordlist_path
    path = filedialog.askopenfilename(title="Sélectionnez un fichier .txt", filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*")])
    if not path:
        return
    wordlist_path = path
    nom = os.path.basename(path)
    label_fichier.config(text=f"Liste chargée : {nom}")
    btn_charger.config(text="Charger de liste")

def toggle_password(entry, eye_btn):
    if entry.cget("show") == "*":
        entry.config(show="")
        eye_btn.config(text="Masquer")
    else:
        entry.config(show="*")
        eye_btn.config(text="Afficher")

def valider_mdp(entry, label_result, progress_bar, btn_valider, btn_cancel, label_fichier):
    global stop_event, worker_thread, wordlist_path

    mdp_secret = entry.get()

    if not wordlist_path:
        messagebox.showerror("Erreur", "Aucune liste importée. \n" \
        "Veuillez charger un fichier .txt ")
        return

    if mdp_secret == "":
        messagebox.showerror("Erreur", "Veuillez saisir un mot de passe")
        return

    entry.config(state="disabled")
    btn_valider.config(state="disabled")
    btn_cancel.config(state="normal")

    label_result.config(text="BruteForce en cours...")
    progress_bar["value"] = 0

    stop_event = threading.Event()

    def on_finish():
        entry.after(0, lambda: entry.config(state="normal"))
        btn_valider.after(0, lambda: btn_valider.config(state="normal"))
        btn_cancel.after(0, lambda: btn_cancel.config(state="disabled"))

    worker_thread = threading.Thread(
        target=combinaison_check_wordlist,
        args=(mdp_secret, wordlist_path, label_result, progress_bar, stop_event, on_finish),
        daemon=True
    )
    worker_thread.start()

def annuler(stop_event):
    if stop_event is not None:
        stop_event.set()

fenetre = tk.Tk()
fenetre.title("Démonstration : Attaque par Dictionnaire by fvrrmn")
fenetre.geometry("540x290")

label_instruction = tk.Label(fenetre, text="Entrez un mot de passe :", font=("Arial", 12))
label_instruction.pack(pady=8)

frame_entry = tk.Frame(fenetre)
frame_entry.pack(pady=5)
entry_mdp = tk.Entry(frame_entry, show="*", font=("Arial", 12))
entry_mdp.grid(row=0, column=0)
btn_eye = tk.Button(frame_entry, text="Afficher", font=("Arial", 10), command=lambda: toggle_password(entry_mdp, btn_eye))
btn_eye.grid(row=0, column=1, padx=6)

frame_file = tk.Frame(fenetre)
frame_file.pack(pady=6)

label_fichier = tk.Label(frame_file, text="Aucune liste importée", font=("Arial", 10))
label_fichier.grid(row=0, column=0, padx=8)

btn_charger = tk.Button(frame_file, text="Choisir une liste", font=("Arial", 10), command=lambda: charger_liste(label_fichier, btn_charger))
btn_charger.grid(row=0, column=1, padx=8)

progress_bar = ttk.Progressbar(fenetre, orient="horizontal", length=480, mode="determinate")
progress_bar.pack(pady=10)

label_result = tk.Label(fenetre, text="", font=("Arial", 11))
label_result.pack(pady=8)

frame_btn = tk.Frame(fenetre)
frame_btn.pack(pady=6)

btn_valider = tk.Button(frame_btn, text="Démarrer", font=("Arial", 12), command=lambda: valider_mdp(entry_mdp, label_result, progress_bar, btn_valider, btn_cancel, label_fichier))
btn_valider.grid(row=0, column=0, padx=6)

btn_cancel = tk.Button(frame_btn, text="Annuler", font=("Arial", 12), command=lambda: annuler(stop_event), state="disabled")
btn_cancel.grid(row=0, column=1, padx=6)

entry_mdp.bind("<Return>", lambda event: valider_mdp(entry_mdp, label_result, progress_bar, btn_valider, btn_cancel, label_fichier))

fenetre.mainloop()
