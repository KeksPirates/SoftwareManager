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
