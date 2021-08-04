import plotly.express as px
import pandas #Doing this so replit automatically installs the package as required by plotly express

def drawGraph(data):
    day = ['Monday','Tuesday','Wednesday','Thursday','Friday', 'Saturday', 'Sunday',]
    busyness = [len(x) for x in data['hour']]
    mostBusy = max(busyness)
    busyness = [mostBusy-busyness[x]+1 if not data['closed'][x] else 0 for x in range(7)]

    fig = px.bar(x=day,y=busyness)
    fig.update_traces(marker_color='gray', marker_line_width = 1, marker_line_color = 'darkslategray')
    fig.update_layout(title="Busyness by Day", 
      xaxis_title="Day of the Week", yaxis_title="Busyness", bargap=0.05, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(visible=False)
    return fig.to_html(full_html=False, default_height  = 500, default_width=800, config={'staticPlot':True})

  
def formatTime(hours, flags):
  output = []
  for i in range(7):
    if flags[i] == True:
      output.append('Closed')
    else:
      day = []
      for hour in hours[i]:
        if hour >= 12:
          day.append(f"{(hour-12 if hour > 12 else hour)}PM")
        else:
          day.append(f'{(hour if hour > 0 else hour + 12)}AM')
      output.append(', '.join(day))
  return output

          

