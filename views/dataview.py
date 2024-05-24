""" Calculate Thresholds View.
"""

###########
# Imports #
###########
# Standard library
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Add custom filepath
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')

# Custom
from tmpy.functions.helper_funcs import truncate_path
from models import scoringmodel

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

###################
# ThresholdDialog #
###################
class ThresholdDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Assign variables
        self.parent = parent

        # Window settings
        self.withdraw()
        self.resizable(False, False)
        self.title("Calculate Thresholds")
        self.grab_set()

        # Populate frame with widgets
        self.draw_widgets()

        # Center the session dialog window
        self.center_window()


    def draw_widgets(self):
        """ Populate the main view with all widgets. """
        #################
        # Create frames #
        #################      
        # Shared frame settings
        frame_options = {'padx': 10, 'pady': 10}
        widget_options = {'padx': 5, 'pady': 5}

        # Main frame
        frm_main = ttk.Frame(self)
        frm_main.grid(row=5, column=5, sticky='nsew', **frame_options)

        # Options frame
        lfrm_options = ttk.LabelFrame(frm_main, text="Options")
        lfrm_options.grid(row=5, column=5, sticky='nsew')

        # Submit button frame
        frm_submit = ttk.Frame(frm_main)
        frm_submit.grid(row=10, column=5, sticky='nsew')
        frm_submit.columnconfigure(5, weight=1)
        frm_submit.rowconfigure(5, weight=1)

        ################
        # Draw Widgets #
        ################
        # Threshold data directory
        ttk.Label(lfrm_options, text="Threshold Data Directory:"
            ).grid(row=20, column=5, sticky='e', **widget_options)
        # Create textvariable
        self.thresh_data_dir_var = tk.StringVar(
            value='Please select a directory'
        )
        # Threshold data directory browse button
        ttk.Label(lfrm_options, textvariable=self.thresh_data_dir_var, 
            borderwidth=2, relief="solid", width=30
            ).grid(row=20, column=10, sticky='w', padx=(0,10))
        ttk.Button(lfrm_options, text="Browse", 
                   command=self._create_scoring_class).grid(row=25, 
                    column=10, sticky='w', pady=(0, 10))
        
        # Number of reversals entry box
        self.num_reversals_var = tk.IntVar(value=0)
        ttk.Label(lfrm_options, text="Number of Reversals for Averaging:"
            ).grid(row=5, column=5, sticky='e', **widget_options)
        ttk.Entry(lfrm_options, width=10, 
            textvariable=self.num_reversals_var
            ).grid(row=5, column=10, sticky='w')

        # Submit button
        ttk.Button(frm_submit,
            text="Submit",
            command=self._on_submit).grid(
                row=5, column=5, pady=(10,0))


    #############
    # Functions #
    #############
    def center_window(self):
        """ Center the TopLevel window over the root window. """
        # Get updated window size (after drawing widgets)
        self.update_idletasks()

        # Calculate the x and y coordinates to center the window
        x = self.parent.winfo_x() \
            + (self.parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = self.parent.winfo_y() \
            + (self.parent.winfo_height() - self.winfo_reqheight()) // 2

        # Set the window position
        self.geometry("+%d+%d" % (x, y))

        # Display window
        self.deiconify()


    def _create_scoring_class(self):
        """ Instantiate Scoring Model. """
        # Instantiate ScoringModel object
        self.s = scoringmodel.ScoringModel()

        # Retrieve and truncate threshold data directory path
        short_thresh_data_path = truncate_path(
            self.s.directory,
            length=30
        )
        self.thresh_data_dir_var.set(value=short_thresh_data_path)


    def _on_submit(self):
        """ Calculate thresholds using scoringmodel. """
        try:
            self.s.score(self.num_reversals_var.get())
        except AttributeError:
            msg = "You must provide a valid data directory!"
            messagebox.showerror(
                title="Missing Directory",
                message=msg,
            )
            return
        except ValueError as e:
            messagebox.showerror(
                title="Invalid Quantity",
                message=e
            )
            return

        self.destroy()


if __name__ == '__main__':
    pass
