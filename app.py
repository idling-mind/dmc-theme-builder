import json
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, _dash_renderer, Input, Output, State, callback, ctx, no_update
from components import progress_card
from components import theme_switch
from components import figures
from components import authentication
from components import sample_components
from components import stepper
from components import date_picker
from utilities.color import generate_colors


_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL)

colors = dmc.DEFAULT_THEME["colors"]
color_picker_value_mapping = {
    color: codes[5] for color, codes in colors.items() if color != "dark"
}
theme_name_mapping = {
    codes[5]: color for color, codes in colors.items() if color != "dark"
}
size_name_mapping = {1: "xs", 2: "sm", 3: "md", 4: "lg", 5: "xl"}
color_picker_value_mapping_reverse = {
    v: k for k, v in color_picker_value_mapping.items()
}

def color_swatches(colors):
    """Create a list of color swatches for the color picker."""
    return [dmc.Paper(bg=color, p="xs", radius="xs") for color in colors]

color_picker = dmc.Stack(
    [
        dmc.Text("Color", size="xs"),
        dmc.ColorPicker(
            id="color-picker",
            size="sm",
            swatches=list(color_picker_value_mapping.values()),
            swatchesPerRow=7,
            value=color_picker_value_mapping["green"],
            fullWidth=True,
        ),
        dmc.TextInput(id="color-picker-textinput", value="green", debounce=True),
        dmc.Group(
            color_swatches(list(color_picker_value_mapping.values())),
            gap=2,
            grow=True,
            id="shade-swatches",
        ),
    ],
    gap="sm",
)


def make_slider(title, id):
    return dmc.Stack(
        [
            dmc.Text(title, size="sm"),
            dmc.Slider(
                min=1,
                max=5,
                value=2,
                id=id,
                updatemode="drag",
                styles={"markLabel": {"display": "none"}},
                marks=[
                    {"value": 1, "label": "xs"},
                    {"value": 2, "label": "sm"},
                    {"value": 3, "label": "md"},
                    {"value": 4, "label": "lg"},
                    {"value": 5, "label": "xl"},
                ],
            ),
        ],
        mt="md",
    )


customize_theme = dmc.Box(
    [
        dmc.Button("Customize Theme", id="modal-demo-button"),
        dmc.Modal(
            id="modal-customize",
            size="sm",
            children=[
                dmc.Box(
                    [
                        color_picker,
                        make_slider("Radius", "radius"),
                        make_slider("Shadow", "shadow"),
                        dmc.Group(
                            [
                                theme_switch.theme_toggle,
                                dmc.Text("light/dark color scheme", size="sm", pt="sm"),
                            ]
                        ),
                    ],
                    bd="1px solid gray.3",
                    p="sm",
                )
            ],
            zIndex=1000,
            withCloseButton=False,
            yOffset="0vh",
            styles={"overlay": {"background": "rgba(0, 0, 0, 0.3)"}},
        ),
    ]
)


see_code = dmc.Box(
    [
        dmc.Button("copy theme code", id="modal-code-button", variant="outline"),
        dmc.Modal(
            [
                dmc.CodeHighlight(
                    id="json",
                    code="",
                    language="json",
                    h=300,
                    style={"overflow": "auto"},
                ),
                dmc.Text("dmc.MantineProvider(theme=theme)"),
            ],
            zIndex=1000,
            withCloseButton=False,
            yOffset="0vh",
            id="modal-code",
        ),
    ]
)

github_link = dmc.Anchor(
    dmc.ActionIcon(
        DashIconify(icon="radix-icons:github-logo", width=25),
        variant="transparent",
        size="lg",
    ),
    href="https://github.com/AnnMarieW/dmc-theme-builder",
    target="_blank",
    visibleFrom="xs",
)


sample_app = dmc.Box(
    [
        dmc.Group(
            [
                sample_components.card,
                progress_card.card,
                figures.card,
                date_picker.card,
                authentication.card,
                stepper.card,
            ],
            gap="lg",
            justify="center",
        ),
    ]
)

layout = dmc.Container(
    [
        dmc.Group(
            [
                dmc.Title("Dash Mantine Components Theme Builder", order=1, mt="lg"),
                github_link,
            ],
            justify="space-between",
        ),
        dmc.Title(
            "Set default color, radius, shadow, and color scheme", order=3, mb="lg"
        ),
        dmc.Group([customize_theme, see_code]),
        dmc.Divider(size="md", mt="lg"),
        dmc.Space(h=60),
        sample_app,
    ],
    #   fluid=True,
    mb="lg",
)

app.layout = dmc.MantineProvider(
    layout,
    theme={
        "primaryColor": "green",
        "defaultRadius": "sm",
        "components": {"Card": {"defaultProps": {"shadow": "sm"}}},
    },
    forceColorScheme="light",
    id="mantine-provider",
)


@callback(
    Output("mantine-provider", "theme"),
    Output("json", "code"),
    Output("color-picker-textinput", "value"),
    Output("color-picker", "value"),
    Output("shade-swatches", "children"),
    Input("color-picker", "value"),
    Input("color-picker-textinput", "value"),
    Input("radius", "value"),
    Input("shadow", "value"),
    State("mantine-provider", "theme"),
)
def update(color, color_text, radius, shadow, theme):
    if ctx.triggered_id == "color-picker-textinput":
        color = color_picker_value_mapping.get(color_text, color_text)
    if color in theme_name_mapping:
        theme["primaryColor"] = theme_name_mapping[color]
        theme.pop("colors", None)
        color_shades = dmc.DEFAULT_THEME["colors"][theme["primaryColor"]]
    else:
        try:
            base_color_index, color_shades = generate_colors(color)
        except ValueError:
            return [no_update] * 4
        theme["colors"] = {"myColor": color_shades}
        theme["primaryColor"] = "myColor"
    theme["defaultRadius"] = size_name_mapping[radius]
    theme["components"]["Card"]["defaultProps"]["shadow"] = size_name_mapping[shadow]
    return (
        theme,
        "theme=" + json.dumps(theme, indent=4),
        color_picker_value_mapping_reverse.get(color, color),
        color,
        color_swatches(color_shades),
    )


@callback(
    Output("modal-customize", "opened"),
    Input("modal-demo-button", "n_clicks"),
    State("modal-customize", "opened"),
    prevent_initial_call=True,
)
def modal_demo(n, opened):
    return not opened


@callback(
    Output("modal-code", "opened"),
    Input("modal-code-button", "n_clicks"),
    State("modal-code", "opened"),
    prevent_initial_call=True,
)
def modal_code(n, opened):
    return not opened


if __name__ == "__main__":
    app.run(debug=True)
