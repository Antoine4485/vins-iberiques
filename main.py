import tkinter as tk
from functools import partial
from pathlib import Path

import tkintermapview as tkm
from PIL import Image, ImageTk
from tkintermapview import osm_to_decimal
from tkintermapview.canvas_position_marker import CanvasPositionMarker


class Application(tk.Tk):

    def __init__(self, title, infos_by_cities, center, zoom_start):
        tk.Tk.__init__(self)
        self.title(title)
        marker: None | CanvasPositionMarker = None
        self.infos_by_cities = {city: {"latitude": infos[0][0],
                                       "longitude": infos[0][1],
                                       "wine_type": infos[1],
                                       "button": Button(self, city=city,
                                                        command=partial(self.create_or_delete_marker, city)),
                                       "marker": marker} for city, infos in infos_by_cities.items()}
        self.map_widget = Map()
        self.map_widget.set_position(center[0], center[1])
        self.map_widget.set_zoom(zoom_start)
        self.show_widgets()

    def show_widgets(self):
        for i, infos in enumerate(self.infos_by_cities.values()):
            infos["button"].grid(row=i, column=0, padx=10, pady=5, sticky="nswe")
        self.map_widget.grid(row=0, column=1, rowspan=len(self.infos_by_cities))

    def create_or_delete_marker(self, city):
        if self.infos_by_cities[city]["marker"] is None:
            image = Image.open(f"{Path("images") / self.infos_by_cities[city]["wine_type"]}.webp").resize((30, 30))
            marker = self.map_widget.set_marker(
                self.infos_by_cities[city]["latitude"],
                self.infos_by_cities[city]["longitude"],
                icon=ImageTk.PhotoImage(image)
            )
            self.infos_by_cities[city]["marker"] = marker
            self.infos_by_cities[city]["button"].activate()
            # si la ville est en-dehors de la carte on centre dessus
            if not self.map_widget.coordinates_inside(self.infos_by_cities[city]["latitude"],
                                                      self.infos_by_cities[city]["longitude"]):
                self.map_widget.set_position(self.infos_by_cities[city]["latitude"],
                                             self.infos_by_cities[city]["longitude"])
        else:
            self.infos_by_cities[city]["marker"].delete()
            self.infos_by_cities[city]["marker"] = None
            self.infos_by_cities[city]["button"].deactivate()


class Map(tkm.TkinterMapView):

    def __init__(self):
        tkm.TkinterMapView.__init__(self, width=800, height=600)

    def get_border_coordinates(self):
        upper_left_tile_pos = osm_to_decimal(self.upper_left_tile_pos[0], self.upper_left_tile_pos[1], round(self.zoom))
        lower_right_tile_pos = osm_to_decimal(self.lower_right_tile_pos[0], self.lower_right_tile_pos[1],
                                              round(self.zoom))

        return {"longitude_left": upper_left_tile_pos[1], "latitude_top": upper_left_tile_pos[0],
                "longitude_right": lower_right_tile_pos[1], "latitude_bottom": lower_right_tile_pos[0]}

    def coordinates_inside(self, latitude, longitude):
        border_coordinates = self.get_border_coordinates()

        if (longitude < border_coordinates["longitude_left"] or
                longitude > border_coordinates["longitude_right"] or
                latitude < border_coordinates["latitude_bottom"] or
                latitude > border_coordinates["latitude_top"]):
            return False

        return True


class Button(tk.Button):

    def __init__(self, application, city, command):
        tk.Button.__init__(self, application, text=city, command=command)
        self.deactivate()

    def activate(self):
        self.config(bg="#B0C4DE")

    def deactivate(self):
        self.config(bg="#B0E0E6")


if __name__ == '__main__':

    MADRID_COORDINATES = (39.8960, -2.4876)
    DO_VINOS = {"Alicante": ((38.3436365, -0.4881708), "Tinto"), "Calatayud": ((41.3527628, -1.6422977), "Tinto"),
                "Cariñena": ((41.3382122, -1.2263149), "Tinto"),
                "Condado de Huelva": ((37.3382055, -6.5384658), "Blanco"),
                "Jumilla": ((38.4735408, -1.3285417), "Tinto"), "La Gomera": ((28.116, -17.248), "Blanco"),
                "Málaga": ((36.7213028, -4.4216366), "Blanco"),
                "Rías Baixas": ((42.459627886165265, -8.722862824636783), "Blanco"),
                "Ribera del Duero": ((41.49232, -3.005), "Tinto"),
                "Rioja": ((42.29993373411561, -2.486288477690506), "Tinto"),
                "Rueda": ((41.4129785, -4.9597533), "Blanco"), "Somontano": ((42.0883878, 0.0994041), "Tinto"),
                "Tarragona": ((41.1172364, 1.2546057), "Tinto"),
                "Txakoli de Getaria": ((43.29428414467608, -2.202397625912913), "Blanco"),
                "Xérès": ((36.6816936, -6.1377402), "Blanco")}

    app = Application(title="Vinos Ibericos", infos_by_cities=DO_VINOS, center=MADRID_COORDINATES, zoom_start=6)
    app.mainloop()