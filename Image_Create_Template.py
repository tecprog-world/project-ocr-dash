import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from skimage import data
import json
from PIL import Image, ImageEnhance, ImageFilter
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
import pytesseract
from io import StringIO
import cv2
from pytesseract import Output as Output1
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

fileName="C:\\Users\\JIMMY\Desktop\\Programming\\Invoices\\Fort_Bend_Invoices\\PDF_and_JPG\\ADMIN1.jpg"

img = cv2.imread(fileName)

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\JIMMY\Desktop\Programming\Python_Libraries\Tesseract-OCR\tesseract'
#img = data.chelsea()
columns = ['type','left','top', 'width', 'height', 'scaleX', 'strokeWidth']

d = pytesseract.image_to_data(img, output_type=Output1.DICT)
dfCoord=pd.DataFrame.from_dict(d)
print(dfCoord)
dfCoord = dfCoord[(dfCoord['text'] == "77487-5029")]
dfCoord=dfCoord.iloc[0]
print(dfCoord)
yCoor = dfCoord['top']
xCoor = dfCoord['left']
print (xCoor, yCoor)

fig = Image.open(fileName)
fig = px.imshow(fig)
shapes=pd.read_csv("C:\\Users\\JIMMY\\Desktop\\Programming\\RMS\\Sheets\\shapeSugarLand1.csv")
row_1=shapes.iloc[0]
print(row_1)
yCoor = yCoor-row_1['y0']
xCoor = xCoor-row_1['x0']
print (xCoor, yCoor)
for index, row in shapes.iterrows():
    fig.add_shape(
        type='rect', xref='x', yref='y',
        x0=row['x0']+xCoor, x1=row['x1']+xCoor, y0=row['y0']+yCoor, y1=row['y1']+yCoor, line=dict(color="red", width=1)
    )

fig.update_layout(dragmode="drawrect",
                  #newshape=dict(fillcolor="cyan", opacity=0.3, line=dict(color="red", width=1)),)
                  newshape=dict(line=dict(color="red", width=1)),)
fig.update_layout( margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
config = {
    "modeBarButtonsToAdd": [
        #"drawline",
        #"drawopenpath",
        #"drawclosedpath",
        #"drawcircle",
        "drawrect",
        "eraseshape",
    ]
}

# Build App
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H4("Draw a shape, then modify it"),
        dcc.Graph(id="fig-image", figure=fig, config=config,style={'width': '150vh', 'height': '150vh',"border":"1px black solid"}),
        dcc.Markdown("Characteristics of shapes"),
        html.Pre(id="annotations-pre"),
        #dash_table.DataTable(id='canvaas-table',
        #                     style_cell={'textAlign': 'left'},
        #                     columns=[{"name": i, "id": i} for i in columns]),
    ]
)

@app.callback(
    Output('annotations-pre', 'children'),
    #Output('canvaas-table', 'data'),
    Input("fig-image", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(string):
    #for key in relayout_data:
    if "shapes" in string:
            print (string)
            data=string['shapes']
            print (data)
            data = pd.DataFrame.from_dict(data)
            print(data)

            data2 = pd.DataFrame()
            ReadingSection = pd.DataFrame()
            for index, row in data.iterrows():
                y1 = int(row['y0'])
                y2 = int(row['y1'])
                x1 = int(row['x0'])
                x2 = int(row['x1'])
                ReadingSection = img[y1:y2, x1:x2]
                text = pytesseract.image_to_string(ReadingSection, config='--psm 6')
                dfReadingSection = pd.DataFrame(StringIO(text))
                # dfReadingSection = dfReadingSection[0].str.split(" ", expand=True)
                data2 = data2.append(dfReadingSection)
                print(data2)
            data2 = data2.to_dict(orient='records')
            return json.dumps(data2, indent=2)
    return dash.no_update

if __name__ == "__main__":
    app.run_server(debug=True)