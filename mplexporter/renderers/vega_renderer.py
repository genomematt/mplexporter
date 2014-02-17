import warnings
import json
import random
from .base import Renderer
from ..exporter import Exporter


class VegaRenderer(Renderer):
    def open_figure(self, fig, properties):
        self.properties = properties
        self.figwidth = int(properties['figwidth'] * properties['dpi'])
        self.figheight = int(properties['figheight'] * properties['dpi'])
        self.data = []
        self.scales = []
        self.axes = []
        self.marks = []
            
    def open_axes(self, ax, properties):
        if len(self.axes) > 0:
            warnings.warn("multiple axes not yet supported")
        self.axes = [dict(type="x", scale="x", ticks=10),
                     dict(type="y", scale="y", ticks=10)]
        self.scales = [dict(name="x",
                            domain=properties['xlim'],
                            type="linear",
                            range="width",
                            title=properties['xlabel']
                        ),
                       dict(name="y",
                            domain=properties['ylim'],
                            type="linear",
                            range="height",
                            title=properties['ylabel']
                        ),]

    def draw_line(self, data, coordinates, style):
        if coordinates != 'data':
            warnings.warn("Only data coordinates supported. Skipping this")
        dataname = "table{0:03d}".format(len(self.data) + 1)

        # TODO: respect the other style settings
        self.data.append({'name': dataname,
                          'values': [dict(x=d[0], y=d[1]) for d in data]})
        self.marks.append({'type': 'line',
                           'from': {'data': dataname},
                           'properties': {
                               "enter": {
                                   "interpolate": {"value": "monotone"},
                                   "x": {"scale": "x", "field": "data.x"},
                                   "y": {"scale": "y", "field": "data.y"},
                                   "stroke": {"value": style['color']},
                                   "strokeOpacity": {"value": style['alpha']},
                                   "strokeWidth": {"value": style['width']},
                               }
                           }
                       })

    def draw_markers(self, data, coordinates, style):
        if coordinates != 'data':
            warnings.warn("Only data coordinates supported. Skipping this")
        dataname = "table{0:03d}".format(len(self.data) + 1)

        # TODO: respect the other style settings
        self.data.append({'name': dataname,
                          'values': [dict(x=d[0], y=d[1]) for d in data]})
        self.marks.append({'type': 'symbol',
                           'from': {'data': dataname},
                           'properties': {
                               "enter": {
                                   "interpolate": {"value": "monotone"},
                                   "x": {"scale": "x", "field": "data.x"},
                                   "y": {"scale": "y", "field": "data.y"},
                                   "fill": {"value": style['facecolor']},
                                   "fillOpacity": {"value": style['alpha']},
                                   "stroke": {"value": style['edgecolor']},
                                   "strokeOpacity": {"value": style['alpha']},
                                   "strokeWidth": {"value": style['edgewidth']},
                               }
                           }
                       })

    def to_dict(self):
        return dict(self)

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, **kwargs)

    def __iter__(self):
        yield "width", self.figwidth
        yield "height", self.figheight,
        yield "data", self.data,
        yield "scales", self.scales
        yield "axes", self.axes
        yield "marks", self.marks

    def _repr_html_(self):
        """Build the HTML representation for IPython."""
        id = random.randint(0, 2 ** 16)
        html = '<div id="vis%d"></div>' % id
        html += '<script>\n'
        html += VEGA_TEMPLATE % (self.to_json(), id)
        html += '</script>\n'
        return html


def fig_to_vega(fig):
    """Convert a matplotlib figure to vega dictionary"""
    renderer = VegaRenderer()
    Exporter(renderer).run(fig)
    return renderer


VEGA_TEMPLATE = """
( function() {
  var _do_plot = function() {
    if ( (typeof vg == 'undefined') && (typeof IPython != 'undefined')) {
      $([IPython.events]).on("vega_loaded.vincent", _do_plot);
      return;
    }
    vg.parse.spec(%s, function(chart) {
      chart({el: "#vis%d"}).update();
    });
  };
  _do_plot();
})();
"""
