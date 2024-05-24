""" Settings view window for PEAT. 

    Written by: Travis M. Moore
    Last edited: May 24, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from idlelib.tooltip import Hovertip
from tkinter import ttk
from tkinter import messagebox

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

################
# SettingsView #
################
class SettingsView(tk.Toplevel):
    """ Dialog for setting session parameters. """
    def __init__(self, parent, sessionpars, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        logger.debug("Initializing SettingsView")

        # Assign variables
        self.parent = parent
        self.sessionpars = sessionpars

        # Window settings
        self.withdraw()
        self.resizable(False, False)
        self.title("Settings")
        self.grab_set()


        #################
        # Create Frames #
        #################
        # Shared frame settings
        frame_options = {'padx': 10, 'pady': 10}
        widget_options = {'padx': 5, 'pady': 5}

        # Session info frame
        frm_session = ttk.Labelframe(self, text='Session Information')
        frm_session.grid(row=5, column=5, **frame_options, sticky='nsew')

        # Stimulus options frame
        frm_stimulus = ttk.Labelframe(self, text='Stimulus Options')
        frm_stimulus.grid(row=10, column=5, **frame_options, sticky='nsew')

        # Staircase options frame
        frm_staircase = ttk.Labelframe(self, text='Staircase Options')
        frm_staircase.grid(row=15, column=5, **frame_options, sticky='nsew')

        ################
        # Draw Widgets #
        ################
        # Default amount of time for tool tips to appear
        tt_delay = 1000 # ms

        # SESSION #
        # Subject
        lbl_sub = ttk.Label(frm_session, text="Subject:")
        lbl_sub.grid(row=5, column=5, sticky='e', **widget_options)
        sub_tt = Hovertip(
            anchor_widget=lbl_sub, 
            text="A unique subject identifier.\nCan be alpha, numeric, or both.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_session, width=20, 
            textvariable=self.sessionpars['subject']
            ).grid(row=5, column=10, sticky='w')

        # Condition
        lbl_cond = ttk.Label(frm_session, text="Condition:")
        lbl_cond.grid(row=10, column=5, sticky='e', **widget_options)
        cond_tt = Hovertip(
            anchor_widget=lbl_cond, 
            text="A unique condition name.\nCan be alpha, numeric, or both.\nSeparate words with underscores.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_session, width=20, 
            textvariable=self.sessionpars['condition']
            ).grid(row=10, column=10, sticky='w')

        # Plots
        chk_plots = ttk.Checkbutton(frm_session, text="Display Plots",
            takefocus=0, variable=self.sessionpars['disp_plots'])
        chk_plots.grid(row=15, column=5,  columnspan=20, sticky='w', 
            **widget_options)
        plots_tt = Hovertip(
            anchor_widget=chk_plots,
            text="Display staircase plots after each threshold.",
            hover_delay=tt_delay
        )


        # STIMULUS #
        # Number of channels for stimulus
        lbl_num_chans = ttk.Label(frm_stimulus, text="Channels:")
        lbl_num_chans.grid(row=5, column=5, sticky='e', **widget_options)
        num_chans_tt = Hovertip(
            anchor_widget=lbl_num_chans,
            text="The number of channels for audio playback.\nUpdate channel routing accordingly.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_stimulus, width=20, 
            textvariable=self.sessionpars['num_stim_chans']
            ).grid(row=5, column=10, sticky='w')

        # Duration
        lbl_dur = ttk.Label(frm_stimulus, text="Duration (s):")
        lbl_dur.grid(row=10, column=5, sticky='e', **widget_options)
        dur_tt = Hovertip(
            anchor_widget=lbl_dur,
            text="Duration of the stimulus (per interval) in seconds.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_stimulus, width=20, 
            textvariable=self.sessionpars['duration']
            ).grid(row=10, column=10, sticky='w')

        # Test Frequencies
        lbl_freqs = ttk.Label(frm_stimulus, text="Frequencies (Hz):")
        lbl_freqs.grid(row=15, column=5, sticky='e', **widget_options)
        freqs_tt = Hovertip(
            anchor_widget=lbl_freqs,
            text="Frequencies to test in a given session.\nSeparate multiple frequencies with a comma and space.\nFrequencies will be tested in the order provided.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_stimulus, width=50, 
            textvariable=self.sessionpars['test_freqs']
            ).grid(row=15, column=10, sticky='w', padx=(0,10))


        # STAIRCASE #
        # Starting Level
        lbl_level = ttk.Label(frm_staircase, text="Starting Level (dB):")
        lbl_level.grid(row=5, column=5, sticky='e', **widget_options)
        level_tt = Hovertip(
            anchor_widget=lbl_level,
            text="The starting level for each new threshold search.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_staircase, width=20, 
            textvariable=self.sessionpars['starting_level']
            ).grid(row=5, column=10, sticky='w')

        # Minimum Level
        lbl_min_lvl = ttk.Label(frm_staircase, text="Minimum Level (dB):")
        lbl_min_lvl.grid(row=10, column=5, sticky='e', **widget_options)
        min_lvl_tt = Hovertip(
            anchor_widget=lbl_min_lvl,
            text="The minimum permissible output level.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_staircase, width=20, 
            textvariable=self.sessionpars['min_level']
            ).grid(row=10, column=10, sticky='w')
        
        # Maximum Level
        lbl_max_lvl = ttk.Label(frm_staircase, text="Maximum Level (dB):")
        lbl_max_lvl.grid(row=15, column=5, sticky='e', **widget_options)
        max_lvl_tt = Hovertip(
            anchor_widget=lbl_max_lvl,
            text="The maximum permissible output level.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_staircase, width=20, 
            textvariable=self.sessionpars['max_level']
            ).grid(row=15, column=10, sticky='w')
        
        # Step Sizes
        lbl_steps = ttk.Label(frm_staircase, text="Step Size(s):")
        lbl_steps.grid(row=20, column=5, sticky='e', **widget_options)
        steps_tt = Hovertip(
            anchor_widget=lbl_steps,
            text="The step size(s) used by the staircase to bracket a " + \
                "threshold.\nThe last step size will be repeated until " + \
                "all reversals have been collected.\nSeparate multiple " + \
                "values with a comma and space.",
                hover_delay=tt_delay
        )
        ttk.Entry(frm_staircase, width=20, 
            textvariable=self.sessionpars['step_sizes']
            ).grid(row=20, column=10, sticky='w')

        # Number of Reversals
        lbl_num_revs = ttk.Label(frm_staircase, text="Reversals:")
        lbl_num_revs.grid(row=25, column=5, sticky='e', **widget_options)
        num_revs_tt = Hovertip(
            anchor_widget=lbl_num_revs,
            text="The number of reversals to obtain before stopping the procedure.",
            hover_delay=tt_delay
        )
        ttk.Entry(frm_staircase, width=20, 
            textvariable=self.sessionpars['num_reversals']
            ).grid(row=25, column=10, sticky='w')

        # Rapid Descend
        lbl_descend = ttk.Label(frm_staircase, text="Rapid Descend:")
        lbl_descend.grid(row=30, column=5, sticky='e', **widget_options)
        descend_tt = Hovertip(
            anchor_widget=lbl_descend,
            text="Initial decrease with 1-down rule to reach threshold faster.",
            hover_delay=tt_delay
        )
        vlist = ["Yes", "No"]
        ttk.Combobox(
            frm_staircase, 
            textvariable=self.sessionpars['rapid_descend'], 
            values=vlist,
            state='readonly'
        ).grid(row=30, column=10, sticky='w')

        # Submit button
        btn_submit = ttk.Button(self, text="Submit", command=self._on_submit)
        btn_submit.grid(row=40, column=5, columnspan=2, pady=(0, 10))

        # Center the session dialog window
        self.center_window()

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


    def _check_channels(self):
        """ Ensure the number of channels is less than the number of 
            non-overlapping phi values (see stimulusmodel>
            _get_random_phis).
        """
        logger.debug("Checking the number of channels")
        # Get value from entry box
        chans = self.sessionpars['num_stim_chans'].get()

        # Looks like the tk.IntVar forces to an integer?
        # This doesn't get called, even with a float value.
        # Dangerous because there is no warning. It seems like
        # the previous value is used?
        if not isinstance(chans, int):
            return False
        if chans > 9:
            return False
        return True


    def _check_test_freqs(self):
        """ Ensure only valid test frequencies have been entered. """
        logger.debug("Checking specified test frequencies")
        # List of valid frequencies
        valid_freqs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 
                        200, 250, 315, 400, 500, 630, 750, 800, 1000, 
                        1250, 1500, 1600, 2000, 2500, 3000, 4000, 
                        6000, 6300, 8000, 9000, 10000, 11200, 14000, 
                        16000]
        
        # Get raw frequencies from entry box
        test_freqs = self.sessionpars['test_freqs'].get()

        # Attempt to convert to integers
        try:
            test_freqs = [int(val) for val in test_freqs.split(', ')]
        except ValueError:
            return False
        
        # Test for invalid frequencies
        if not set(test_freqs).issubset(valid_freqs):
            return False
        return True
    

    def _check_step_sizes(self):
        """ Ensure step sizes are integers. """
        logger.debug("Checking specified step sizes")
        steps = self.sessionpars['step_sizes'].get()
        try:
            steps = [int(val) for val in steps.split(', ')]
        except ValueError:
            return False
        return True


    def _check_reversals(self):
        """ Ensure there are enough reversals for step sizes. """
        logger.debug("Checking specified reversals")
        revs = self.sessionpars['num_reversals'].get() 
        steps = int(len(self.sessionpars['step_sizes'].get().split()))

        return revs >= steps


    def _check_levels(self):
        """ Ensure minimum level is less than maximum level. """
        logger.debug("Checking specified levels")
        min_level = self.sessionpars['min_level'].get()
        max_level = self.sessionpars['max_level'].get()

        return max_level > min_level


    def _on_submit(self):
        """ Perform various validation checks.
            Send submit event to controller.
        """
        logger.debug("Submit button pressed")
        # Convert rapid descend response to boolean
        if self.sessionpars['rapid_descend'].get() == "Yes":
            self.sessionpars['rapid_descend_bool'].set(True)
        elif self.sessionpars['rapid_descend'].get() == "No":
            self.sessionpars['rapid_descend_bool'].set(False)

        # Make sure the number of channels is supported by
        #   the number of non-overlapping phis.
        if not self._check_channels():
            messagebox.showerror(
                title="Invalid Channels",
                message="Invalid number of channels!",
                detail="The maximum number of channels is nine."\
                    "\nChannels must be integers."
            )
            return            

        # Check that frequencies are allowable (have RETSPLs)
        if not self._check_test_freqs():
            messagebox.showerror(
                title="Invalid Frequency",
                message="Invalid test frequency found!",
                detail="See Help>README for a list of valid test frequencies."
            )
            return  
        
        # Make sure the number of reversals at least matches
        #   the number of steps
        if not self._check_reversals():
            messagebox.showerror(
                title="Not Enough Reversals",
                message="The number of reversals must at least equal the " + 
                    "number of steps!"
            )
            return
        
        # Make sure max_level > min_level
        if not self._check_levels():
            messagebox.showerror(
                title="Invalid Levels",
                message="The maximum level must exceed the minimum level!"
            )
            return

        # Make sure step sizes are integers
        if not self._check_step_sizes():
            messagebox.showerror(
                title="Invalid Step Size",
                message="Step sizes must be integers!"
            )
            return

        # Send save event to controller
        logger.debug("Sending save event to controller")
        self.parent.event_generate('<<SettingsSubmit>>')
        logger.debug("Destroying SettingsView")
        self.destroy()
