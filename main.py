from kivy import require
# Kivy version used in this project
require("2.2.1")

from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import FadeTransition
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

import sqlite3
from ast import literal_eval  # str(dict) to dict
import secrets


########################################################################################################################
###################################################   SCREENS   ########################################################
########################################################################################################################
class ToDoListScreen(MDScreen):
    def on_enter(self, *args):
        """
        What it will do when the moment it enters the screen
        """
        Clock.schedule_once(self.generate_list)
        Clock.schedule_once(lambda dt: app.change_statusbar_color_to())
        Clock.schedule_once(lambda dt: app.change_navbar_color_to())

    # ------------------------------------------------------------------------------------------------------------------  
    def mymenu_config(self):
        self.ids.my_menu.ids.plus_icon_button.bind(on_release=self.create_new_item)
        self.ids.my_menu.ids.search_text_input.bind(text=self.search_for_item)
        self.ids.title.bind(text=self.save_user_data)

    # ------------------------------------------------------------------------------------------------------------------  
    def save_user_data(self, *args):
        # Create list of all
        # all = []
        # for i in app.user_data["app_info"]:
        #     all.append(i["Title"])
        all_id = [i["Id"] for i in app.user_data["app_info"]]
        all_title = [i["Id"] for i in app.user_data["app_info"]]
        all_widgets = [i.title for i in app.original_order]

        # Remove bugs
        for i, child in enumerate(app.user_data["app_info"]):
            if child["Id"] not in all_id and child["Title"] not in all_widgets:
                app.user_data["app_info"].pop(i)

        # Add new item if not added before
        for i, child in enumerate(app.original_order):
            if len(child.title) > 0:
                # Add to list
                if child.id not in all_id and child.title not in all_title:
                    app.user_data["app_info"].append({
                        "Id": child.id,
                        "Title": child.title,
                        "Checked": child.ids.checkbox_icon.active
                    })
                # Update in list
                else:
                    for i2, child2 in enumerate(app.user_data["app_info"]):
                        if child2["Id"] == child.id:
                            app.user_data["app_info"][i2] = {
                                "Id": child.id,
                                "Title": child.title,
                                "Checked": child.ids.checkbox_icon.active
                            }
        # Save title
        app.user_data["name_of_todo"] = self.ids.title.text
            
        # Update database 
        app.update_db_file()
        print(app.user_data)

    # ------------------------------------------------------------------------------------------------------------------  
    def generate_list(self, *args):
        """
        Generate list of items
        """
        if app.user_data:
            for child in reversed(app.user_data["app_info"]):
                item = ListItem(
                    title=str(child["Title"]),
                    id=str(child["Id"])
                )
                item.ids.checkbox_icon.active = child["Checked"]
                item.ids.name_text_input.bind(text=self.save_list)
                item.ids.checkbox_icon.bind(active=self.update_check)
                self.ids.my_list.add_widget(item)

        # Set text
        self.ids.loading_text.text = ""

        # Save
        children = self.ids.my_list.children[:]
        app.original_order = children
        self.save_user_data()

        # Activate MyMenu config
        self.mymenu_config()

    def create_new_item(self, *args):
        # Save old
        children = self.ids.my_list.children[:]
        app.original_order = children
        # Clear old
        self.ids.my_list.clear_widgets()

        # Add new
        item = ListItem(
            title="",
            id=str(secrets.token_hex(15))
        )
        item.ids.name_text_input.bind(text=self.save_list)
        item.ids.checkbox_icon.bind(active=self.update_check)
        self.ids.my_list.add_widget(item)

        # Add old
        for child in reversed(children):
            self.ids.my_list.add_widget(child)

        # Save old
        children = self.ids.my_list.children[:]
        app.original_order = children

    # ------------------------------------------------------------------------------------------------------------------
    def search_for_item(self, instance, value):
        # Clear old
        self.ids.my_list.clear_widgets()

        # Search for the list_item that has value in its title property
        for child in reversed(app.original_order):
            # If found, add to the screen
            if value in child.title:
                self.ids.my_list.add_widget(child)

    # ------------------------------------------------------------------------------------------------------------------
    def save_list(self, instance, value):
        # Save the ListItem in a variable
        item = instance.parent.parent
        # Save the current value typed in the TextInput in a variable
        current_title = value
        # List of titles in app.original_order
        item_titles = [i["Title"] for i in app.user_data["app_info"]]

        # Search for the list_item
        for child in app.original_order:
            # If found, change the old title for the current_title
            if child == item:
                item.title = current_title
                
        # Update database
        self.save_user_data()

    # ------------------------------------------------------------------------------------------------------------------
    def update_check(self, instance, value):
        # Save the ListItem in a variable
        item = instance.parent.parent

        # Update list
        for i, child in enumerate(app.user_data["app_info"]):
            if child["Title"] == item.title:
                app.user_data["app_info"][i]["Checked"] = value

        # Update database
        self.save_user_data()


