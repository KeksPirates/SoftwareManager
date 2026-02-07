from PySide6.QtWidgets import QWidget, QVBoxLayout


def create_tab(title, searchbar, software_list, tabs, dlbutton, layout2): 
    tab = QWidget() 
    layout = QVBoxLayout() 
    if searchbar:
        layout.addWidget(searchbar)
    if layout2:
        layout.addLayout(layout2)
    else:
        layout.addWidget(software_list)
    if dlbutton:
        layout.addWidget(dlbutton)
    tab.setLayout(layout)
    tabs.addTab(tab, title) 
    return tab

#################
# SETTINGS TABS #
#################
def general_tab(title, autoresume, update_checkbox, transparent_window, tabs):
    tab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(autoresume)
    layout.addWidget(update_checkbox)
    layout.addWidget(transparent_window)
    layout.addStretch()
    tab.setLayout(layout)
    tabs.addTab(tab, title)
    return tab

def paths_tab(title, download_path, image_path, tabs):
    tab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(download_path)
    layout.addWidget(image_path)
    layout.addStretch()
    tab.setLayout(layout)
    tabs.addTab(tab, title)
    return tab
    

def network_tab(title, network_interface, max_connections, max_downloads, up_speed_limit, down_speed_limit, api_url, tabs):
    tab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(network_interface)
    layout.addWidget(max_connections)
    layout.addWidget(max_downloads)
    layout.addWidget(up_speed_limit)
    layout.addWidget(down_speed_limit)
    layout.addWidget(api_url)
    layout.addStretch()
    tab.setLayout(layout)
    tabs.addTab(tab, title)
    return tab
