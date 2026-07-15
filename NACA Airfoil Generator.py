# IMPORTING NECESSARY LIBRARIES
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def naca4_airfoil(code, chord, n_points):
    """
    Computes the geometry of a NACA 4-digit airfoil.
    Returns all curve arrays and key points for plotting.
    Handles symmetric airfoils without division errors.
    """
    #Extracting different paramaters of the airfoil
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0

    # Cosine-spaced for better edge detail
    beta = np.linspace(0, np.pi, n_points)
    x = 0.5 * chord * (1 - np.cos(beta))

    # Thickness distribution

    xc = x / chord  # non-dimensional x

    yt = 5 * t * chord * (
    0.2969 * np.sqrt(xc)
    - 0.1260 * xc
    - 0.3516 * xc**2
    + 0.2843 * xc**3
    - 0.1036 * xc**4
    )
    
    #Setting up the camber
    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)
    if m == 0 or p == 0:
        # Symmetrical airfoil: mean line is y=0
        yc[:] = 0
        dyc_dx[:] = 0
    else:
        for i, xci in enumerate(xc):
            if xci < p:
                yc[i] = m / (p ** 2) * (2 * p * xci - xci ** 2) * chord
                dyc_dx[i] = (2 * m / (p ** 2)) * (p - xci)
            else:
                yc[i] = m / ((1 - p) ** 2) * (1 - 2 * p + 2 * p * xci - xci ** 2) * chord
                dyc_dx[i] = (2 * m / ((1 - p) ** 2)) * (p - xci)

    #calculating the points to be plotted
    theta = np.arctan(dyc_dx)
    x_upper = x - yt * np.sin(theta)
    y_upper = yc + yt * np.cos(theta)
    x_lower = x + yt * np.sin(theta)
    y_lower = yc - yt * np.cos(theta)

    x_camber = x
    y_camber = yc

    # Max camber
    if m == 0 or p == 0:
        x_max_camber = 0
        y_max_camber = 0
    else:
        x_max_camber = p * chord
        y_max_camber = m * chord

    # Max thickness (where yt is max)
    max_thickness_idx = np.argmax(yt)
    x_max_thickness = x[max_thickness_idx]
    y_max_thickness = yc[max_thickness_idx]

    return (
        x_upper, y_upper,
        x_lower, y_lower,
        x_camber, y_camber,
        x_max_camber, y_max_camber,
        x_max_thickness, y_max_thickness
    )

#------ GUI functions -------- #

def show_welcome(root):
    """Show the welcome 'page' and a Continue button."""
    global current_frame
    #sets up the welcome frame
    if current_frame is not None:
        current_frame.destroy()


    frame = tk.Frame(root)
    current_frame = frame
    frame.pack(fill='both', expand=True)
    #Adding GUI features
    tk.Label(
        frame,
        text="NACA Airfoil Generator",
        font=("Arial", 26)
    ).pack(pady=50)

    tk.Label(
        frame,
        text=("Create and visualize NACA 4-digit airfoils with custom parameters.\n"
              "Click Continue to get started."),
        font=("Arial", 15),
        justify="center"
    ).pack(pady=20)

    tk.Button(
        frame,
        text="Continue",
        font=("Arial", 15),
        command=lambda: show_form(root)
    ).pack(pady=40)

