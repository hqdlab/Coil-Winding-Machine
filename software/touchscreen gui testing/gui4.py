import tkinter as tk
import tkinter.font as tkFont

# Create the main window
root = tk.Tk()
root.title("My GUI")

dfont = tkFont.Font(size=-24)

# Create label
label = tk.Label(root, text="Control", font=dfont)

button_on  = tk.Button(root, text="On",  font=dfont)
button_off = tk.Button(root, text="Off", font=dfont)
button_quit = tk.Button(root, text="Quit", font=dfont, command=root.destroy)

# Lay out
label.pack()
button_on.pack()
button_off.pack()
button_quit.pack()

root.attributes('-fullscreen', True)
    
# Run forever!
root.mainloop()