########################################################################################################################
###################################################   WIDGETS   ########################################################
########################################################################################################################
class ListItem(OneLineAvatarIconListItem):
    """
    List Item that contains an area information
    """
    title = StringProperty()
    i = 1
    anim = False

    # Remove the current ListItem
    def delete_item(self):
        """
        If double click, it will delete the List Item
        If one click, it will open the Snackbar
        """
        if self.i == 2:
            parent_container = self.parent
            if parent_container:
                # Remove widget
                parent_container.remove_widget(self)

                # Remove widget's from user_data
                for i, child in enumerate(app.user_data["app_info"]):
                    if child["Id"] == self.id:
                        app.user_data["app_info"].pop(i)

                # Find index of this widget in app.original_order list
                index = app.original_order.index(self)
                # Remove this widget from list
                app.original_order.pop(index)
                # Save old
                app.sm.get_screen("ToDoListScreen").save_user_data()

        self.i += 1
        Clock.schedule_once(self.verify_double_click, 0.5)

    # ------------------------------------------------------------------------------------------------------------------    
    def verify_double_click(self, *args):
        """
        Verify if the user clicked two times in the trash icon
        """
        if self.i == 2:
            self.i = 1
            self.open_snackbar()

    # ------------------------------------------------------------------------------------------------------------------
    def open_snackbar(self):
        """
        Snackbar used when user presses the trash item one time
        """
        Snackbar(
            text=f"[font={app.font_thin}][color=#000000]Double click to remove item[/font][/color]",
            bg_color=app.sky_blue,
            duration=1,
            snackbar_x="10dp",
            snackbar_y="65dp",
            size_hint_x=(Window.width - (dp(10) * 2)) / Window.width
        ).open()


########################################################################################################################
###################################################   MAIN APP   #######################################################
########################################################################################################################
class MyApp(MDApp):
    screens = {"ToDoListScreen": ToDoListScreen}
    original_order = []
    current_title = ""
    user_data = {}
    font_bold = "Poppins/Poppins-Bold.ttf"
    font_thin = "Poppins/Poppins-SemiBold.ttf"
    sky_blue = "#7eb4e3"
    light_sky_blue = "#a2c1dd"
    black = "#000000"
    half_black = "#00000080"
    transparent = "#00000000"

    # ------------------------------------------------------------------------------------------------------------------    
    def set_current_screen(self, screen_name: str, switch: bool = True):
        """
        Load screen_name.kv file if necessary, and change current screen to screen_name
        """
        # Load
        self.load_screen(screen_name)
        # Change
        if switch:
            self.sm.transition = FadeTransition(duration=0.2)
            self.sm.current = screen_name

    def load_screen(self, screen_name: str):
        """
        Load screen_name.kv file
        """
        if not self.sm.has_screen(screen_name):
            Builder.load_file(f"{screen_name}.kv")
            self.sm.add_widget(self.screens[screen_name]())

    # ------------------------------------------------------------------------------------------------------------------
    def change_statusbar_color_to(self):
        """
        Change the color of Status Bar of the Android
        """
        # Verify platform
        if platform == "android":
            # Changing colors
            from kvdroid.tools import change_statusbar_color
            change_statusbar_color(self.sky_blue, "black")

    def change_navbar_color_to(self):
        """
        Change the color of Navigation Bar of the Android
        """
        # Verify platform
        if platform == "android":
            # Changing colors
            from kvdroid.tools import navbar_color
            navbar_color(self.light_sky_blue)
            
    # ------------------------------------------------------------------------------------------------------------------    
    def create_db_file_if_not_exists(self, *args):
        """
        Create SQLite3 database if there's not already one created
        """
        conection = sqlite3.connect("app2.db")
        cursor = conection.cursor()
        with conection:  # closes conection automatically
            cursor.execute("CREATE TABLE IF NOT EXISTS app(app_information TEXT)")
        self.get_from_db_file()

    def get_from_db_file(self):
        """
        Get data from SQLite3 database
        """
        # Create connection and cursor
        conection = sqlite3.connect("app2.db")
        cursor = conection.cursor()
        # Open connection
        with conection:  # closes conection automatically
            cursor.execute(f"SELECT * FROM app")
            info = cursor.fetchall()
            try:
                self.user_data = {
                    "app_info": literal_eval(info[0][0])["app_info"],
                    "name_of_todo": literal_eval(info[0][0])["name_of_todo"]
                }
            except:
                self.user_data = {
                    "app_info": [],
                    "name_of_todo": ""
                }
        self.set_current_screen("ToDoListScreen")
        self.sm.get_screen("ToDoListScreen").ids.title.text = self.user_data["name_of_todo"]

    def update_db_file(self):
        """
        Create/Update SQLite3 database with MyApp.user_data["app_info"] data
        """
        # Create connection and cursor
        conection = sqlite3.connect("app2.db")
        cursor = conection.cursor()
        # Open connection
        with conection:
            # Get everything from the app2.db
            cursor.execute(f"SELECT * FROM app")
            info = cursor.fetchall()
            # If there's nothing in app2.db
            if not info:
                # If the user has data
                if self.user_data:
                    # Create
                    print("Create")
                    cursor.execute("""INSERT INTO app VALUES (:app_information)""", {
                        "app_information": str(self.user_data)
                    })
            else:
                # Update
                print("Update")
                cursor.execute(f"""
                    UPDATE app SET app_information=:app_information""", {
                    "app_information": str(self.user_data)
                })

    # ------------------------------------------------------------------------------------------------------------------    
    def on_start(self):
        """
        What the App will do when it starts
        """
        Clock.schedule_once(self.create_db_file_if_not_exists)
        # self.change_statusbar_color_to()
        # self.change_navbar_color_to()

    def on_stop(self):
        """
        What the App will do when it ends
        """
        print("App ended")
        self.update_db_file()

    def on_pause(self):
        """
        What the App will do when it pauses
        """
        print("App paused")
        self.update_db_file()
        return True

    def on_resume(self):
        """
        What the App will do when it comes back from pause
        """
        # Here you can check if any data needs replacing (usually nothing)
        pass

    # ------------------------------------------------------------------------------------------------------------------    
    def __init__(self, **kwargs):
        """
        What the App will do when it is built
        """
        super().__init__(**kwargs)
        # Initialize the Screen Manager
        self.sm = MDScreenManager()

    def build(self):
        return self.sm


########################################################################################################################
if __name__ == "__main__":
    app = MyApp()
    app.run()