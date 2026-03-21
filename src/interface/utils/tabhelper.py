from PySide6.QtWidgets import QWidget, QVBoxLayout, QLayout

# Tab creation helper function
def create_tab(title, items, tabs, stretch):
    tab = QWidget()
    layout = QVBoxLayout()

    for item in items:
        if item is None:
            continue

        if isinstance(item, QLayout):
            wrapper = QWidget()
            wrapper.setLayout(item)
            layout.addWidget(wrapper)
        else:
            layout.addWidget(item)

    if stretch:
        layout.addStretch()

    tab.setLayout(layout)
    tabs.addTab(tab, title)
    return tab