def show_form(root):
    """Show the main form and plotting area."""
    global current_frame, naca_entry, chord_entry, npoints_entry
    global error_var, fig, ax, canvas

    if current_frame is not None:
        current_frame.destroy()

    frame = tk.Frame(root)
    current_frame = frame
    frame.pack(fill='both', expand=True)

    # Inputs
    tk.Label(
        frame,
        text="NACA 4-digit code (e.g., 2412, 0012):",
        font=("Arial", 14)
    ).grid(row=0, column=0, sticky="e", pady=4)

    naca_entry = ttk.Entry(frame, font=("Arial", 14), width=12)
    naca_entry.grid(row=0, column=1, padx=6, pady=4)

    tk.Label(
        frame,
        text="Chord length (e.g., 1):",
        font=("Arial", 14)
    ).grid(row=1, column=0, sticky="e", pady=4)

    chord_entry = ttk.Entry(frame, font=("Arial", 14), width=12)
    chord_entry.grid(row=1, column=1, padx=6, pady=4)

    tk.Label(
        frame,
        text="Number of points (>= 40):",
        font=("Arial", 14)
    ).grid(row=2, column=0, sticky="e", pady=4)

    npoints_entry = ttk.Entry(frame, font=("Arial", 14), width=12)
    npoints_entry.insert(0, "100")
    npoints_entry.grid(row=2, column=1, padx=6, pady=4)

    tk.Button(
        frame,
        text="Generate Airfoil",
        font=("Arial", 14),
        command=plot_airfoil
    ).grid(row=3, column=0, columnspan=2, pady=14)

    # Error label
    error_var = tk.StringVar()
    lbl_error = tk.Label(
        frame,
        textvariable=error_var,
        fg="red",
        font=("Arial", 12)
    )
    lbl_error.grid(row=4, column=0, columnspan=2)

    # Matplotlib figure
    fig, ax = plt.subplots(figsize=(9, 4.8))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, pady=20)

def plot_airfoil():
    """Read entries, validate, compute airfoil, and plot it."""
    global ax, fig, canvas, naca_entry, chord_entry, npoints_entry, error_var

    code = naca_entry.get().strip()
    try:
        chord = float(chord_entry.get())
        n_points = int(npoints_entry.get())
        m_point = int(code[0])
        p_point = int(code[1])
        if len(code) != 4 or not code.isdigit():
            raise ValueError("NACA code must be exactly 4 digits (e.g., 2412, 0012).")
        if (m_point == 0) != (p_point == 0):
            raise ValueError("First two digits must both be 0 (symmetric) or both non-zero (cambered).")
        if chord <= 0:
            raise ValueError("Chord length must be positive.")
        if n_points < 40:
            raise ValueError("Use at least 40 points for a smooth airfoil.")
    except Exception as exc:
        error_var.set(str(exc))
        return

    error_var.set("")

    (x_u, y_u, x_l, y_l,
     x_c, y_c,
     x_max_camber, y_max_camber,
     x_max_thickness, y_max_thickness) = naca4_airfoil(code, chord, n_points)

    ax.clear()
    # Main airfoil features
    ax.plot(x_u, y_u, label="Upper Surface", color='blue')
    ax.plot(x_l, y_l, label="Lower Surface", color='red')
    ax.plot(x_c, y_c, label="Camber Line", color='green', linestyle='--', linewidth=2)
    ax.plot([0, chord], [0, 0], color='gray', linestyle='-', linewidth=1.5, label="Chord Line")

    # Key points
    ax.plot(x_max_camber, y_max_camber, 'go', label="Max Camber")
    ax.plot(x_max_thickness, y_max_thickness, 'mo', label="Max Thickness")

    # Label key points with x-coordinates
    ax.annotate(
        f"x={x_max_camber:.3f}",
        xy=(x_max_camber, y_max_camber),
        xytext=(5, 10),
        textcoords="offset points",
        fontsize=10,
        color="green"
    )
    ax.annotate(
        f"x={x_max_thickness:.3f}",
        xy=(x_max_thickness, y_max_thickness),
        xytext=(5, -15),
        textcoords="offset points",
        fontsize=10,
        color="magenta"
    )

    # Axes & title
    ax.set_title(f"NACA {code} (Chord = {chord})", fontsize=17)
    ax.set_xlabel("x (Chordwise)", fontsize=13)
    ax.set_ylabel("y", fontsize=13)

    # X-axis from 0 to chord with ticks
    n_ticks = 6  # adjust as desired
    xticks = np.linspace(0, chord, n_ticks)
    ax.set_xlim(0, chord)
    ax.set_xticks(xticks)

    ax.axis('equal')
    ax.grid(True, alpha=0.3)

    # Legend/key
    ax.legend(loc='upper right', fontsize=11, framealpha=0.65)

    fig.tight_layout()
    canvas.draw()

def main():
    global current_frame
    current_frame = None

    root = tk.Tk()
    root.title("NACA 4-Digit Airfoil Generator")
    root.geometry("950x700")
    root.resizable(False, False)

    show_welcome(root)
    root.mainloop()

if __name__ == "__main__":
    main()