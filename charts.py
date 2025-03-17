from datetime import datetime
import urllib.parse
import json
import pandas as pd

class Chart:

    @staticmethod
    def get_bar_chart_url(chart_config):
        if not chart_config:
            return 
        base_url = "https://quickchart.io/chart"
        json_config = json.dumps(chart_config)
        return f"{base_url}?c={urllib.parse.quote(str(json_config))}"
    
    @staticmethod
    def create_chart_config(data, locations, gpus, brand=None):
        '''
        Creates charts for the following commands: !chart, !achart, !nchart
        '''
        if not data:
            return

        start = datetime.strptime(data[0][2], "%Y-%m-%d")
        end = datetime.strptime(data[-1][2], "%Y-%m-%d")
        labels = Chart.__generate_time_labels(start, end, interval="D")
        
        datasets = Chart.__generate_datasets(gpus, data, labels)            
        datasets = list(datasets.values())

        def format_title(t, locs):
            for l in locs:
                t += f"{l}, "
            t = t.strip().strip(",")
            t += " stores" if len(locs) > 1 else " store"
            return t

        title = f"{brand} " if brand else ""
        title += "Stock data for "
        if locations:
            title = format_title(title, locations)
        
        else:
            title += 'all stores'

        stepsize = Chart.__get_step_size(datasets)

        chart_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "title": {"display": True, "text": title, 'fontColor': 'white'},
            "legend": {"labels": {"fontColor": 'white'}},
            "scales": {
                "xAxes": [{
                    "stacked": True,
                    "scaleLabel": {"display": True, "labelString": 'Date', 'fontColor': 'white'},
                    "gridLines": {"display": False},
                    "grid": {"display": False},
                    "ticks": {'fontColor': 'white', 'font': { 'size': 12 }}}],
                "yAxes": [{
                    "stacked": True,
                    "scaleLabel": {"display": True, "labelString": 'Quantity', 'fontColor': 'white'},
                    "gridLines": {"color": "white"},
                    "ticks": {'fontColor': 'white', "stepSize": stepsize, "beginAtZero": True,},
                    "grid": {"color": "rgba(200, 200, 200, 0.3)"}
                    }
                ],
            
            },
            "plugins": {
                "datalabels": {
                    "display": True,
                    "color": 'black'
                    }
                }
        }
    }
        return chart_config
    
    @staticmethod
    def create_hour_dist_chart_config(data, location=None):
        '''
        Create charts for the !hour command.
        '''
        if not data:
            return
        new = {}
        for d in data:
            new.setdefault(d[0], d[1])
        
        start = datetime.strptime("0", "%H")
        end = datetime.strptime("23", "%H")
        labels = Chart.__generate_time_labels(start, end, interval="h")
        datasets = Chart.__generate_hour_dist_dataset(new, labels)
        title = f'All-time hourly stock scan for {location} store' if location else 'All-time hourly stock scan for all stores'
        
        chart_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "title": {"display": True, "text": title, 'fontColor': 'white'},
            "legend": {"display": False},
            "scales": {
                "xAxes": [{
                    "stacked": True,
                    "scaleLabel": {"display": True, "labelString": 'Hour', 'fontColor': 'white'},
                    "gridLines": {"display": False},
                    "grid": {"display": False},
                    "ticks": {'fontColor': 'white', 'font': { 'size': 12 }}}],
                "yAxes": [{
                    "stacked": True,
                    "scaleLabel": {"display": True, "labelString": 'Quantity', 'fontColor': 'white'},
                    "gridLines": {"color": "white"},
                    "ticks": {'fontColor': 'white', "stepSize": 2, "beginAtZero": True,},
                    "grid": {"color": "rgba(200, 200, 200, 0.3)"} 
                }]
            }
        }
        }
        return chart_config

    @staticmethod
    def __generate_time_labels(start, end, interval="D"):
        """Generate time labels between start and end at given intervals"""
        time_range = pd.date_range(start=start, end=end, freq=interval)
        return [t.strftime("%Y-%m-%d") for t in time_range] if interval=="D" else [t.strftime("%H") for t in time_range]

    @staticmethod
    def __generate_datasets(gpus, data, labels):
        '''
        Creates dataset based on what QuickChart accepts
        '''
        colors = [
        "rgb(189, 236, 182)",  # Soft Green
        "rgb(250, 214, 165)",  # Peach
        "rgb(226, 193, 232)",  # Lavender
        "rgb(178, 235, 242)",  # Light Aqua
        "rgb(255, 221, 225)",  # Blush Pink
        "rgb(255, 246, 184)",  # Pale Yellow
        "rgb(192, 216, 255)",  # Soft Blue
        "rgb(224, 242, 241)",  # Mint
        "rgb(245, 222, 179)",  # Light Sand
        "rgb(233, 233, 233)"   # Light Gray
        ]
        datasets = {}
        count_data = {}
        # Create datasets with empty data for each gpu
        for i, gpu in enumerate(gpus):
            datasets.setdefault(gpu, {'label': gpu, 'data': [], "borderColor": 'black', "borderWidth": 1, 'backgroundColor': colors[i]})
            count_data.setdefault(gpu, 0)
        
        i = 0
        # Loop through each date label, populating the data field with the quantity for that date
        for label in labels:
            appended_once = False
            while i in range(len(data)):
                gpu = data[i][0]
                quantity = data[i][1]
                date = data[i][2]

                if date == label:
                    datasets[gpu]['data'].append(quantity)
                    count_data[gpu] += 1
                    appended_once = True
                    i += 1
                    
                elif date != label and not appended_once:
                    # None of the GPUs had stock for this particular day.
                    # Need to add in 0 as quantity for that day if that is the case.
                    for other_gpu in gpus:
                        datasets[other_gpu]['data'].append(0)
                        count_data[other_gpu] += 1
                    break
                    
                elif date != label:
                    # One of the GPUs had stock for this particular day.
                    # Need to append 0 quantity for the other GPUs that did not have stock for this particular day
                    max_count = max(count_data.values())
                    for other_gpu in gpus:
                        if len(datasets[other_gpu]['data']) != max_count:
                            datasets[other_gpu]['data'].append(0)
                            count_data[other_gpu] += 1
                    break

                else:
                    i += 1

        # Loop may have terminated before we could add in 0 quantities for the last day.
        max_count = max(count_data.values())
        for other_gpu in gpus:
            if len(datasets[other_gpu]['data']) != max_count:
                datasets[other_gpu]['data'].append(0)
                count_data[other_gpu] += 1

        return datasets
    
    @staticmethod
    def __generate_hour_dist_dataset(data, labels):
        datasets = {"label": "Quantity", "data": [], "backgroundColor": "rgb(255, 221, 225)"}
        for label in labels:
            if label in data:
                datasets['data'].append(data[label])
                continue
            datasets['data'].append(0)
        return [datasets]

    @staticmethod
    def __get_step_size(dataset):
        aggr_sum = []
        for data in dataset:
            if not aggr_sum:
                aggr_sum = data['data']
            else:
                for i, qty in enumerate(data['data']):
                    aggr_sum[i] += qty
        maximum = max(aggr_sum)
        stepsize = maximum // 15
        stepsize = max(stepsize, 1)
        return stepsize

    

    