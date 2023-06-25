from tkinter import ttk

from Tooltip import Tooltip


class SearchableCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_searching = False  # Flag to indicate if searching is active
        self._search_var = ""  # Variable to store the search query
        self._original_values = self["values"]  # Store the original set of values
        self.bind('<KeyPress>', self._on_keypress)  # Bind keypress event to _on_keypress method
        self.bind('<KeyRelease>', self._on_keyrelease)  # Bind key release event to _on_keyrelease method
        self.bind('<FocusOut>', self._on_focus_out)  # Bind focus out event to _on_focus_out method
        self.bind('<Button-1>', self._on_mouse_click)  # Bind mouse click event to _on_mouse_click method
        self.tooltip = Tooltip(self, "Double click dropdown and then type to search. "
                                     "Hit ESC to clear the search and start over.")

    # Event handler for mouse click
    def _on_mouse_click(self, event):
        self.tooltip.hide_tooltip()  # Dismiss the tooltip

    # Event handler for focus out
    def _on_focus_out(self, event):
        self.tooltip.hide_tooltip()  # Dismiss the tooltip

    # Event handler for key press
    def _on_keypress(self, event):
        if not self._is_searching:
            self._original_values = self["values"]  # Store the original set of values
        self._is_searching = True  # Set searching flag to True
        self._search_var += event.char.lower()  # Append the pressed key (in lowercase) to the search query
        self._update_values()  # Update the values displayed in the dropdown

    # Event handler for key release
    def _on_keyrelease(self, event):
        if event.keysym == "BackSpace" and self._search_var:
            self._search_var = self._search_var[:-1]  # Remove the last character from the search query
            self._update_values()  # Update the values displayed in the dropdown
        elif event.keysym == "Escape":
            self._reset_search()  # Reset the search query and values to the original ones

    # Update the values displayed in the dropdown based on the search query
    def _update_values(self):
        self["values"] = [value for value in self._original_values if value.lower().startswith(self._search_var)]
        # Set the selected value to the first one in the filtered list, if any
        if self["values"]:
            self.set(self["values"][0])
        else:
            self.set('')  # Clear the selected value

    # Reset the search query and values to the original ones
    def _reset_search(self):
        self._is_searching = False  # Set searching flag to False
        self._search_var = ""  # Clear the search query
        self["values"] = self._original_values  # Restore the original set of values
