""" P.sychophysical E.stimation of A.uditory T.hresholds (PEAT)
    
    Threshold estimation app for SoundGear NRR measurements. 
    For use in the sound field, PEAT presents warble tones (FM)
    to a given number of speakers. RETSPLs have been applied to
    equal loudness. Starting phase and sound field summation of
    the warble tones are accounted for. 

    PEAT uses a 2IAFC task with a 1-up 2-down rule, tracking at 
    the 70.7% correct level (Levitt, 1971). 
    
    Calibrate using a mono 1 kHz warble tone scaled to -40 dB. 

    Written by: Travis M. Moore
    Created: January 4, 2024
"""

###########
# Imports #
###########
# Standard library
import datetime
import json
import logging.config
import logging.handlers
import os
import sys
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk
from tkinter import messagebox

# Third party
import markdown

# Add custom filepath
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')

# Custom Modules
import app_assets
import menus
import models
import setup
import tmpy
import views
from tmpy import tkgui

##########
# logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

###############
# Application #
###############
class Application(tk.Tk):
    """ Application root window. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #############
        # Constants #
        #############
        self.NAME = 'P.E.A.T.'
        self.VERSION = '2.0.1'
        self.EDITED = 'May 24, 2024'

        # Create menu settings dictionary
        self._app_info = {
            'name': self.NAME,
            'version': self.VERSION,
            'last_edited': self.EDITED
        }

        # Sampling rate (Hz)
        self.FS = 48000

        # Intervals
        self.INTERVALS = [1, 2]

        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Setup main window
        self.withdraw() # Hide window during setup
        self.resizable(False, False)
        self.title(self.NAME)
        self.taskbar_icon = tk.PhotoImage(
            file=tkgui.shared_assets.images.LOGO_FULL_PNG
            )
        self.iconphoto(True, self.taskbar_icon)

        # Assign special quit function on window close
        self.protocol('WM_DELETE_WINDOW', self._quit)

        # First trial flag
        self._first_run_flag = True

        # Trial number tracker
        self.trial = 0

        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Load current settings from file
        # or load defaults if file does not exist yet
        self.settings_model = tkgui.models.SettingsModel(
            parent=self,
            settings_vars=setup.settings_vars.fields,
            app_name=self.NAME
            )
        self._load_settings()

        # Set up custom logger as soon as config dir is created
        # (i.e., after settings model has been initialized)
        config = tmpy.functions.logging_funcs.setup_logging(self.NAME)
        logging.config.dictConfig(config)
        logger.debug("Started custom logger")
        logger.debug("Initializing Application")

        # Load calibration model
        #self.calmodel = calmodel.CalModel(self.settings)

        # Load stimulus model
        self.stim_model = models.StimulusModel(self.settings)

        # Load main view
        self.main_frame = views.MainView(self)
        self.main_frame.grid(row=5, column=5)

        # Add progress bar after loading mainview
        self._progress_bar()

        # Load menus
        self.menu = menus.MainMenu(self, self._app_info)
        self.config(menu=self.menu)

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileSettings>>': lambda _: self.show_settings_view(),
            '<<FileStart>>': lambda _: self.start_new_run(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsAudioSettings>>': lambda _: self._show_audio_dialog(),
            '<<ToolsCalibration>>': lambda _: self._show_calibration_dialog(),

            # Data menu
            '<<DataCalculateThresholds>>': lambda _: self.show_scoring_dialog(),

            # Help menu
            '<<HelpREADME>>': lambda _: self._show_help(),
            '<<HelpChangelog>>': lambda _: self._show_changelog(),

            # Session dialog commands
            '<<SettingsSubmit>>': lambda _: self._save_settings(),

            # Calibration dialog commands
            '<<CalPlay>>': lambda _: self.play_calibration_file(),
            '<<CalStop>>': lambda _: self.stop_audio(),
            '<<CalibrationSubmit>>': lambda _: self._calc_offset(),

            # Audio dialog commands
            '<<AudioDialogSubmit>>': lambda _: self._save_settings(),

            # Main View commands
            '<<MainOne>>': lambda _: self._on_1(),
            '<<MainTwo>>': lambda _: self._on_2(),
            '<<MainSubmit>>': lambda _: self._on_submit(),
        }

        # Bind callbacks to sequences
        logger.debug("Binding callbacks to controller")
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        ###################
        # Version Control #
        ###################
        # Check for updates
        if self.settings['check_for_updates'].get() == 'yes':
            _filepath = self.settings['version_lib_path'].get()
            u = tkgui.models.VersionModel(_filepath, self.NAME, self.VERSION)
            if u.status == 'mandatory':
                logger.critical("This version: %s", self.VERSION)
                logger.critical("Mandatory update version: %s", u.new_version)
                messagebox.showerror(
                    title="New Version Available",
                    message="A mandatory update is available. Please install " +
                        f"version {u.new_version} to continue.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
                logger.critical("Application failed to initialize")
                self.destroy()
                return
            elif u.status == 'optional':
                messagebox.showwarning(
                    title="New Version Available",
                    message="An update is available.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
            elif u.status == 'current':
                pass
            elif u.status == 'app_not_found':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="Cannot retrieve version number!",
                    detail=f"'{self.NAME}' does not exist in the version library."
                 )
            elif u.status == 'library_inaccessible':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="The version library is unreachable!",
                    detail="Please check that you have access to Starfile."
                )

        # Temporarily disable Help menu until documents are written
        #self.menu.help_menu.entryconfig('README...', state='disabled')

        # Center main window
        self.center_window()

        # Initialization successful
        logger.info('Application initialized successfully')     

    #####################
    # General Functions #
    #####################
    def center_window(self):
        """ Center the root window. """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()


    def _progress_bar(self):
        """ Create and position task progress bar. The progress 
            bar updates based on the number of frequencies 
            remaining to test in a given session.
        """
        self.progress_bar = ttk.Progressbar(
            master=self,
            orient='horizontal',
            mode='determinate',
            length=self.winfo_width()
        )
        self.progress_bar.grid(row=10, column=5, columnspan=40, sticky='nsew')


    def bind_keys(self):
        """ Bind keys to main_frame response functions. """
        self.bind('1', lambda event: self.main_frame.on_1())
        self.bind('2', lambda event: self.main_frame.on_2())


    def unbind_keys(self):
        """ Unbind keys to main_frame response functions. """
        self.unbind('1')
        self.unbind('2')


    def _quit(self):
        """ Exit the application. """
        self.destroy()

    ###################
    # File Menu Funcs #
    ###################
    def start_new_run(self):
        """ 1. Disable "Start Task" from file menu.
            2. Get number of frequencies to test (for progress bar).
            3. Create staircase.
            4. Present first trial.
            Repeat steps 2 - 4 for each new run (i.e., frequency).
        """
        logger.debug("Starting new run")
        # Check for first run
        if self._first_run_flag:
            # Disable "Start Task" from File menu
            self.menu.file_menu.entryconfig('Start Task', state='disabled')

            # Get frequencies
            # Query AFTER the task starts to capture updates to sessioninfo
            self.freqs, self.NUM_FREQS = self.stim_model.get_test_freqs()

            # Set first run flag to False
            self._first_run_flag = False
            
        # Get next frequency or end
        try:
            self.current_freq = self.freqs.pop(0)
            logger.debug("Testing %d Hz", self.current_freq)
            messagebox.showinfo(
                title="Ready",
                message="When you are ready, close this window to continue."
            )
        except IndexError:
            logger.debug("Session ended successfully by start_new_run")
            messagebox.showinfo(
                title="Task Complete",
                message="You have finished this task. Please let the "
                    "investigator know."
            )
            self._quit()
            return

        # Generate stimulus
        self.stim = self.stim_model.create_stimulus(
            dur=self.settings['duration'].get(),
            fs=self.FS,
            fc=self.current_freq,
            mod_rate=5,
            mod_depth=5
        )

        # Update progress bar
        if self.progress_bar['value'] < 100:
            self.progress_bar['value'] += 100/self.NUM_FREQS

        # Convert step_sizes to list of ints
        steps = self.settings['step_sizes'].get()
        steps = [int(val) for val in steps.split(', ')]

        # Create staircase
        self.staircase = tmpy.handlers.StaircaseHandler(
            start_val=self.settings['starting_level'].get(),
            step_sizes=steps,
            nUp=1,
            nDown=2,
            nTrials=0,
            nReversals=self.settings['num_reversals'].get(),
            rapid_descend=self.settings['rapid_descend_bool'].get(),
            min_val=self.settings['min_level'].get(),
            max_val=self.settings['max_level'].get()
        )

        # Start first trial
        self._new_trial()


    def _new_trial(self):
        """ Present a 2IAFC trial. """
        logger.debug("Presenting next trial")
        # Print message to console
        logger.debug("Trial %d: %d Hz", self.trial, self.current_freq)

        # Assign stimulus to an interval
        self.stim_interval = self.stim_model.assign_stimulus_interval(
            intervals=self.INTERVALS
        )
        logger.debug("Stimulus is in interval %d", self.stim_interval)

        # Calculate the RETSPL-adjusted, single channel level
        final_single_chan_level = self.stim_model.calc_presentation_lvl(
            stair_lvl=self.staircase.current_level,
            freq = self.current_freq
        )

        # Apply offset to desired dB level
        # (Also update settings)
        self._calc_level(final_single_chan_level)

        # # Print values to console
        # print(f"Staircase level: {self.staircase.current_level}")
        # print(f"Unscaled final single chan level: {final_single_chan_level}")
        # print(f"Scaled final single chan level: " +
        #       f"{self.settings['adjusted_level_dB'].get()}")

        # Pause
        time.sleep(0.5)
        
        # Interval 1
        self.main_frame.interval_1_colors()
        if self.stim_interval == 1:
            self.present_audio(
                audio=self.stim,
                pres_level=self.settings['adjusted_level_dB'].get(),
                sampling_rate=self.FS
            )
        time.sleep(self.settings['duration'].get() + 0.15)

        # ISI
        self.main_frame.clear_interval_colors()
        time.sleep(0.5)

        # Interval 2
        self.main_frame.interval_2_colors()
        if self.stim_interval == 2:
            self.present_audio(
                audio=self.stim,
                pres_level=self.settings['adjusted_level_dB'].get(),
                sampling_rate=self.FS
            )
        time.sleep(self.settings['duration'].get() + 0.15)

        # End
        self.main_frame.clear_interval_colors()

        # Wait to bind keys until after trial has finished
        #   to avoid multiple submissions during the presentation
        self.after(10, lambda: self.bind_keys())

    ######################
    # MainView Functions #
    ######################
    def _on_1(self):
        """ Set response value to 1 (yes). """
        logger.debug("Setting response to 1 (yes)")
        self.response = 1


    def _on_2(self):
        """ Set response value to 0 (no). """
        logger.debug("Setting response to 0 (no)")
        self.response = 2


    def _on_submit(self):
        """ Assign response value and save to file.
            Update key bindings.
            Present next trial.
        """
        logger.debug("Submit button pressed")
        # Assign response value
        if (self.response == 1) and (self.stim_interval == 1):
            self.staircase.add_response(1)
        elif (self.response == 2) and (self.stim_interval == 2):
            self.staircase.add_response(1)
        else: 
            self.staircase.add_response(-1)

        # Save the trial data
        self._save_trial_data()

        # Update trial counter
        self.trial += 1

        # Unbind keys for the start of the next trial
        self.unbind_keys()

        # Check for end of staircase
        if not self.staircase.status:
            logger.debug("End of staircase!")
            if self.settings['disp_plots'].get() == 1:
                self.staircase.plot_data()
            # Call start_new_run to get next frequency
            self.start_new_run()
        else:
            self._new_trial()


    def _save_trial_data(self):
        """ Select data to save and write to CSV. """
        # Get tk variable values
        converted = dict()
        for key in self.settings:
            converted[key] = self.settings[key].get()

        # Add most recent datapoint object attributes to dict
        converted.update(self.staircase.dw.datapoints[-1].__dict__)

        # Add 1 to trial number
        converted['trial'] = self.trial + 1

        # Add current test frequency to dict
        converted['test_freq'] = self.current_freq

        # Define selected items for writing to file
        save_list = [
            'trial', 'subject', 'condition', 'min_level', 'max_level', 
            'duration', 'step_sizes', 'num_reversals', 'rapid_descend', 
            'slm_reading', 'cal_level_dB', 'slm_offset', 'adjusted_level_dB',
             'desired_level_dB', 'test_freq', 'response', 'reversal'
        ]

        # Create new dict with desired items
        try:
            data = dict((k, converted[k]) for k in save_list)
        except KeyError as e:
            logger.error("Unexpected variable when attempting " +
                  "to save: %s", e)
            messagebox.showerror(
                title="Undefined Variable",
                message="Data not saved!",
                detail=f'{e} is undefined.'
            )
            self.destroy()
            return

        # Write data to file
        logger.debug("Attempting to save record")
        try:
            self.csvmodel.save_record(data)
        except PermissionError as e:
            print(e)
            messagebox.showerror(
                title="Access Denied",
                message="Data not saved! Cannot write to file!",
                detail=e
            )
            self.destroy()
            return

    ##########################
    # SettingsView Functions #
    ##########################
    def show_settings_view(self):
        """ Show session parameter dialog. """
        logger.debug("Calling settings view")
        self.update_idletasks()
        views.SettingsView(self, self.settings)


    def _load_settings(self):
        """ Load parameters into self.settings dict. """
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create runtime dict from session model fields
        self.settings = dict()
        for key, data in self.settings_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])
        logger.debug("Loaded settings model fields into " +
            "running settings dict")


    def _save_settings(self, *_):
        """ Save current runtime parameters to file. """
        logger.debug("Calling settings model set and save funcs")
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
            self.settings_model.save()


    ########################
    # Tools Menu Functions #
    ########################
    def _show_audio_dialog(self):
        """ Show audio settings dialog. """
        print("\ncontroller: Calling audio dialog")
        audioview.AudioDialog(self, self.settings)

    def _show_calibration_dialog(self):
        """ Display the calibration dialog window. """
        print("\ncontroller: Calling calibration dialog")
        calibrationview.CalibrationDialog(self, self.settings)


    #######################
    # Data Menu Functions #
    #######################
    def show_scoring_dialog(self):
        """ Display the threshold calculation dialog. """
        logger.debug("Calling threshold window")
        views.ThresholdDialog(self)


    ################################
    # Calibration Dialog Functions #
    ################################
    def play_calibration_file(self):
        """ Load calibration file and present. """
        # Get calibration file
        try:
            self.calmodel.get_cal_file()
        except AttributeError:
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find internal calibration file!",
                detail="Please use a custom calibration file."
            )
        # Present calibration signal
        self.present_audio(
            audio=Path(self.calmodel.cal_file), 
            pres_level=self.settings['cal_level_dB'].get()
        )


    def _calc_offset(self):
        """ Calculate offset based on SLM reading. """
        # Calculate new presentation level
        self.calmodel.calc_offset()
        # Save level - this must be called here!
        self._save_settings()


    def _calc_level(self, desired_spl):
        """ Calculate new dB FS level using slm_offset. """
        # Calculate new presentation level
        self.calmodel.calc_level(desired_spl)
        # Save level - this must be called here!
        self._save_settings()


    #######################
    # Help Menu Functions #
    #######################
    def _show_help(self):
        """ Create html help file and display in default browser. """
        logger.debug("Calling README file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.README.README_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.README.README_HTML, 'w') as f:
            f.write(html)

        # Open README in default web browser
        webbrowser.open(app_assets.README.README_HTML)


    def _show_changelog(self):
        """ Create html CHANGELOG file and display in default browser. """
        logger.debug("Calling CHANGELOG file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.CHANGELOG.CHANGELOG_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.CHANGELOG.CHANGELOG_HTML, 'w') as f:
            f.write(html)

        # Open CHANGELOG in default web browser
        webbrowser.open(app_assets.CHANGELOG.CHANGELOG_HTML)

    ###################
    # Audio Functions #
    ###################
    def _create_audio_object(self, audio, **kwargs):
        # Create audio object
        try:
            self.a = tmpy.audio_handlers.AudioPlayer(
                audio=audio,
                **kwargs
            )
        except FileNotFoundError:
            logger.exception("Cannot find audio file!")
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find the audio file!",
                detail="Go to File>Session to specify a valid audio path."
            )
            self.show_settings_view()
            return
        except tmpy.audio_handlers.InvalidAudioType:
            raise
        except tmpy.audio_handlers.MissingSamplingRate:
            raise


    def _format_routing(self, routing):
        """ Convert space-separated string to list of ints
            for speaker routing.
        """
        logger.debug("Formatting channel routing string as list")
        routing = routing.split()
        routing = [int(x) for x in routing]
        return routing
    

    def _play(self, pres_level):
        """ Format channel routing, present audio and catch exceptions. """
        # Get routing either from a trial handler or settings
        try:
            routing=[self.th.trial_info['speaker']]
        except AttributeError:
            routing = tmpy.functions.helper_funcs.string_to_list(
                self.settings['channel_routing'].get(), 'int')
            
        # Attempt to present audio
        try:
            self.a.play(
                level=pres_level,
                device_id=self.settings['audio_device'].get(),
                routing=routing
            )
        except tmpy.audio_handlers.InvalidAudioDevice as e:
            logger.error("Invalid audio device: %s", e)
            messagebox.showerror(
                title="Invalid Device",
                message="Invalid audio device! Go to Tools>Audio Settings " +
                    "to select a valid audio device.",
                detail = e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.InvalidRouting as e:
            logger.error("Invalid routing: %s", e)
            messagebox.showerror(
                title="Invalid Routing",
                message="Speaker routing must correspond with the " +
                    "number of channels in the audio file! Go to " +
                    "Tools>Audio Settings to update the routing.",
                detail=e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.Clipping:
            logger.error("Clipping has occurred - aborting!")
            messagebox.showerror(
                title="Clipping",
                message="The level is too high and caused clipping.",
                detail="The waveform will be plotted when this message is " +
                    "closed for visual inspection."
            )
            self.a.plot_waveform("Clipped Waveform")


    def present_audio(self, audio, pres_level, **kwargs):
        # Load audio
        try:
            self._create_audio_object(audio, **kwargs)
        except tmpy.audio_handlers.InvalidAudioType as e:
            logger.error("Invalid audio format: %s", e)
            messagebox.showerror(
                title="Invalid Audio Type",
                message="The audio type is invalid!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return
        except tmpy.audio_handlers.MissingSamplingRate as e:
            logger.error("Missing sampling rate: %s", e)
            messagebox.showerror(
                title="Missing Sampling Rate",
                message="No sampling rate was provided!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return

        # Play audio
        self._play(pres_level)


    def stop_audio(self):
        """ Stop audio playback. """
        logger.debug("User stopped audio playback")
        try:
            self.a.stop()
        except AttributeError:
            logger.debug("Stop called, but there is no audio object!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
