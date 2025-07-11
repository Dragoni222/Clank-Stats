import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from data.card_data import COLOR_PALETTE


class histogram_canvas(FigureCanvas):
    def __init__(self, values, colors, parent=None, width=4, height=2.5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.set_facecolor(COLOR_PALETTE[3])
        self.axes.set_facecolor(COLOR_PALETTE[5])
        super().__init__(fig)
        self.setParent(parent)
        self.plot(values, colors)
        self.colors = colors

    def plot(self, valuelist, colors):
        self.axes.clear()
        bar_size = 0.8 / len(valuelist)
        if valuelist:
            indices = list(range(1,len(valuelist[0])))

            percentages = [[(v / values[0]) * 100 if sum(values) > 0 else 0 for v in values] for values in valuelist]
            percentages = [i[1:] for i in percentages]
            for j in range(len(valuelist)):
                self.axes.bar([((j+0.5)*bar_size) - 0.4 + i for i in indices], percentages[j], width=bar_size,
                              color=colors[0][j], edgecolor='black')
            self.axes.set_xticks(indices)
            self.axes.set_xticklabels([str(i) for i in indices])
            self.axes.set_ylim(0, 115)

            for j in range(len(valuelist)):
                for i, p in zip([((j+0.5)*bar_size) - 0.4 + i for i in indices], percentages[j]):
                    self.axes.text(i, p + 1, f"{p:0.0f}", ha='center', va='bottom', fontsize=9, color=colors[1][j])

        else:
            self.axes.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=12)

        self.draw()
