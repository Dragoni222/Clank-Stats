from copy import copy

from PyQt6.QtWidgets import QWidget, QListWidget, QCheckBox

from data.card_data import CARD_STATS, find_card, COLOR_PALETTE
from gui.CardButton import CardButton
from gui.Histogram import histogram_canvas
from logic.card_loader import card_name_to_filename, Card
import os
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QGridLayout, QVBoxLayout,
    QScrollArea, QLabel, QFrame, QHBoxLayout, QLineEdit
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, QEvent

from logic.simulation import Deck, HandValue, flatten_handvalues


class CardGridViewer(QWidget):
    def __init__(self, image_dir):
        self.default_selected_names = [
            "Scramble", "Sidestep", "Stumble", "Stumble",
            "Burgle", "Burgle", "Burgle", "Burgle", "Burgle", "Burgle"
        ]
        super().__init__()
        self.saved_decks = {}  # name -> list[Card]
        self.setWindowTitle("Clank Companion")
        self.setMinimumSize(900, 700)
        CARD_STATS.sort(key=lambda x: x.cost if x.name not in ["Explore", "Mercenary", "Secret Tome"] else -1)
        self.cards = CARD_STATS
        self.image_dir = image_dir
        self.current_deck = Deck([], [], [], [])  # starts empty or default
        self.last_deck = self.current_deck
        # Widgets and Layouts
        self.all_cards_layout = QGridLayout()
        self.draw_cards_layout = QGridLayout()
        self.hand_cards_layout = QGridLayout()
        self.discard_cards_layout = QGridLayout()

        self.deck_histogram = None
        self.hand_histogram = None

        self.setup_ui()
        self.installEventFilter(self)

    def setup_ui(self):
        # Main horizontal split: left and right
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- LEFT PANEL (original UI) ---
        left_panel = QVBoxLayout()

        # All cards scroll area
        all_cards_scroll = QScrollArea()
        all_cards_scroll.setWidgetResizable(True)
        all_cards_container = QWidget()
        all_cards_container.setLayout(self.all_cards_layout)
        all_cards_scroll.setWidget(all_cards_container)

        left_panel.addWidget(QLabel("All Cards:"))
        left_panel.addWidget(all_cards_scroll, stretch=2)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        left_panel.addWidget(separator)

        # Selected cards scroll area
        selected_cards_scroll = QScrollArea()
        selected_cards_scroll.setWidgetResizable(True)
        selected_cards_container = QWidget()
        selected_cards_container.setLayout(self.draw_cards_layout)
        selected_cards_scroll.setWidget(selected_cards_container)

        left_panel.addWidget(QLabel("Draw:"))
        left_panel.addWidget(selected_cards_scroll, stretch=2)

        # Separator 2
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        left_panel.addWidget(separator)

        # Selected cards scroll area
        selected_cards_scroll = QScrollArea()
        selected_cards_scroll.setWidgetResizable(True)
        selected_cards_container = QWidget()
        selected_cards_container.setLayout(self.hand_cards_layout)
        selected_cards_scroll.setWidget(selected_cards_container)

        left_panel.addWidget(QLabel("Hand Cards:"))
        left_panel.addWidget(selected_cards_scroll, stretch=1)

        # Separator 3
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        left_panel.addWidget(separator)

        # Selected cards scroll area
        selected_cards_scroll = QScrollArea()
        selected_cards_scroll.setWidgetResizable(True)
        selected_cards_container = QWidget()
        selected_cards_container.setLayout(self.discard_cards_layout)
        selected_cards_scroll.setWidget(selected_cards_container)

        left_panel.addWidget(QLabel("Discard Cards:"))
        left_panel.addWidget(selected_cards_scroll, stretch=1)

        # Reset button
        reset_button = QPushButton("Reset to Default Cards")
        reset_button.clicked.connect(lambda _: self.reset_to_default())
        shuffle_button = QPushButton("Shuffle Discard")
        shuffle_button.clicked.connect(lambda _: (self.current_deck.shuffle_deck(), self.relayout()))
        discard_button = QPushButton("Discard Hand")
        discard_button.clicked.connect(lambda _: (self.current_deck.discard_hand(), self.relayout()))
        # Style buttons (optional, same as before)
        for button in [reset_button, shuffle_button, discard_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    margin: 5px;
                    padding: 8px 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    background-color: {COLOR_PALETTE[1]};
                    border: 1px solid #888;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PALETTE[2]};
                }}
            """)

        # Put them in a horizontal layout
        button_row = QHBoxLayout()
        button_row.addWidget(reset_button)
        button_row.addWidget(shuffle_button)
        button_row.addWidget(discard_button)

        # Add the button row to the left panel
        left_panel.addLayout(button_row)

        # Wrap left panel in QWidget
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        # --- RIGHT PANEL (example content) ---
        right_panel = QVBoxLayout()
        self.right_panel = right_panel

        self.deck_list = QListWidget()
        self.deck_list.itemClicked.connect(self.load_deck)
        right_panel.addWidget(QLabel("Saved Decks:"))
        right_panel.addWidget(self.deck_list)

        # Save deck UI
        save_layout = QHBoxLayout()
        self.deck_name_input = QLineEdit()
        self.deck_name_input.setPlaceholderText("Deck name...")
        save_button = QPushButton("Save Deck")
        save_button.clicked.connect(self.save_current_deck)
        save_layout.addWidget(self.deck_name_input)
        save_layout.addWidget(save_button)
        right_panel.addLayout(save_layout)

        check_row = QHBoxLayout()

        self.skill_checkbox = QCheckBox("Skill")
        self.skill_checkbox.setChecked(True)
        check_row.addWidget(self.skill_checkbox)
        self.skill_checkbox.stateChanged.connect(lambda _: self.relayout())

        self.boot_checkbox = QCheckBox("Boots")
        self.boot_checkbox.setChecked(True)
        check_row.addWidget(self.boot_checkbox)
        self.boot_checkbox.stateChanged.connect(lambda _: self.relayout())

        self.sword_checkbox = QCheckBox("Swords")
        self.sword_checkbox.setChecked(False)
        check_row.addWidget(self.sword_checkbox)
        self.sword_checkbox.stateChanged.connect(lambda _: self.relayout())

        self.clank_checkbox = QCheckBox("Clank")
        self.clank_checkbox.setChecked(False)
        check_row.addWidget(self.clank_checkbox)
        self.clank_checkbox.stateChanged.connect(lambda _: self.relayout())

        self.tele_checkbox = QCheckBox("Teleports")
        self.tele_checkbox.setChecked(False)
        check_row.addWidget(self.tele_checkbox)
        self.tele_checkbox.stateChanged.connect(lambda _: self.relayout())

        self.gold_checkbox = QCheckBox("Gold")
        self.gold_checkbox.setChecked(False)
        check_row.addWidget(self.gold_checkbox)
        self.gold_checkbox.stateChanged.connect(lambda _: self.relayout())

        right_panel.addLayout(check_row)

        # Deck stats display
        right_panel.addWidget(QLabel("Deck Stats:"))
        self.deck_stats_label = QLabel()
        self.deck_stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.deck_stats_label.setStyleSheet("font-family: monospace;")
        right_panel.addWidget(self.deck_stats_label)

        self.hand_stats_label = QLabel()
        self.hand_stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hand_stats_label.setStyleSheet("font-family: monospace;")
        right_panel.addWidget(self.hand_stats_label)

        # Spacer
        right_panel.addStretch()

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        # Add to main layout (left = 1, right = 1 for 50%/50%)
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(right_widget, stretch=2)

        available_width = int(
            self.all_cards_layout.parentWidget().parentWidget().width()) - 220  # use actual layout width, not full window
        button_width = int(available_width / 6)
        columns = 6

        for idx, card in enumerate(self.cards):
            row = idx // columns
            col = idx % columns
            button = self.create_card_button(card, button_width)
            button.leftClicked.connect(lambda _, c=card: (self.current_deck.add_to_deck(c), self.relayout()))
            self.all_cards_layout.addWidget(button, row, col)

        # Load initial default selection
        self.reset_to_default()
        self.relayout()

    def relayout(self):

        for layout in [self.draw_cards_layout, self.discard_cards_layout,
                       self.hand_cards_layout]:
            # Clear layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            if not self.cards:
                return

            # Get container width safely
            parent_widget = layout.parentWidget().parentWidget()
            if parent_widget is None:
                return

            available_width = int(parent_widget.width()) - 220  # use actual layout width, not full window
            button_width = int(available_width / 6)
            columns = 6

            cards = self.cards
            match layout:
                case self.draw_cards_layout:
                    cards = self.current_deck.draw
                case self.discard_cards_layout:
                    cards = self.current_deck.discard
                case self.hand_cards_layout:
                    cards = self.current_deck.hand

            for idx, card in enumerate(cards):
                row = idx // columns
                col = idx % columns
                button = self.create_card_button(card, button_width)
                button.leftClicked.connect(lambda _, c=card: (self.current_deck.move_card(c), self.relayout()))
                button.rightClicked.connect(
                    lambda _, c=card: (self.current_deck.remove_from_deck(c), self.relayout()))
                layout.addWidget(button, row, col)

        self.display_deck_stats(1000)
        self.save_current_deck()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            self.relayout()
            while self.all_cards_layout.count():
                item = self.all_cards_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            available_width = int(
                self.all_cards_layout.parentWidget().parentWidget().width()) - 220  # use actual layout width, not full window
            button_width = int(available_width / 6)
            columns = 6

            for idx, card in enumerate(self.cards):
                row = idx // columns
                col = idx % columns
                button = self.create_card_button(card, button_width)
                button.leftClicked.connect(lambda _, c=card: (self.current_deck.add_to_deck(c), self.relayout()))
                self.all_cards_layout.addWidget(button, row, col)
        return super().eventFilter(obj, event)

    def reset_to_default(self):
        # Build list of Card objects from default names
        default_cards = []
        for name in self.default_selected_names:
            card = next((c for c in self.cards if c.name == name), None)
            if card:
                new_card = copy(card)
                default_cards.append(new_card)
        self.current_deck = Deck(default_cards, default_cards, [], [])
        self.relayout()

    def save_current_deck(self):
        name = self.deck_name_input.text().strip()
        if not name:
            name = "deck" + str(len(self.deck_list))
        self.saved_decks[name] = copy(self.current_deck)
        # Add to list widget if new
        existing_names = [self.deck_list.item(i).text() for i in range(self.deck_list.count())]
        if name not in existing_names:
            self.deck_list.addItem(name)

    def load_deck(self, item):
        name = item.text()
        if name not in self.saved_decks:
            return
        deck = self.saved_decks[name]
        self.current_deck = copy(deck)
        self.deck_name_input.setText(name)
        self.relayout()

    def display_deck_stats(self, simcount):
        simDeck = self.current_deck.simulate_hands(simcount)
        simNextHand = self.current_deck.simulate_next_hands(simcount)

        self.deck_stats_label.setText(
            "Deck Value Avg: \n" + str(flatten_handvalues(simDeck) / simcount))

        self.hand_stats_label.setText("Next Hand Average: \n" + str(flatten_handvalues(simNextHand) / simcount))
        # Update histogram
        if self.deck_histogram:
            self.right_panel.removeWidget(self.deck_histogram)
            self.deck_histogram.setParent(None)
            self.deck_histogram.deleteLater()
            self.deck_histogram = None

        if self.hand_histogram:
            self.right_panel.removeWidget(self.hand_histogram)
            self.hand_histogram.setParent(None)
            self.hand_histogram.deleteLater()
            self.hand_histogram = None

        deck_histogram_data = self.generate_histogram_data(simDeck)
        hand_histogram_data = self.generate_histogram_data(simNextHand)
        deck_histogram_data_filtered = []
        hand_histogram_data_filtered = []
        histogram_colors = [[], []]
        if self.skill_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[0])
            hand_histogram_data_filtered.append(hand_histogram_data[0])
            histogram_colors[0].append('skyblue')
            histogram_colors[1].append('navy')
        if self.boot_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[1])
            hand_histogram_data_filtered.append(hand_histogram_data[1])
            histogram_colors[0].append('yellow')
            histogram_colors[1].append('darkgoldenrod')
        if self.sword_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[2])
            hand_histogram_data_filtered.append(hand_histogram_data[2])
            histogram_colors[0].append('red')
            histogram_colors[1].append('maroon')
        if self.clank_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[3])
            hand_histogram_data_filtered.append(hand_histogram_data[3])
            histogram_colors[0].append('grey')
            histogram_colors[1].append('black')
        if self.gold_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[4])
            hand_histogram_data_filtered.append(hand_histogram_data[4])
            histogram_colors[0].append('gold')
            histogram_colors[1].append('darkgoldenrod')
        if self.tele_checkbox.isChecked():
            deck_histogram_data_filtered.append(deck_histogram_data[5])
            hand_histogram_data_filtered.append(hand_histogram_data[5])
            histogram_colors[0].append('purple')
            histogram_colors[1].append('indigo')

        if len(deck_histogram_data_filtered) > 0:
            self.deck_histogram = histogram_canvas(deck_histogram_data_filtered, histogram_colors, parent=self)
            self.right_panel.insertWidget(self.right_panel.count() - 2, self.deck_histogram)
            self.hand_histogram = histogram_canvas(hand_histogram_data_filtered, histogram_colors, parent=self)
            self.right_panel.insertWidget(self.right_panel.count() - 1, self.hand_histogram)

    def generate_histogram_data(self, sim):
        skill_values = [hand.skill for hand in sim]
        boot_values = [hand.boots for hand in sim]
        sword_values = [hand.swords for hand in sim]
        clank_values = [hand.clank for hand in sim]
        gold_values = [hand.gold for hand in sim]
        tele_values = [hand.teleports for hand in sim]

        highest_value = max(
            skill_values + boot_values + sword_values + clank_values + gold_values + tele_values + [10]) + 1
        histogram_data = [[0 for _ in range(highest_value)] for _ in range(6)]

        for skill in skill_values:
            for i in range(skill + 1):
                histogram_data[0][i] += 1

        for boot in boot_values:
            for i in range(boot + 1):
                histogram_data[1][i] += 1

        for sword in sword_values:
            for i in range(sword + 1):
                histogram_data[2][i] += 1

        for clank in clank_values:
            for i in range(clank + 1):
                histogram_data[3][i] += 1

        for gold in gold_values:
            for i in range(gold + 1):
                histogram_data[4][i] += 1

        for tele in tele_values:
            for i in range(tele + 1):
                histogram_data[5][i] += 1

        return histogram_data

    def create_card_button(self, card: Card, button_size):
        path = os.path.join(self.image_dir, card.filename)
        if not os.path.exists(path):
            print(f"Missing image for card: {card.name}")
            return None
        icon_size = button_size + 20

        button = CardButton(self)
        button.setIcon(QIcon(path))
        button.setToolTip(card.name)
        button.setIconSize(QSize(icon_size, icon_size))
        button.setFixedSize(icon_size, icon_size)
        button.setStyleSheet("""
            QPushButton {
                background-color: #919191;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        return button
