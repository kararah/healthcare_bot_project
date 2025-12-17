import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from mvp_engine import HealthcareEngine
import re
from typing import Optional

# ----------------------------------------
# CONSTANTS
# ----------------------------------------
PRIMARY_COLOR = "#2196F3"
SUCCESS_COLOR = "#4CAF50"
WARNING_COLOR = "#FF9800"
DANGER_COLOR = "#F44336"
BG_COLOR = "#F5F5F5"
TEXT_COLOR = "#333333"

EMERGENCY_TEXT = """🚨 EMERGENCY: If you're experiencing chest pain, difficulty breathing, 
severe bleeding, loss of consciousness, or other life-threatening symptoms, 
call emergency services immediately (911 in US) or go to the nearest ER."""

EXAMPLE_SYMPTOMS = "e.g., headache, fever, cough, fatigue"

# ----------------------------------------
# MAIN APPLICATION CLASS
# ----------------------------------------
class HealthcareChatbot:
    def __init__(self, root):
        self.root = root
        self.engine = HealthcareEngine()
        self.history = []
        self.current_mood = None
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Healthcare Assistant Chatbot")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)
        
    def create_widgets(self):
        """Create all UI components"""
        # Header Frame
        self.create_header()
        
        # Emergency Notice
        self.create_emergency_notice()
        
        # Main Content Frame
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Mood Section
        self.create_mood_section()
        
        # Symptoms Section
        self.create_symptoms_section()
        
        # Action Buttons
        self.create_action_buttons()
        
        # Output Section
        self.create_output_section()
        
        # History Section
        self.create_history_section()
        
    def create_header(self):
        """Create header with title and disclaimer"""
        header_frame = tk.Frame(self.root, bg=PRIMARY_COLOR)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="🏥 Healthcare Assistant Chatbot",
            font=("Arial", 20, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack()
        
        disclaimer = tk.Label(
            self.root,
            text="⚠️ DISCLAIMER: This is NOT a medical diagnosis tool. Always consult a qualified healthcare professional.",
            font=("Arial", 9, "bold"),
            fg=DANGER_COLOR,
            bg=BG_COLOR,
            wraplength=650,
            pady=5
        )
        disclaimer.pack()
        
    def create_emergency_notice(self):
        """Create emergency notice banner"""
        emergency_frame = tk.Frame(self.root, bg="#FFEBEE", relief=tk.SOLID, borderwidth=1)
        emergency_frame.pack(fill=tk.X, padx=20, pady=5)
        
        emergency_label = tk.Label(
            emergency_frame,
            text=EMERGENCY_TEXT,
            font=("Arial", 8),
            fg=DANGER_COLOR,
            bg="#FFEBEE",
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=8
        )
        emergency_label.pack()
        
    def create_mood_section(self):
        """Create mood input section"""
        mood_frame = tk.LabelFrame(
            self.main_frame,
            text="Step 1: How are you feeling today?",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=10,
            pady=10
        )
        mood_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mood_entry = tk.Entry(
            mood_frame,
            width=50,
            font=("Arial", 11)
        )
        self.mood_entry.pack(pady=5)
        self.mood_entry.insert(0, "e.g., tired, anxious, unwell")
        self.mood_entry.config(fg="gray")
        
        # Placeholder behavior
        self.mood_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.mood_entry, "e.g., tired, anxious, unwell"))
        self.mood_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.mood_entry, "e.g., tired, anxious, unwell"))
        
    def create_symptoms_section(self):
        """Create symptoms input section"""
        symptoms_frame = tk.LabelFrame(
            self.main_frame,
            text="Step 2: Enter your symptoms (comma-separated)",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=10,
            pady=10
        )
        symptoms_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.symptom_entry = tk.Entry(
            symptoms_frame,
            width=50,
            font=("Arial", 11)
        )
        self.symptom_entry.pack(pady=5)
        self.symptom_entry.insert(0, EXAMPLE_SYMPTOMS)
        self.symptom_entry.config(fg="gray")
        
        # Placeholder behavior
        self.symptom_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.symptom_entry, EXAMPLE_SYMPTOMS))
        self.symptom_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.symptom_entry, EXAMPLE_SYMPTOMS))
        
        # Bind Enter key to diagnose
        self.symptom_entry.bind("<Return>", lambda e: self.get_diagnosis())
        
        # Character counter
        self.char_count_label = tk.Label(
            symptoms_frame,
            text="0/200 characters",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg="gray"
        )
        self.char_count_label.pack(anchor=tk.E)
        self.symptom_entry.bind("<KeyRelease>", self.update_char_count)
        
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        button_frame.pack(pady=10)
        
        self.diagnose_btn = tk.Button(
            button_frame,
            text="🔍 Get Diagnosis",
            command=self.get_diagnosis,
            font=("Arial", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.diagnose_btn.grid(row=0, column=0, padx=5)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 Reset",
            command=self.reset_form,
            font=("Arial", 12),
            bg=WARNING_COLOR,
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.reset_btn.grid(row=0, column=1, padx=5)
        
        # Loading label (hidden initially)
        self.loading_label = tk.Label(
            button_frame,
            text="⏳ Analyzing...",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        self.loading_label.grid(row=1, column=0, columnspan=2, pady=5)
        self.loading_label.grid_remove()
        
    def create_output_section(self):
        """Create output display section"""
        output_frame = tk.LabelFrame(
            self.main_frame,
            text="Diagnosis Results",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=10,
            pady=10
        )
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.output_box = scrolledtext.ScrolledText(
            output_frame,
            width=70,
            height=15,
            font=("Arial", 10),
            state='disabled',
            wrap=tk.WORD,
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.output_box.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.output_box.tag_config("title", font=("Arial", 12, "bold"), foreground=PRIMARY_COLOR)
        self.output_box.tag_config("section", font=("Arial", 10, "bold"), foreground=TEXT_COLOR)
        self.output_box.tag_config("warning", foreground=DANGER_COLOR, font=("Arial", 9, "italic"))
        
    def create_history_section(self):
        """Create search history section"""
        history_frame = tk.LabelFrame(
            self.main_frame,
            text="Recent Searches",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=5,
            pady=5
        )
        history_frame.pack(fill=tk.X)
        
        self.history_label = tk.Label(
            history_frame,
            text="No searches yet",
            font=("Arial", 9),
            bg=BG_COLOR,
            fg="gray",
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.history_label.pack(fill=tk.X)
        
    def clear_placeholder(self, entry, placeholder_text):
        """Clear placeholder text on focus"""
        if entry.get() == placeholder_text and entry.cget('fg') == 'gray':
            entry.delete(0, tk.END)
            entry.config(fg=TEXT_COLOR)
            
    def restore_placeholder(self, entry, placeholder_text):
        """Restore placeholder if entry is empty"""
        if entry.get().strip() == "":
            entry.insert(0, placeholder_text)
            entry.config(fg="gray")
            
    def update_char_count(self, event=None):
        """Update character count label"""
        text = self.symptom_entry.get()
        if text == EXAMPLE_SYMPTOMS:
            count = 0
        else:
            count = len(text)
        
        color = DANGER_COLOR if count > 200 else "gray"
        self.char_count_label.config(text=f"{count}/200 characters", fg=color)
        
    def validate_input(self, text: str, max_length: int = 200) -> bool:
        """Validate user input"""
        if not text or text.strip() == "":
            return False
        if len(text) > max_length:
            messagebox.showwarning(
                "Input Too Long",
                f"Please limit your input to {max_length} characters."
            )
            return False
        # Check for suspicious patterns
        if re.search(r'[<>{}[\]\\]', text):
            messagebox.showwarning(
                "Invalid Characters",
                "Please remove special characters like <, >, {, }, [, ], \\"
            )
            return False
        return True
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep commas and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9,.\s-]', '', text)
        return text.strip()
        
    def get_diagnosis(self):
        """Process diagnosis request"""
        # Get mood
        mood = self.mood_entry.get()
        if mood != "e.g., tired, anxious, unwell" and self.mood_entry.cget('fg') != 'gray':
            self.current_mood = self.sanitize_input(mood)
        
        # Get symptoms
        symptoms = self.symptom_entry.get()
        
        # Check if placeholder
        if symptoms == EXAMPLE_SYMPTOMS or self.symptom_entry.cget('fg') == 'gray':
            messagebox.showwarning(
                "Input Required",
                "Please enter your symptoms before getting a diagnosis."
            )
            self.symptom_entry.focus()
            return
            
        # Validate
        if not self.validate_input(symptoms):
            return
            
        # Sanitize
        symptoms = self.sanitize_input(symptoms)
        
        if not symptoms:
            messagebox.showwarning(
                "Input Required",
                "Please enter at least one symptom."
            )
            return
        
        # Show loading
        self.show_loading(True)
        self.root.update()
        
        try:
            # Get prediction from engine
            result = self.engine.predict(symptoms)
            
            # Display results
            self.display_results(result, symptoms)
            
            # Update history
            self.update_history(symptoms)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while processing your request:\n{str(e)}\n\nPlease try again or contact support."
            )
        finally:
            self.show_loading(False)
            
    def show_loading(self, show: bool):
        """Show or hide loading indicator"""
        if show:
            self.diagnose_btn.config(state='disabled')
            self.loading_label.grid()
        else:
            self.diagnose_btn.config(state='normal')
            self.loading_label.grid_remove()
            
    def display_results(self, result: dict, symptoms: str):
        """Display diagnosis results"""
        self.output_box.config(state='normal')
        self.output_box.delete(1.0, tk.END)
        
        # Mood acknowledgment
        if self.current_mood:
            self.output_box.insert(tk.END, f"💭 You're feeling: {self.current_mood}\n")
            self.output_box.insert(tk.END, "I hope this information helps you feel better.\n\n")
        
        # Main diagnosis
        self.output_box.insert(tk.END, "🩺 DIAGNOSIS RESULTS\n", "title")
        self.output_box.insert(tk.END, "=" * 50 + "\n\n")
        
        self.output_box.insert(tk.END, f"Most Likely Condition: {result['disease']}\n", "section")
        
        confidence = result['confidence'] * 100
        confidence_color = "green" if confidence > 70 else "orange" if confidence > 40 else "red"
        self.output_box.insert(tk.END, f"Confidence Score: {confidence:.1f}%\n\n")
        
        # Matched symptoms
        self.output_box.insert(tk.END, "✔ Symptoms You Have:\n", "section")
        if result["matched"]:
            for m in result["matched"]:
                self.output_box.insert(tk.END, f"  • {m}\n")
        else:
            self.output_box.insert(tk.END, "  (No direct matches found)\n")
        
        self.output_box.insert(tk.END, "\n")
        
        # Missing symptoms
        if result["missing"]:
            self.output_box.insert(tk.END, "❗ Other Common Symptoms for This Condition:\n", "section")
            for m in result["missing"][:5]:  # Show only first 5
                self.output_box.insert(tk.END, f"  • {m}\n")
            self.output_box.insert(tk.END, "\n")
        
        # Description
        self.output_box.insert(tk.END, "📘 About This Condition:\n", "section")
        self.output_box.insert(tk.END, f"{result['description']}\n\n")
        
        # Precautions
        self.output_box.insert(tk.END, "🛡 Recommended Precautions:\n", "section")
        for i, p in enumerate(result["precautions"], 1):
            self.output_box.insert(tk.END, f"  {i}. {p}\n")
        
        # Final warning
        self.output_box.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.output_box.insert(tk.END, "⚠️ IMPORTANT: This is NOT a medical diagnosis.\n", "warning")
        self.output_box.insert(tk.END, "Please consult a qualified healthcare professional for proper diagnosis and treatment.\n", "warning")
        
        self.output_box.config(state='disabled')
        
    def update_history(self, symptoms: str):
        """Update search history"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        self.history.append(f"[{timestamp}] {symptoms[:50]}...")
        
        # Keep only last 3
        if len(self.history) > 3:
            self.history.pop(0)
            
        history_text = "\n".join(self.history)
        self.history_label.config(text=history_text, fg=TEXT_COLOR)
        
    def reset_form(self):
        """Reset the form"""
        self.mood_entry.delete(0, tk.END)
        self.mood_entry.insert(0, "e.g., tired, anxious, unwell")
        self.mood_entry.config(fg="gray")
        
        self.symptom_entry.delete(0, tk.END)
        self.symptom_entry.insert(0, EXAMPLE_SYMPTOMS)
        self.symptom_entry.config(fg="gray")
        
        self.output_box.config(state='normal')
        self.output_box.delete(1.0, tk.END)
        self.output_box.config(state='disabled')
        
        self.current_mood = None
        self.update_char_count()
        
        self.mood_entry.focus()

# ----------------------------------------
# RUN APPLICATION
# ----------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HealthcareChatbot(root)
    root.mainloop()